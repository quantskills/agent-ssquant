#!/usr/bin/env python3
"""Quick environment check for a local SSQuant checkout or install."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional


MIN_PY = (3, 9)
MAX_PY_EXCLUSIVE = (3, 15)
MIN_SSQUANT_VERSION = (0, 4, 5)

KEY_FILES = [
    "ssquant/api/strategy_api.py",
    "ssquant/backtest/unified_runner.py",
    "ssquant/config/trading_config.py",
    "ssquant/config/config_helpers.py",
    "ssquant/data/data_source.py",
    "ssquant/data/local_adjust.py",
    "examples/B_双均线策略_高性能.py",
]

AI_AGENT_FILES = [
    "ai_agent/start_server.py",
    "ai_agent/requirements.txt",
    "ai_agent/backend.py",
]


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def normalize(path: Path) -> str:
    try:
        return str(path.resolve())
    except OSError:
        return str(path)


def find_project_root(start: Optional[Path]) -> Optional[Path]:
    if start is None:
        start = Path.cwd()
    start = start.resolve()
    candidates = [start] + list(start.parents)
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() and (candidate / "ssquant").is_dir():
            return candidate
    return None


def read_pyproject_version(root: Path) -> Optional[str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        text = pyproject.read_text(encoding="utf-8")
    except Exception:
        return None
    match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else None


def parse_version(version: Optional[str]) -> Optional[tuple[int, ...]]:
    if not version:
        return None
    parts = re.findall(r"\d+", version)
    if not parts:
        return None
    return tuple(int(part) for part in parts[:3])


def version_supported(version: Optional[str]) -> Optional[bool]:
    parsed = parse_version(version)
    if parsed is None:
        return None
    if len(parsed) < len(MIN_SSQUANT_VERSION):
        parsed = parsed + (0,) * (len(MIN_SSQUANT_VERSION) - len(parsed))
    return parsed >= MIN_SSQUANT_VERSION


def check_import(root: Optional[Path]) -> dict[str, Any]:
    if root and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        module = importlib.import_module("ssquant")
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}
    version = getattr(module, "__version__", None)
    location = getattr(module, "__file__", None)
    ctp_available = getattr(module, "CTP_AVAILABLE", None)
    return {
        "ok": True,
        "version": version,
        "location": location,
        "ctp_available": ctp_available,
    }


def build_report(project: Optional[Path]) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    py_ok = MIN_PY <= sys.version_info[:2] < MAX_PY_EXCLUSIVE
    if not py_ok:
        errors.append(
            f"Python {sys.version_info.major}.{sys.version_info.minor} is outside SSQuant supported range >=3.9,<3.15"
        )

    root = find_project_root(project)
    if root is None:
        warnings.append("No local SSQuant project root found from the supplied path.")

    import_info = check_import(root)
    if not import_info["ok"]:
        errors.append(f"Could not import ssquant: {import_info['error']}")
    else:
        import_version = import_info.get("version")
        if version_supported(import_version) is False:
            errors.append(f"Imported ssquant version {import_version} is unsupported; require >=0.4.5")

    missing_files: list[str] = []
    missing_ai_agent_files: list[str] = []
    example_count = 0
    high_perf_count = 0
    data_cache_exists = False
    pyproject_version = None

    if root:
        pyproject_version = read_pyproject_version(root)
        if version_supported(pyproject_version) is False:
            errors.append(f"SSQuant pyproject version {pyproject_version} is unsupported; require >=0.4.5")
        for rel in KEY_FILES:
            if not (root / rel).exists():
                missing_files.append(rel)
        for rel in AI_AGENT_FILES:
            if not (root / rel).exists():
                missing_ai_agent_files.append(rel)
        examples_dir = root / "examples"
        if examples_dir.exists():
            examples = list(examples_dir.glob("*.py"))
            example_count = len(examples)
            high_perf_count = len([p for p in examples if "_高性能" in p.name])
        else:
            missing_files.append("examples/")
        data_cache_exists = (root / "data_cache" / "backtest_data.db").exists()

    if missing_files:
        errors.append("Missing key project files: " + ", ".join(missing_files))
    if root and example_count == 0:
        warnings.append("No example strategies found under examples/.")
    if root and high_perf_count == 0:
        warnings.append("No *_高性能.py examples found; generated strategies may have weaker templates.")
    if root and missing_ai_agent_files:
        warnings.append("AI Agent files missing: " + ", ".join(missing_ai_agent_files))
    if root and not data_cache_exists:
        warnings.append("Local data_cache/backtest_data.db not found; local backtests may need data import.")

    report = {
        "python": {
            "version": sys.version.split()[0],
            "supported": py_ok,
            "required": ">=3.9,<3.15",
        },
        "ssquant": {
            "required": ">=0.4.5",
            "pyproject_supported": version_supported(pyproject_version),
            "import_supported": version_supported(import_info.get("version") if import_info.get("ok") else None),
        },
        "project_root": normalize(root) if root else None,
        "pyproject_version": pyproject_version,
        "import": import_info,
        "examples": {
            "count": example_count,
            "high_performance_count": high_perf_count,
        },
        "data_cache_exists": data_cache_exists,
        "errors": errors,
        "warnings": warnings,
    }
    return report, errors, warnings


def print_human(report: dict[str, Any]) -> None:
    print("SSQuant doctor")
    print(f"- Python: {report['python']['version']} ({'ok' if report['python']['supported'] else 'unsupported'})")
    print(f"- Project root: {report['project_root'] or 'not found'}")
    if report["pyproject_version"]:
        pyproject_ok = report["ssquant"]["pyproject_supported"]
        pyproject_status = "ok" if pyproject_ok is True else "unsupported" if pyproject_ok is False else "unknown"
        print(f"- pyproject version: {report['pyproject_version']} ({pyproject_status}, require >=0.4.5)")
    imp = report["import"]
    if imp["ok"]:
        import_ok = report["ssquant"]["import_supported"]
        import_status = "ok" if import_ok is True else "unsupported" if import_ok is False else "unknown"
        print(f"- import ssquant: ok ({imp.get('version') or 'unknown version'}, {import_status}, require >=0.4.5)")
        print(f"- import location: {imp.get('location')}")
        print(f"- CTP available flag: {imp.get('ctp_available')}")
    else:
        print(f"- import ssquant: failed ({imp['error']})")
    print(
        f"- examples: {report['examples']['count']} total, {report['examples']['high_performance_count']} high-performance"
    )
    print(f"- local data cache: {'found' if report['data_cache_exists'] else 'not found'}")
    for warning in report["warnings"]:
        print(f"[WARN] {warning}")
    for error in report["errors"]:
        print(f"[ERROR] {error}")


def main() -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, help="Path inside a local SSQuant checkout")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human output")
    args = parser.parse_args()

    report, errors, _warnings = build_report(args.project)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
