#!/usr/bin/env python3
"""Static validator for generated SSQuant strategy files."""

from __future__ import annotations

import argparse
import ast
import py_compile
import sys
from pathlib import Path
from typing import Optional


ORDER_METHODS = {"buy", "sell", "sellshort", "buycover", "close_all"}
FORBIDDEN_IMPORT_PARTS = [
    "ssquant.data.data_source",
    "ssquant.backtest.backtest_core",
    "ssquant.pyctp",
    "ssquant.ctp",
]
FORBIDDEN_NAMES = {
    "DataSource",
    "BacktestCore",
    "TraderApi",
    "MdApi",
    "current_raw_price",
    "raw_price",
    "_adjust_factor",
}


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


class StrategyVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: set[str] = set()
        self.imports: set[str] = set()
        self.calls: list[ast.Call] = []
        self.names: set[str] = set()
        self.strategy_rolling_lines: list[int] = []
        self.initialize_register_lines: list[int] = []
        self.non_api_order_lines: list[int] = []
        self.runner_strategy_names: set[str] = set()
        self.run_mode_assignments: list[str] = []
        self.string_literals: list[str] = []
        self.keyword_values: dict[str, list[str]] = {}
        self.current_function: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.add(node.name)
        previous = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = previous

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        self.imports.add(module)
        for alias in node.names:
            self.names.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self.names.add(node.id)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "RUN_MODE":
                if isinstance(node.value, ast.Attribute):
                    self.run_mode_assignments.append(node.value.attr)
                elif isinstance(node.value, ast.Name):
                    self.run_mode_assignments.append(node.value.id)
                elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    self.run_mode_assignments.append(node.value.value)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            self.string_literals.append(node.value)

    def visit_Call(self, node: ast.Call) -> None:
        self.calls.append(node)
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if self.current_function == "strategy" and attr == "rolling":
                self.strategy_rolling_lines.append(node.lineno)
            if self.current_function == "initialize" and attr == "register_indicator":
                self.initialize_register_lines.append(node.lineno)
            if attr in ORDER_METHODS:
                if not isinstance(node.func.value, ast.Name) or node.func.value.id != "api":
                    self.non_api_order_lines.append(node.lineno)
        for keyword in node.keywords:
            if keyword.arg == "strategy" and isinstance(keyword.value, ast.Name):
                self.runner_strategy_names.add(keyword.value.id)
            if keyword.arg and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                self.keyword_values.setdefault(keyword.arg, []).append(keyword.value.value)
        self.generic_visit(node)


def compile_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        errors.append(f"py_compile failed: {exc.msg}")
    return errors


def parse_file(path: Path) -> tuple[Optional[ast.AST], list[str]]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            source = path.read_text(encoding="gbk")
        except UnicodeDecodeError as exc:
            return None, [f"Could not read file as UTF-8 or GBK: {exc}"]
    except OSError as exc:
        return None, [f"Could not read file: {exc}"]
    try:
        return ast.parse(source), []
    except SyntaxError as exc:
        return None, [f"AST parse failed: {exc}"]


def validate(path: Path, allow_no_indicator: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"Strategy file not found: {path}"], warnings
    if not path.is_file():
        return [f"Path is not a file: {path}"], warnings

    errors.extend(compile_file(path))
    tree, parse_errors = parse_file(path)
    errors.extend(parse_errors)
    if tree is None:
        return errors, warnings

    visitor = StrategyVisitor()
    visitor.visit(tree)

    if "initialize" not in visitor.functions:
        errors.append("Missing required function: initialize(api)")
    strategy_function_names = {"strategy"} | visitor.runner_strategy_names
    if not (visitor.functions & strategy_function_names):
        errors.append("Missing strategy function: define strategy(api) or pass a function via runner.run(strategy=...)")

    required_import_names = {"StrategyAPI", "UnifiedStrategyRunner", "RunMode", "get_config"}
    missing_import_names = sorted(required_import_names - visitor.names)
    if missing_import_names:
        warnings.append("Expected SSQuant imports/names not seen: " + ", ".join(missing_import_names))

    if not visitor.initialize_register_lines and not allow_no_indicator:
        errors.append("No api.register_indicator() call found inside initialize(api). Use --allow-no-indicator only for justified dynamic/Tick cases.")

    forbidden_imports = sorted(
        imp for imp in visitor.imports for forbidden in FORBIDDEN_IMPORT_PARTS if imp == forbidden or imp.startswith(forbidden + ".")
    )
    if forbidden_imports:
        errors.append("Forbidden low-level SSQuant imports in strategy: " + ", ".join(forbidden_imports))

    forbidden_names = sorted(visitor.names & FORBIDDEN_NAMES)
    if forbidden_names:
        errors.append("Forbidden framework/internal names used in strategy: " + ", ".join(forbidden_names))

    if visitor.non_api_order_lines:
        errors.append("Order methods must be called on api at lines: " + ", ".join(map(str, visitor.non_api_order_lines)))

    if visitor.strategy_rolling_lines:
        warnings.append("Pandas rolling-like calls inside strategy(api) at lines: " + ", ".join(map(str, visitor.strategy_rolling_lines)))

    symbols = visitor.keyword_values.get("symbol", [])
    suspect_000 = sorted({s for s in symbols if len(s) >= 3 and "000" in s})
    if suspect_000:
        warnings.append("Found string(s) containing 000; SSQuant continuous contracts usually use 888/777, not 000: " + ", ".join(suspect_000[:5]))

    periods = [value.lower() for value in visitor.keyword_values.get("kline_period", [])]
    data_modes = [value.lower() for value in visitor.keyword_values.get("data_source_mode", [])]
    if "tick" in periods and "local" not in data_modes:
        errors.append('Tick backtests must set data_source_mode="local".')

    if any("REAL_TRADING" in value for value in visitor.run_mode_assignments):
        warnings.append("RUN_MODE is assigned to REAL_TRADING; confirm the user explicitly requested live trading.")

    return errors, warnings


def main() -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strategy", type=Path, help="Path to a SSQuant strategy .py file")
    parser.add_argument("--allow-no-indicator", action="store_true", help="Allow strategies without initialize(api) indicator registration")
    args = parser.parse_args()

    errors, warnings = validate(args.strategy, args.allow_no_indicator)
    print(f"SSQuant strategy validation: {args.strategy}")
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")
    if not errors and not warnings:
        print("OK: no issues found")
    elif not errors:
        print("OK with warnings")
    else:
        print("FAILED")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
