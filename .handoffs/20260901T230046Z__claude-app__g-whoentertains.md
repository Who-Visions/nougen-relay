# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FAN-OUT LIVE: shards.nougenai.com now returns blade + phoebus as one union (12 hits, 6 per node, complete=true) — v2 race-with-deadline deployed and verified
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:00:46.576Z

---
Closing the thread from legs `20260901T202643Z` → `204618Z` → `210232Z` → `211348Z`. **Fan-out is live and verified.**

Deployed `nougen-fleet-mcp` at **22:59:28Z**. A single `shards_search` through `shards.nougenai.com` now returns:

```
count: 12, fanout: {blade:"ok", phoebus:"ok"}, complete: true
```

6 hits from each node, every hit tagged `source_node`. **Phoebus-only rows are reachable from every fleet connector for the first time** — e.g. shard 9751 (macOS keyring prerequisite) and 10032 (brain-import throughput), neither of which exists on blade. One connector, whole fleet.

## What changed from v1
v1 used `Promise.allSettled`, which resolves only when *every* arm settles — so a slow peer billed every read its full timeout before blade's answer could return. v2 races:
- both arms start together, only the **primary** is awaited normally
- the peer carries its **own** budget via a scoped env copy: `SHARD_HTTP_TIMEOUT_MS`/`SHARD_SSE_TIMEOUT_MS` = `PHOEBUS_TIMEOUT_MS` (default 12000) and `SHARD_CALL_MAX_ATTEMPTS=1`, since a retry doubles the wait on the already-slower half
- after the primary lands the peer gets at most `PHOEBUS_GRACE_MS` (default 6000) more, then the answer ships without it

Worst-case added latency is the grace window, not the peer's whole budget. Both knobs are plain vars, tunable without a redeploy, as is `SHARD_FANOUT=off`.

Writes still never fan out — allowlist over the three read tool names resolved from the same `SHARD_TOOL_*` vars the handlers use, so it can't drift and a new tool can't inherit fan-out by omission.

## Near-miss worth more than the feature — please read if you touch this bundle
Re-fetching the live bundle before patching produced a JS file **missing its first three lines: the esbuild preamble defining `__name`**, which the bundle calls 68 times. Cause: my extractor split multipart headers from body on `\n\n`, but after my own earlier deploy Cloudflare returned the part with `\r\n\r\n` separators, so the split fell through to the next blank line — the one after the `__name` definition. Deploying that would have killed the worker on its first request.

**It would have passed the deploy gate**, because the gate checked that the string `__name` appeared — and 68 call sites still contain it. **Presence of a symbol is not presence of its definition.** Gate now asserts the definition text and that the file begins with `var __defProp = Object.defineProperty;`. Extractor now prefers `\r\n\r\n`, validated by re-extracting a known-good bundle and confirming byte equality with what is actually running.

**General rule for this untracked bundle: when you round-trip it through the API, diff the re-fetched copy against what you shipped BEFORE editing. The transport reformats what it returns, and a truncation at the top of a bundled file is invisible to any check that only counts occurrences.**

## Discipline that held
Content-only PUT with `keep_bindings` for both types; guarded on `modified_on` so a concurrent lane deploy aborts rather than gets reverted; bindings re-read after every deploy because the PUT response is not evidence. **32 bindings intact across all four deploys today.**

**Known remaining**: phoebus's node degrades with uptime (leg `211348Z`) — needs periodic restarts to stay inside the peer budget, root cause still unfound. If phoebus misses the grace window the answer degrades honestly (`complete:false`) rather than silently.
