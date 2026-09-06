# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: P1: Fix semantic recall false negatives with malformed shard DB index 8
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:07:12.473Z

---
## Incident

ChatGPT connector live test on 2026-08-30 found the shard gateway healthy and the corpus present, but semantic recall is returning false negatives.

### Verified state

- `shards_status`: `up=true`, `health_up=true`, `mcp_up=true`, `configured=true`
- `shards_coverage`: 80,529 total shards visible
- Span: 2010-05-08 through 2026-08-30
- August 2026: 16,102 shards
- Grid reports 9 DBs expected, 8 mounted
- DB index 8 errors with: `DatabaseError: database disk image is malformed`
- `read_through=true`
- `recall_trustworthy=true` is currently misleading given observed failures

### Reproduction

Semantic recall against high-confidence anchors returned `(no recall results)` even though the corpus is large and those topics are known to exist. Tested anchors included Shadow Dweller and NouGen Q.

### Required fix

1. Repair, restore, or rebuild shard DB index 8.
2. Audit the semantic recall fanout so one malformed DB cannot collapse or poison recall across the remaining healthy databases.
3. Make recall degrade gracefully and still return hits from healthy DBs.
4. Change `recall_trustworthy` semantics so it cannot report true when a mounted DB is malformed or recall fanout is degraded.
5. Add a regression test: corrupt or quarantine one DB, query a known shard in another DB, and require a valid result plus an explicit degraded-state diagnostic.
6. After repair, rerun recall for known anchors and verify non-empty results.

### Done when

Known anchors return semantic hits, DB 8 is healthy or safely quarantined, degraded recall is observable rather than silently empty, and `recall_trustworthy` accurately reflects the state of the retrieval path.
