# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of the false-empty reads: the grid fan-out catches sqlite3.OperationalError but a corrupt DB raises its PARENT DatabaseError, so ONE bad DB killed every ranked read across all 9. Fixed + regression test
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:48:20.277Z

---
## The false-empty is an uncaught exception class

`src/nougen_shards/core.py`. The federated fan-out is:

```
for i in range(1, MAX_DB_COUNT + 1):
    conn = get_connection(i)
    try:
        ...
    finally:
        conn.close()
```

`try`/`finally`, **no except**. The only guard sits inside, around the FTS SQL, and it catches `sqlite3.OperationalError`.

A corrupt file raises **`sqlite3.DatabaseError`** - the *parent* class. `except OperationalError` never matches it. So the exception escaped the for-loop entirely and killed the whole federated read, leaving eight healthy DBs unread.

`shards_coverage` has been printing the answer all along: `databases_errored: [{index: 5, "DatabaseError: database disk image is malformed"}]`.

## The triage that found it (whoart, cross-session)

Three read paths, same lane, same moment:

| path | ranks? | result |
|---|---|---|
| `shards_recall` (semantic) | yes | **empty** |
| `shards_search` (FTS5) | yes | **empty** |
| `shards_window` (date filter) | no | **returned content** (id 22215, `_db_index` 9) |

The paths that rank return nothing; the path that filters on timestamp and never enters the fan-out returns rows. Not data loss, not reachability, not auth.

## Federation hypothesis: dead. Blade's grid is perfect.

Per-DB on blade, all 9: `quick_check` **ok** on every one, and FTS row count **exactly equal** to shard count on every one (31342/31342, 29770/29770, 27049/27049, 27462/27462, 30286/30286, 28848/28848, 30131/30131, 29065/29065, 26091/26091). **260,044 shards total.** No unmounted DB, no stale index, nothing missing.

**Which sharpens the origin point:** blade holds **260,044** shards; the node the Outpost lane reads reports **199,877 total / 178,122 mounted**. Those are not the same vault. The lanes differ in **content**, not just in health - so a shard "missing" on one lane may simply live on the other.

## Fixed
- All **5** fan-out loops now `except sqlite3.DatabaseError`: log the failing index, record a `DB_DEGRADED` history event, `continue`. A partial answer from 8 DBs beats a false empty every time.
- The connection is opened **inside** the try. `get_connection()` runs `PRAGMA journal_mode=WAL`, so a corrupt file raises *before* the loop body starts - the first version of this patch still died on it. The test caught that; without it a half-fix would have shipped.
- `tests/test_grid_corrupt_db_degrades.py`: write a shard to DB 1, shred DB 2's pages behind a valid header, assert recall still finds it. Fails on the old code, passes now, captured log reads `grid DB 2 unreadable during scan, skipping it`.

## What this does NOT fix
The corrupt DB5 lives on the **Space node**, not blade. Ranked reads on lanes pointing there stay empty until that node runs this code, or its DB5 is re-synced from blade's healthy copy. The fix makes the failure **survivable**, it does not repair the file.

## Still open
- **`/health` is a false green one layer deeper**: `health_up: true` while every ranked read returned nothing. It checks reachability, not retrieval. Same family as the case in `gateway_probe.py`'s docstring. Deserves its own fix.
- whoart's ~03:15Z shard is **not** settled and no lane is claiming data loss. A miss only becomes informative once the reading node has this fix.
- `shards_capture` returning a bare `{}` on the unreachable path - should raise.
- **Rhea's Space** still held for GM (no-op push to force a rebuild).
- **`CLOUDFLARED_NGS_TUNNEL_TOKEN`** still absent from blade's vault; `blade.nougenai.com` stays 530.

Pushed so far: `0c23aa1` on `codex/shards-capture-main` (gateway_probe three states, supervisor + tunnel_lane fixes). The core.py fan-out fix follows once the full suite is green.
