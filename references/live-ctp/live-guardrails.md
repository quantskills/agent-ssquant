# Live CTP Guardrails

## Before Startup

Confirm:

- run mode: SIMNOW or REAL_TRADING
- account key, not password
- concrete contract
- K-line source: `local` or `data_server`
- preload settings
- order type and volume defaults
- logging path
- maximum startup wait

For real trading, ask for final confirmation after restating the exact account key, contract, direction capability, and process command.

## Before Order Or Cancel

Restate:

- mode
- account key
- concrete contract
- action: buy, sell, sellshort, buycover, cancel, or cancel all
- open/close
- volume
- order type
- price or offset ticks
- timeout

Execute only after final confirmation. Redact credentials in all outputs.

## Evidence

Acceptable evidence:

- bounded command output
- live log lines
- process id plus command line
- query response with credentials redacted
- order/trade callback lines with account identifiers redacted

Not enough:

- "the code should run"
- config presence without a launch
- old logs from a different run

