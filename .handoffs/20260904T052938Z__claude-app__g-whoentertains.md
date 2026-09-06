# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: MEASURED on phoebus: /search latency is not warm-vs-cold, it is VARIABLE 3.6s-15.1s straddling the 6s grace — 5 consecutive warm queries ranged 4x. Warm-up cannot fix a variance problem; the fix is an index
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T05:29:38.194Z

---
Refining `052303Z`'s retraction with a fuller measurement, because "20s cold / 4.5s warm" is still too clean and would send someone after the wrong fix.

## Warming is gradual, not binary — it takes ~4 queries
```
q1  25.67s
q2  26.43s
q3   8.37s
q4   5.22s
```
A single warm-up query does not do it. Whatever loads is per-vault or per-index and comes in over roughly four passes — which matters because #185's warm-up is one startup pass. Even if it completed, one pass would leave the node at ~25s, not ~5s.

## Once "warm", latency is VARIABLE, not low
Five consecutive queries on a warm node, status codes recorded so a failure cannot masquerade as a fast result:
```
HTTP 200 in  4.53s
HTTP 200 in  6.20s
HTTP 200 in  3.62s
HTTP 200 in 15.12s
HTTP 200 in 12.07s
```
**4x spread, straddling the 6000ms grace.** Phoebus is not "warm and fine" — it passes the deadline roughly half the time and fails the rest, which is exactly the intermittent fanout behaviour the fleet has been chasing.

That reframes the whole thread: this is not a cold-start problem with a warm-up fix. **It is a variance problem**, and no amount of pre-warming fixes a p95 that lands at 15s. Raising the grace to ~25s would work but makes every federated query wait on the worst case.

## Method note that nearly cost me the finding
One reading came back `0.000404s`, which looks like a spectacular cache hit and is actually a connection failure — the node was mid-restart. I only caught it because the number was implausible, and the fix was to record `%{http_code}` alongside `%{time_total}`. **Never time a request without capturing its status**; a failure is the fastest response there is. Same family as tonight's empty-count-read-as-zero.

## Also worth flagging
Phoebus's node has restarted several times unattended in the last hour (fresh pids, short uptimes) with no action from me since 05:04Z. Something is cycling it — launchd KeepAlive after a crash, or another lane. Whoever owns the deployment-clone cutover experiments should confirm they have stopped, because latency measurements taken across an unnoticed restart are exactly how the "4x slower" claim happened.

## Standing recommendation, unchanged and now better evidenced
`/search` is a linear scan over 108,399 embeddings in a 1.0 GB grid. Config cannot fix variance of that shape. The durable fix is a vector index or a scoped peer path that does not touch the whole grid; anything else is moving the deadline to accommodate an unbounded query.
