# StrategyAPI Return Types

Check the local `ssquant/api/strategy_api.py` before finalizing code. Current SSQuant forks commonly expose these semantics:

## Scalars

```python
api.get_price(index=0)       # current strategy price, scalar or None
api.get_raw_price(index=0)   # raw current price, scalar or None when available
api.get_indicator(name, index=0)
api.get_datetime(index=0)
api.get_pos(index=0)
api.get_long_pos(index=0)
api.get_short_pos(index=0)
api.get_idx(index=0)
```

`api.get_price()` is not a full pandas Series in current checked forks. Do not tell users to call `.iloc[-1]` on `api.get_price()`.

## Series

```python
api.get_close(index=0)
api.get_open(index=0)
api.get_high(index=0)
api.get_low(index=0)
api.get_volume(index=0)
```

These return historical pandas Series through the current bar. Extract the current value before scalar comparisons:

```python
close = float(api.get_close(index=0).iloc[-1])
high = float(api.get_high(index=0).iloc[-1])
```

## Arrays

```python
api.get_close_array(window=None, index=0)
api.get_open_array(window=None, index=0)
api.get_high_array(window=None, index=0)
api.get_low_array(window=None, index=0)
api.get_volume_array(window=None, index=0)
api.get_indicator_array(name, window=None, index=0)
```

Prefer arrays or registered indicators inside high-performance strategies. Keep `strategy(api)` O(1) when possible.

## Common Failure

`ValueError: The truth value of a Series is ambiguous` usually means code compared a Series directly:

```python
if api.get_close(index=0) > ma20:
    ...
```

Fix:

```python
close = float(api.get_close(index=0).iloc[-1])
if close > ma20:
    ...
```

