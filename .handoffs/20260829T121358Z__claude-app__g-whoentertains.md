# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SHIPPED: grid fan-out survives a corrupt DB (b6b364c) + recall_trustworthy no longer launders a dead upstream into a green verdict (f9fc71f), both with regression tests. blade.nougenai.com is now incident-critical: it is the DB5 repair path
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:13:58.042Z

---
## Shipped on `codex/shards-capture-main`

**`b6b364c` - one corrupt DB no longer zeroes every ranked read.** All 5 federated fan-out loops in `src/nougen_shards/core.py` now `except sqlite3.DatabaseError` per database: log the failing index, record a `DB_DEGRADED` history event, `continue`. The connection is opened **inside** the try - `get_connection()` runs `PRAGMA journal_mode=WAL`, so a corrupt file raises before the loop body starts and the first version of the patch still died there. The regression test caught that; without it a half-fix would have shipped.
`tests/test_grid_corrupt_db_degrades.py` shreds a DB's pages behind a valid header (a torn write, not a truncation, so the connection opens and the read fails the way the real one did) and asserts recall still finds a shard on a healthy sibling.

**`f9fc71f` - `recall_trustworthy` no longer lies while a DB is unreadable.** It was `complete or bool(upstreams)`. **Two** faults in that one expression, not one:
1. An errored database is a fault, not a thin-cache-in-front-of-an-upstream situation. Its rows are dark and no upstream flag makes them readable.
2. The upstream escape hatch rested on an unchecked premise - the function never probes whether the upstream **answers**. The one configured that day was returning **530**. So the expression was laundering a dead host into a trustworthy verdict.

There is a `recall_trustworthy_reason` now. The incomplete-plus-upstream case still returns true but states in its reason that upstream reachability is unverified, so the remaining assumption is visible instead of implied. `tests/test_coverage_trust_when_db_errored.py` fails on the old code **only with an upstream configured** - it asserts the exact laundering path.

This matters more than the other fixes because `shards_coverage`'s own description tells callers to check it *"before concluding a recall miss means the memory does not exist."* It was the designated arbiter for the question the whole fleet spent the morning on, and it was answering wrong.

## Mechanism demonstrated, not inferred (whoart)
Shard 23238 lives on `_db_index 2` - mounted, healthy, 22,361 rows - and was **still** unrecallable, because the fan-out aborted at index 5 before index 2 was ever reached.

Blast radius arithmetic: `total_shards` 199,877 vs `grid.shards` 178,122; the 8 mounted DBs sum to exactly 178,122, so DB5 holds ~21,755. Pre-fix, that one file took all 199,877 dark. Post-fix, 178,122 come back and ~21,755 stay dark until DB5 is repaired.

## `blade.nougenai.com` is INCIDENT-CRITICAL, not housekeeping
The node reports `read_through: true` with `upstreams: [{name: blade, url: https://blade.nougenai.com}]` - the host that is **530**, whose named tunnel was never credentialed. So the read-through that exists precisely to cover missing shards cannot reach blade, and the remedy for DB5 ("re-sync from blade's healthy copy") is blocked by that same dead hostname. It is the repair path for this incident and the standing safety net for the next one. `CLOUDFLARED_NGS_TUNNEL_TOKEN` needs provisioning on blade - **GM**.

## Standing caution: the lanes differ in CONTENT
Blade **260,044** shards (all 9 DBs `quick_check` ok, FTS count == shard count on every one). The node behind the Outpost lane: **199,877** total / **178,122** readable. ~60k apart, and **neither is a superset by assumption**. A shard "missing" on one lane may simply live on the other. Do not reconcile these by guessing.

## Not settled, and precisely why
The ~03:15Z shard. Even once the affected node runs `b6b364c`, a miss is informative only for the 8 healthy DBs. **If that shard landed on DB5, a miss stays uninformative** until DB5 is repaired or resynced. Nobody should declare it lost before then.

## Shared-tree note for whoever owns core.py / app.py
Both files carry uncommitted in-flight work in blade's tree that is not mine, inside the same functions I touched. I stashed it, applied only my hunks onto HEAD, tested, committed, and restored it - what got pushed is my change alone and that work is untouched in the working tree.
Two failures are **that work's, not mine**: `test_search_bounded_still_returns_sparse_era_shards` and `test_capture_accepts_relay_provenance_and_utility` fail with it applied and pass without it. I have not touched them - they are their owner's to land. Full suite: **14 failed / 676 passed** both before and after my changes; several are environment-flaky on this box (VRAM gate, model client).

## Still open
- **Rhea's Space** - GM. No-op push to force a rebuild; whoart has `contribute-repos` but no runtime/logs/restart scope.
- **`CLOUDFLARED_NGS_TUNNEL_TOKEN`** - GM. Now incident-critical per above.
- **`shards_capture` returns a bare `{}`** on the unreachable path instead of raising.
- **`/health` is a false green one layer deeper**: `health_up: true` while every ranked read returned nothing. It checks reachability, not retrieval.
