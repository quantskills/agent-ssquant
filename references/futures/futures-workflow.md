# Futures Strategy Workflow

## Minimal High-Performance Pattern

```python
import pandas as pd

from ssquant.api.strategy_api import StrategyAPI
from ssquant.backtest.unified_runner import UnifiedStrategyRunner, RunMode
from ssquant.config.trading_config import get_config


def initialize(api: StrategyAPI):
    fast = api.get_param("fast_ma", 5)
    slow = api.get_param("slow_ma", 20)
    api.register_indicator(
        "ma_fast",
        lambda c, o, h, l, v: pd.Series(c).rolling(fast).mean().to_numpy(),
        window=fast,
        index=0,
    )
    api.register_indicator(
        "ma_slow",
        lambda c, o, h, l, v: pd.Series(c).rolling(slow).mean().to_numpy(),
        window=slow,
        index=0,
    )


def strategy(api: StrategyAPI):
    fast = api.get_indicator_array("ma_fast", window=2, index=0)
    slow = api.get_indicator_array("ma_slow", window=2, index=0)
    if fast is None or slow is None or len(fast) < 2 or len(slow) < 2:
        return
    if pd.isna(fast[-1]) or pd.isna(slow[-1]):
        return

    pos = api.get_pos(index=0)
    if fast[-2] <= slow[-2] and fast[-1] > slow[-1] and pos <= 0:
        if pos < 0:
            api.buycover(volume=abs(pos), order_type="next_bar_open", reason="cover short", index=0)
        api.buy(volume=1, order_type="next_bar_open", reason="golden cross", index=0)
    elif fast[-2] >= slow[-2] and fast[-1] < slow[-1] and pos >= 0:
        if pos > 0:
            api.sell(volume=pos, order_type="next_bar_open", reason="close long", index=0)
        api.sellshort(volume=1, order_type="next_bar_open", reason="dead cross", index=0)
```

## Multi-Source Pattern

```python
config = get_config(
    RunMode.BACKTEST,
    data_sources=[
        {"symbol": "rb888", "kline_period": "30m", "adjust_type": "1"},
        {"symbol": "au888", "kline_period": "30m", "adjust_type": "1"},
    ],
    start_date="2024-01-01",
    end_date="2025-01-01",
    data_source_mode="data_server",
)
```

Do not use a comma-separated single `symbol` to represent multiple sources unless the local loader proves support.

## Cost And Execution Notes

- Confirm `contract_multiplier`, `price_tick`, `margin_rate`, `commission`, and fixed per-lot commission fields.
- Use realistic slippage for futures backtests.
- Keep order reasons explicit; they are needed for report review.
- Low trade count, large drawdown, or unstable costs must be reported as risk, not hidden behind total return.

## Validation

```powershell
python -m py_compile <strategy.py>
python <agent-root>\scripts\validate_strategy.py <strategy.py>
python <strategy.py>
```

If `validate_strategy.py` is not on the current working path, run it from this repository's `scripts/` directory.
