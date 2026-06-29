# Verification Standard

## Do Not Stop At Static Review

When the user asks whether SSQuant work is working, collect real evidence:

- `py_compile` success for generated or edited Python files.
- `scripts/validate_strategy.py` success for strategy files when available.
- A real backtest command and report path when the request asks for results.
- A data query count, cache table inspection, or API response when the request concerns data.
- A bounded process/log check when the request concerns SIMNOW, CTP, or automation.

## Completion Checklist

Before saying the task is complete:

1. List the explicit requirements.
2. Identify the file, command, report, or log that proves each one.
3. Inspect the evidence directly.
4. State unverified items clearly instead of implying success.

## Regression Testing Assets

For a QUANTSKILLS agent or skill package:

```powershell
$env:PYTHONUTF8='1'
python C:\Users\Administrator\.codex\skills\quantskills-asset-auditor\scripts\audit_asset.py `
  <asset-root-or-zip> `
  --output <audit-output> `
  --no-fail-exit
```

Then inspect `audit_report.md`, `audit_report.json`, and every `smoke_artifact.md`.
