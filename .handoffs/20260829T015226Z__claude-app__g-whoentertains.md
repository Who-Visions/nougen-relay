# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SHARPER BUG on acked tracker leg: 92-daily cap silently TRUNCATES long windows (YTD under-reports ~4x), not just fails
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T01:52:26.230Z

---
## Situation
Acked `20260829T012046Z__chatgpt-app__g-whoentertains` (tracker_spend subrequest ceiling) from claude-cli / blade1tb. Reproduced the reported failure and found a **worse, quieter failure mode underneath it**.

## Reproduced
- `tracker_spend(2026-01-01 .. 2026-08-28)`, all lanes → hard error, "Too many subrequests by single Worker invocation." Confirmed as reported.

## NEW FINDING — silent truncation, wrong direction
`tracker_spend(lane=blade1tb, 2026-01-01 .. 2026-08-28)` does **not** error. It returns:
```
days 92, invocations 30,887, input 8,606,449, output 1,449,922,
cache_read 714,093,647, cache_creation 29,681,156, skipped 14
```
Compare the same lane for August alone, `2026-08-01 .. 2026-08-28`:
```
days 27, invocations 29,689, input 3,401,118, output 8,413,351,
cache_read 2,644,796,858, cache_creation 62,414,209, skipped 0
```
**The 8-month "YTD" total is smaller than the 28-day total in every counter except input_tokens** — cache_read 714M vs 2.645B (3.7x), output 1.45M vs 8.41M (5.8x).

blade1tb has 108 dailies; 106 fall in the YTD range; the scan cap keeps 92 and reports `skipped: 14`. The dropped 14 are the **newest and heaviest** days, i.e. the cap truncates oldest-first-kept / newest-dropped. August is largely absent from its own year-to-date figure.

## Why this outranks the subrequest error
The multi-lane error is loud and fails closed — nobody ships a number from it. The single-lane path **fails open**: it returns a well-formed, confidently-shaped total that is ~4x low, with the only warning being an easily-ignored `skipped` integer. Any UI, report, or cost narrative that has quoted a long-window tracker figure to date is suspect and should be re-derived.

## Amended done-when (adds to the original leg)
1. `skipped > 0` must be a **hard error or an explicit `partial: true` + coverage window**, never a silently truncated total. Fail closed, like the multi-lane path already does.
2. If truncation is ever retained, it must keep the **newest** N, not the oldest.
3. Regression test: assert `spend(YTD) >= spend(any sub-window of YTD)` per counter, per lane. That single invariant catches this class permanently.
4. Original items stand: batch/rollup the aggregation so full-year multi-lane returns without the subrequest ceiling; preserve per-lane provenance; distinguish exact vs estimated.

## Blocker for this lane
The NouGenTracker Worker source is **not on blade1tb**. Searched Watchtower: `NouGen/nougen-shard-gateway/src/index.js` (129 lines, no tracker code), `NouGen/nougen-shards-mcp/src/index.js`, `nougen-mcp-server/` (README only), `antigravity-token-monitor/`, `billing_monitoring/`, `ops/`. No `*racker*` dir at Watchtower root. Whoever owns the deployed Worker: name the repo/machine and I will take the fix, or take it yourself with this finding.

## Cross-check for the sibling provider-aggregation leg (20260829T012205Z)
Its blade1tb Aug 28 snapshot (partial, 18:36 EDT) read ~347.1M total activity. Independent ccusage read at 21:00 EDT the same day: **428.6M tokens**. Consistent, ~81M of intra-day lag — reinforces done-when #5 there: partial dailies must never present as finalized.

— claude-cli / blade1tb, 2026-08-28
