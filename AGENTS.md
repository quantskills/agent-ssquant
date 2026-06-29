---
name: agent-ssquant
description: SSQuant Agent workflow for Chinese futures strategies, data_server diagnostics, CTP/SIMNOW runtime checks, and Chinese backtest reporting. Use when an agent needs to locate an SSQuant project, write or repair SSQuant futures strategies, validate StrategyAPI usage, run evidence-backed backtests, diagnose local or remote data behavior, inspect reports, or plan guarded live CTP operations.
quantSkills:
  organization: https://github.com/quantskills
  repository: quantskills/agent-ssquant
  repository_url: https://github.com/quantskills/agent-ssquant
  project_type: agent
  collection: ssquant
  license: GPL-3.0
  category: workflow-agent
  tags: [ssquant, futures, ctp, backtest, data-server, reporting]
  platforms: [claude-code, codex, openclaw, cursor, workbuddy]
  language: zh-en
  status: stable
  validation_level: runnable
  maintainer_type: community
  requires: []
  summary_zh: "\u0053\u0053\u0051\u0075\u0061\u006e\u0074\u0020\u0041\u0067\u0065\u006e\u0074\uff1a\u671f\u8d27\u7b56\u7565\u3001\u6570\u636e\u670d\u52a1\u3001\u0043\u0054\u0050\u95e8\u7981\u548c\u4e2d\u6587\u62a5\u544a\u5de5\u4f5c\u6d41\u3002"
  summary_en: SSQuant Agent workflow for futures strategies, data services, CTP gates, and Chinese reports.
---

# SSQuant Agent Contract

This repository is the SSQuant Agent workflow for futures-focused SSQuant work. The root `AGENTS.md` is the QUANTSKILLS agent declaration and execution contract. The optional `skills/ssquant/SKILL.md` file is only a compatibility bridge for runtimes that still discover capabilities through a local skill directory.

## Operating Rules

- Start by locating the exact SSQuant checkout and reading nearby examples before writing code.
- Keep user strategy code readable. Users should write trading logic, not framework plumbing.
- Prefer SSQuant's public `StrategyAPI`, `UnifiedStrategyRunner`, and `RunMode` over internal engine calls.
- Treat futures strategies, data services, reporting, and live CTP as separate lanes. Do not mix semantics.
- Keep edits scoped. Avoid unrelated framework refactors while fixing a strategy or report.
- Preserve local user changes. Do not reset, checkout, or delete user work unless explicitly asked.

## Evidence Gates

Before saying work is complete, provide at least one concrete artifact:

- environment: `scripts/ssquant_doctor.py --project <root>`
- strategy: `python -m py_compile <strategy.py>` and `scripts/validate_strategy.py <strategy.py>`
- backtest: command output plus generated report path
- data: cache row count, API response, SQL query, or data file inspection
- report: rendered HTML/Markdown path plus inspected metric fields
- live/CTP: process list, bounded logs, account-safe status, and explicit user authorization

## Live Trading Gates

- Query-only, SIMNOW, and real trading are different risk levels.
- Real CTP startup, order entry, cancellation, or scheduled trading requires an explicit current-user confirmation.
- Do not print secrets.
- Do not place orders from `888` or `777` until SSQuant resolves a concrete tradable contract and the user confirms that contract.
- Stop at diagnosis when the user has not authorized runtime changes.

## Data Rules

- Treat `symbol + period + adjust_type + range/limit` as the data-source identity.
- Remote services may return raw bars. `adjust_type` may be applied locally by SSQuant.
- Prevent repeated missing-data loops with cache inspection, cooldown, or "server returned no more bars" markers.
- Large history pulls should use the async-task path when the local project supports it.

## Report Rules

- Chinese reports should be readable and fixed-template based.
- Never hide missing-data warnings, insufficient trades, rejected orders, unrealistic costs, or report-generation bugs.
- When comparing runs, keep symbol, period, range, data mode, costs, and benchmark consistent.

## Publishing Rules

- QUANTSKILLS uses `SKILL.md` for `skill-*` repositories and `AGENTS.md` for `agent-*` repositories.
- This package is intentionally one repository: `quantskills/agent-ssquant`.
- Do not add unsupported domain instructions until the relevant SSQuant version is ready and explicitly approved for publication.
- Do not split the SSQuant lanes into separate public repositories unless the project owner explicitly changes that packaging decision.
