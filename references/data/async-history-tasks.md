# Async History Tasks And Parquet Artifacts

## When To Use Sync

Use synchronous history fetches for small requests only. A safe default is:

- source count within the configured sync limit
- total estimated bars within the configured sync limit
- response small enough to avoid long request timeouts

The exact numbers must come from the active project config. Previous local designs used examples such as 30 sync sources and 500,000 total bars.

## When To Use Async

Use async history tasks for large multi-source requests, such as hundreds of sources or tens of thousands of bars per source.

The server should:

- accept one task request
- split work internally
- isolate per-source failures
- produce a manifest
- produce downloadable result artifacts
- enforce per-account/IP and global task concurrency gates
- clean temporary artifacts after download or TTL

## Why Parquet Exists

Parquet task files are temporary transfer packages and audit-friendly result bundles. They are not meant to become permanent unbounded server storage.

Use them for:

- large result transfer
- migration verification
- reproducible task artifacts
- client cache population

Controls:

- small TTL after completion, such as a few hours
- delete after confirmed transfer when supported
- directory size cap
- global async-task concurrency gate
- per-account/IP async-task gate
- cleanup job on startup and schedule

## Client Closure

The task is not complete until a real SSQuant client can:

1. create or poll a task
2. download the manifest/artifact
3. read Parquet/Arrow
4. write local cache
5. run a second request that hits local cache

