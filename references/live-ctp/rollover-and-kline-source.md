# Auto Roll And Realtime K-Line Sources

## `auto_roll_enabled`

`auto_roll_enabled` belongs to SIMNOW/real runtime migration. It is not the same as backtest rollover-cost simulation.

Use it only when:

- the strategy runs in SIMNOW or REAL_TRADING
- the account and contract have passed live gates
- the framework can resolve continuous contracts to concrete contracts
- the user understands that runtime orders may close one concrete contract and open another

## `backtest_rollover_cost_enabled`

This belongs to backtesting and should not place live orders. See `references/futures/rollover-cost.md`.

## K-Line Sources

`kline_source="local"`:

- aggregate realtime CTP ticks locally
- suitable when the user wants local CTP-derived bars
- depends on CTP market data stability and local aggregation periods

`kline_source="data_server"`:

- use remote pushed/polled K-line data when supported
- requires data-server credentials
- may return raw data and apply local adjustment according to SSQuant behavior

## Derived Periods

If the local CTP aggregation supports only 1m/5m/15m, do not claim 30m/1h/1d live derivation works. Verify the aggregator source and session-end flush behavior.

For daily bars, session-end flush must finalize the last 1m bar and then force multi-period aggregators so same-day 1d can be written when supported.
