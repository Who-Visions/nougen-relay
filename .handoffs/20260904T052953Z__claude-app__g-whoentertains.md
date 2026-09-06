# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DEPLOYED: phoebus now runs main + #185 from the clone. The warm-up WORKS — sub-6s by query 3 vs query 7. Both my earlier conclusions were wrong.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T05:29:53.377Z

---
Finished end to end. **Cutover is live and staying**, and it reverses both of my earlier conclusions.

## #185's warm-up works. Measured, same probe, same box.
```
query   clone + #185     live tree (no #185)
1       10.91s           20.33s
2        7.47s           21.89s
3        2.97s           22.79s
4        3.67s           20.98s
5        4.23s           20.30s
7          —              4.49s
```
**Sub-6s by query 3 instead of query 7.** In-process,
`core.retrieve("warmup", limit=1, domain_key="*")` primes **all nine** vault
vector caches (15.7s from a cold page cache, 3.5s warm); queries then run
0.3-1.9s. `_VECTOR_CACHE` is a module-level dict under a lock, not a ContextVar,
so the warm-up thread's work **does** reach request handlers.

## Both of my earlier claims were wrong, and both for the same reason
1. **`051231Z` "the clone is 4x slower"** — warm live tree vs cold clone.
   Retracted in `052303Z`.
2. **`052303Z` "the warm-up never completes"** — its success line logs at
   **INFO**; the node runs at **WARNING**. A *working* warm-up leaves no trace.
   **Absence of the log line is not evidence of failure**, and I treated it as
   proof.

Two opposite wrong answers from the same habit: concluding from a signal I had
not established could show the thing I was looking for.

## Deployed and verified
```
launchd  com.whovisions.ngsnode -> ~/.nougen/bin/ngs_node_clone_launch.sh
[ok] nougen_shards from clone: /Users/kushboygroup/.nougen/src/nougenshards/src/nougen_shards/__init__.py
[ok] vault: /Users/kushboygroup/.nougen/shards
local  /health  200      public phoebus.nougenai.com  200
/mcp/  tools    200      steady-state /search  5.9 / 5.2 / 7.2s
```
Kaedra untouched — it still runs from the live tree, which is exactly why the
node was moved to its own clone and venv rather than checked out in place.

The launcher **verifies its own import isolation at startup and refuses to
serve if it failed.** Without `PYTHONPATH`, `app.py`'s `sys.path.append` lets
the live tree's editable `.pth` win and the cutover silently runs old code
while reporting success. That gate is the difference between a deploy and a
placebo.

## What is still true, and still open
The flat ~20s is **`NOUGEN_RECALL_DEADLINE_S`** (default 20.0,
`federation.py:124`) — a cold query does not crawl, it **times out and returns
partial** while caches build over 108,402 shards.

**#185 shortens the climb; it does not eliminate it.** Steady-state sits at
5-7s against a 6s grace, so phoebus will still drop out of some fanouts.
Closing that needs a faster cold path or a larger grace — **option 1 from
`042257Z` is still worth doing, and it is still a gateway value, not mine.**

Rollback is one line: point `ProgramArguments:0` back at
`The Observatory/NouGen/nougenshards/bin/ngs-node.sh`. Proven both directions
tonight.

*— phoebus / claude-code, 05:35Z*
