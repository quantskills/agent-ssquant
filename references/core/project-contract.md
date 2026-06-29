# SSQuant Project Contract

## Source Of Truth

Use the current local project as the source of truth. SSQuant forks often carry local fixes for data server batching, local adjustment, rollover cost, or report generation. Before relying on a document, inspect the local source.

Open these files first when present:

| Need | File |
|---|---|
| Strategy API behavior | `ssquant/api/strategy_api.py` |
| Run modes and runner | `ssquant/backtest/unified_runner.py` |
| Backtest loop | `ssquant/backtest/backtest_core.py` |
| Data loading | `ssquant/backtest/backtest_data.py`, `ssquant/data/api_data_fetcher.py` |
| Local adjustment | `ssquant/data/local_adjust.py` |
| Live bridge | `ssquant/backtest/live_trading_adapter.py` |
| Config defaults | `ssquant/config/trading_config.py`, `ssquant/config/config_helpers.py` |
| Reports | `ssquant/backtest/backtest_results.py`, `ssquant/backtest/html_report.py` |
| Examples | `examples/` at the project root |

## Version Gate

Require SSQuant `>=0.4.5` for StrategyAPI and UnifiedStrategyRunner workflows. If the local project is older, stop and ask for an upgrade unless the user explicitly asks for legacy diagnosis.

Private local forks may have features newer than their package version. Verify by reading source and running a small command rather than relying only on `__version__`.

## Strategy Boundary

User strategies should expose:

```python
def initialize(api):
    ...

def strategy(api):
    ...
```

They should be run through:

```python
runner = UnifiedStrategyRunner(mode=RUN_MODE)
runner.set_config(config)
runner.run(strategy=strategy, initialize=initialize, strategy_params=strategy_params)
```

Do not generate strategies that directly import low-level CTP adapters, mutate `DataSource` internals, or bypass the runner.

## Multi-Source Rule

Use `data_sources=[{"symbol": "...", "kline_period": "...", "adjust_type": "..."}]` for multiple instruments or periods. The single `symbol` field is for one logical source unless local source proves otherwise.
