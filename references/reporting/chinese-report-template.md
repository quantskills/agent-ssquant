# Chinese Backtest Report Template

Use this structure for Chinese reports.

## 1. Executive Summary

State the result plainly:

- strategy name
- market and instrument universe
- period and date range
- total return or net PnL
- max drawdown
- whether the result is usable, weak, or invalid

## 2. Backtest Settings

Include:

- run mode
- data mode
- symbol/data sources
- period
- adjustment type
- initial capital
- commission/slippage
- order type
- benchmark

## 3. Core Metrics

Include a compact table:

- total return or net PnL
- annualized return when available
- max drawdown
- Sharpe or equivalent
- trade count
- win rate
- average win/loss
- commission
- slippage
- rollover cost when enabled

## 4. Equity Curve And Drawdown

Charts should be visible in HTML reports. If charts are missing, treat it as a report bug or rendering gap.

## 5. Trade Analysis

Include:

- long/short split when available
- best/worst trades
- monthly or yearly distribution when available
- high-cost or high-turnover warnings

## 6. Data Quality And Warnings

Call out:

- missing bars
- cache misses
- remote failures
- synthetic or incomplete data
- same-bar signal/execution risk
- too-low trade count

## 7. Conclusion

Use direct language: pass, needs more validation, or invalid. Do not overstate.

