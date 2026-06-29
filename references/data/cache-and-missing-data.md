# Cache, Missing Data, And Backup

## Cache Behavior

`data_cache/backtest_data.db` can make repeated backtests faster only when the requested source and range are fully covered.

A request may still go remote when:

- the requested end date is later than cached coverage
- the requested start date is earlier than cached coverage
- the period changed
- `adjust_type` changed
- the symbol changed
- the cache table is empty or corrupted
- the cache was copied without WAL checkpointing

Avoid writing docs that imply "second run is always local and fast".

## Missing Tail Loops

Problem pattern:

1. Framework checks trading calendar and thinks dates are missing.
2. It requests the missing tail.
3. Server has no bars for those dates or only partial bars.
4. Next backtest repeats the same request forever.

Required controls:

- Store a miss key: symbol, period, adjust type, requested range, server, and reason.
- Add TTL/cooldown for repeated no-data responses.
- Do not block other users or other symbols because one source repeatedly fails.
- For intraday periods, do not force a hard "previous trading day only" cutoff. Let the server return available bars.
- For daily periods, be more conservative about incomplete current-day bars.

## SQLite Backup Rule

Do not copy only `kline_data.db` or only `backtest_data.db` while SQLite WAL is active. Safe options:

- Stop the writer, checkpoint WAL, then copy the main DB.
- Use SQLite backup API.
- Copy main DB plus `-wal` and `-shm` only as a consistent set from a stopped or carefully checkpointed state.

Old `-wal` and `-shm` files from a different database should not be reused with a replaced main DB.

