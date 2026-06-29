# Raw Data And Local Adjustment

## Important Semantics

`adjust_type` is a client-side request intent. In current SSQuant remote-data architecture, the remote server can return raw bars, and SSQuant applies local adjustment before exposing strategy continuity prices.

Practical interpretation:

- `adjust_type="0"`: no adjustment.
- `adjust_type="1"`: backward-adjusted continuity may be applied locally.
- `adjust_type="2"`: forward-adjusted continuity may be applied locally.
- Raw execution/accounting prices should remain raw where the framework supports raw/adjusted separation.

## Customer Question Pattern

If a SIMNOW user says:

> I set `adjust_type=1`, but historical minute data or realtime minute data still looks like actual prices.

Explain:

1. `data_server` may transmit raw data.
2. SSQuant applies adjustment locally where the historical path supports it.
3. Live/SIMNOW realtime bars may still reflect actual tradable prices for execution safety.
4. Strategy continuity and execution/accounting can intentionally use different price semantics.
5. Verify by checking `local_adjust.py`, `api_data_fetcher.py`, and `StrategyAPI.get_price/get_raw_price` in the active project.

Do not tell the user the server must have sent adjusted prices unless the server response was inspected directly.

## Fields To Inspect

- `real_symbol`: required for reliable continuous-contract adjustment and rollover detection.
- `_adjust_factor`: internal detail; do not manipulate in user strategies.
- `raw_price` or `current_raw_price`: internal/accounting detail; do not manipulate in user strategies.

