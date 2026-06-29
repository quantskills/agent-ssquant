# Futures Rollover Cost

There are two separate rollover concepts. Do not merge them.

## `auto_roll_enabled`

Purpose: SIMNOW/real trading automatic migration from one concrete contract to another.

Scope:

- Runtime/live operation.
- CTP subscription and order behavior.
- Requires account and final live-operation gates.

Do not use this flag to simulate historical backtest rollover cost.

## `backtest_rollover_cost_enabled`

Purpose: historical backtest cost simulation when a continuous contract changes `real_symbol`.

Default:

```python
backtest_rollover_cost_enabled = False
backtest_rollover_price_mode = "prev_close_to_curr_open"
backtest_rollover_slippage_ticks = None
backtest_rollover_report_enabled = True
```

Rules:

- Detect rollover only from `real_symbol`.
- If `real_symbol` is missing, do not fail the backtest and do not deduct cost.
- If position is zero, record detection but do not create synthetic trades.
- If long across rollover, create rollover close-long and rollover open-long records.
- If short across rollover, create rollover close-short and rollover open-short records.
- Use raw prices for PnL and accounting to avoid adjusted-price contamination.
- Keep `is_rollover`, `old_real_symbol`, `new_real_symbol`, and `rollover_id` in trade details when supported.

## Report Expectations

When enabled, reports should include:

- enabled status
- rollover count
- rollover trade count
- rollover commission
- rollover slippage
- total rollover cost

Default-off behavior must preserve old backtest results.

