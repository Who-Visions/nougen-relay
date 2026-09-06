# 🤝 Git Handoff — claude-app / gm-phone

**Goal**: RESOLVED + CORRECTION: blade /search 50.7s -> 4.1s. My bm25 root cause in leg 20260814T223029Z was WRONG — real cause was the unbounded fuzzy lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-14T23:21:23.989Z

---
## Supersedes `20260814T223029Z__claude-app__gm-phone`

**Do not action that leg's fix plan.** Its root cause was wrong. Details below so nobody rewrites working SQL.

## The correction

I claimed the 40s was `ORDER BY bm25(shards_fts)` forcing SQLite to score every matching row before LIMIT could prune. Measured on db1 with the real match expression from `_build_fts_match_query`:

| probe | result |
|---|---|
| match-set count for `"blade" "federation"` | **1 row** (I claimed ~150k) |
| current join + bm25 + ORDER BY, LIMIT 3 | **0.03s** |
| my proposed rank-subquery rewrite | 0.05s — **slower** |

`_build_fts_match_query` quotes each token as a phrase and space-joins, which is FTS5 implicit **AND** — highly selective. My "a large fraction of each DB matches" premise was never measured. The bm25 ordering was fine as written.

## Actual root cause

The fuzzy lane in `core.py` (was line 783). On the per-DB miss path it ran:

```sql
SELECT id, timestamp, title, content, utility_score, embedding, tags, domain_key, density_score
FROM shards ORDER BY id ASC        -- no LIMIT
```

then hydrated every row and computed char-ngram Dice in Python (~1ms/row). Its comment reasoned "runs only on the miss path, so exact matches never pay for it" — true per DB, but a query is only *exact* in the DBs that actually hold its shards. A term living in 1 of 9 DBs sent the other 8 into a full scan: ~134k rows per query. `retrieve()` then calls the lane **twice** (domain-scoped, then `"*"` on empty), paying it twice.

## Shipped

**483 passed, 4 skipped.** `core.retrieve` 43.5s → **3.58s**; live LAN `POST /search` 50.7s → **4.1s**.

1. Fuzzy lane deferred out of the per-DB loop into one pass after all DBs are scanned. Output-identical by construction — the final sort tiers every exact hit above every fuzzy hit then truncates to `limit`, so fuzzy rows computed when `limit` exact hits already exist were always being discarded.
2. Scores against `substr(content,1,256)` (all the probe ever reads); full rows re-fetched only for survivors.
3. Scan bounded by `NOUGEN_FUZZY_MAX_ROWS` (default 4000/DB, `utility_score DESC` first), and it **logs when the cap bites** — no silent truncation.
4. Trigger changed: `NOUGEN_FUZZY_TRIGGER` = `empty` (default — only when the exact lanes found nothing anywhere) or `underfilled` (previous behavior). **This one is a genuine recall tradeoff, not free.** Under `empty`, a query with 2 exact hits and `limit=20` no longer gets fuzzy padding. On a small vault the two settings agree; on this 151k-shard vault they diverge hard. Set `underfilled` to restore the old behavior at ~30s+ per query.
5. `connectors/cloud.py`: hardcoded `5.0` / `10.0` timeouts replaced with `NGS_CLOUD_SEARCH_TIMEOUT` / `NGS_CLOUD_SYNC_TIMEOUT`.

## Still open

- **Margin is thin.** 4.1s against a 5s default timeout. The remaining ~3.7s is *not* the FTS SQL (0.03s × 9 = 0.27s) and is still unprofiled. Suspects: `get_connection()` × 9 × 2 passes, and `history.log_event` writes per returned row. Worth one profiling pass before anyone calls this done.
- Node is still a foreground process — dies with the session. Boot-persistence unclaimed.
- Peers still need `NGS_ALLOW_INSECURE_CLOUD=1` to talk to `http://10.0.0.87:4444`, or the URL is refused before a request is sent.

## Method note for the fleet

I filed a confident root cause read off the SQL without measuring it, and it would have sent the next lane to rewrite correct code. The probe that killed it took one script: count the match set, time the current query, time the proposed replacement. Measure the hypothesis before putting it in a leg.
