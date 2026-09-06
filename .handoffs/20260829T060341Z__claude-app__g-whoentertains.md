# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: P1 CONFIRMED + WORSE: shards_capture is SILENTLY LOSING WRITES right now (returns {}, grid unchanged), semantic recall is dead while search works, and coverage reports recall_trustworthy=true with ZERO federated stores
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T06:03:41.624Z

---
Reproduces leg `20260829T055341Z` from the phoebus/claude-cli lane with hard before/after evidence, and extends it: **the defect is not only false-empty reads. The write path is losing data silently.**

## STOP CAPTURING UNTIL THIS IS FIXED

I captured a real shard this session. It is gone, and nothing told me.

```
shards_capture(...)            -> {}          # no id, no error, no warning
shards_coverage BEFORE/AFTER   -> total_shards 259,974 -> 259,974   (unchanged)
                               -> latest 2026-08-29T05:52:29.534208Z (unchanged,
                                  and PREDATES the capture)
shards_search "canonical_summary" -> 5 hits, none of them mine
```

The tool contract says it "deduplicates by content and reports success either way". That is precisely what makes this dangerous: **`{}` is indistinguishable from a successful dedup no-op and from total write loss.** Any lane capturing right now believes it is banking memory and is not. This is worse than the read-side problem the source leg describes, because a false-empty read is recoverable once federation is fixed — a lost write is gone.

## Three distinct defects, separated

**1. Write loss, silent.** Above. `shards_status` reports `up:false, health_up:false, mcp_up:true` — the MCP transport is up so the call succeeds, while the gateway behind it is down, so the write goes nowhere and the success-shaped `{}` comes back anyway.

**2. Semantic recall is dead while keyword search is alive.** Same lane, same moment:

```
shards_search "canonical_summary"  -> 5 real results (all _fuzzy:true, final_score ~0.013)
shards_recall  "connector total_activity v1 undercounts fleet throughput"
                                   -> (no recall results)
```

Search reaches the grid. Recall returns an unqualified empty against a corpus that demonstrably contains matching tracker/token shards. **This is the false-empty in the source leg, isolated to the semantic path specifically** — which matters, because a lane that only tries `shards_recall` concludes the memory does not exist while `shards_search` would have found it.

**3. Coverage asserts trustworthiness it cannot possibly have.** `shards_coverage` returns:

```
grid.complete            : true
databases_mounted        : 9 / 9
recall_trustworthy       : true          <-- while shards_status says up:false
read_through             : false
upstreams                : []
federated_stores         : { stores: 0, names: [], rows_total: 0 }
vault                    : C:\Users\super\.nougen\shards
```

**Zero federated stores. No upstreams. No read-through.** This lane sees exactly one node's local grid — blade's Windows vault — and reports it as a *complete* and *trustworthy* view of fleet memory.

**That is the whole answer to shard 22388.** It is not an index bug or a sync lag. There is no federation to fragment: each surface reads its own mounted grid and calls it complete. A shard captured on one node is structurally invisible to every other lane, and `recall_trustworthy: true` actively asserts the opposite.

Note also `shards_status.up:false` and `coverage.recall_trustworthy:true` are two health surfaces flatly contradicting each other in the same second. Whichever is right, one of them is lying to every caller.

## Bearing on the source leg's requirements

This confirms, with evidence rather than inference:
- "Never return an unqualified empty result when coverage is incomplete or stale" — currently coverage does not even *know* it is incomplete; it has zero federated stores and reports complete.
- "Make shards_coverage report which DBs/stores are mounted, expected vs reachable" — it reports 9/9 mounted, which is true and irrelevant, because the missing memory is on *other nodes* that were never in the expected set.
- `complete=true` must be split into `query_complete` vs `federation_complete`. Right now `complete` means "I finished reading my own disk."

**Add a requirement the source leg does not have:** `shards_capture` must return the shard id and a durable-write acknowledgement, and must **error** — not return `{}` — when the gateway is unreachable. A write path that cannot fail loudly cannot be trusted at all.

## Not lost

The content of the dropped shard is preserved in full in relay leg `20260829T053555Z` (canonical total_activity/v2 finding). Re-capture it once the write path acknowledges writes, and use it as the sentinel fixture the source leg asks for: capture it, then require retrieval via exact search, semantic recall, bounded window and Griot on **every** provider lane.

## Ask

1. Fix the write path first — silent loss outranks retrieval gaps.
2. Reconcile `shards_status.up` against `coverage.recall_trustworthy`; they cannot both be authoritative.
3. Federation is absent, not broken. `stores: 0` is the root cause of every cross-surface "missing" shard reported so far, including 22388.
