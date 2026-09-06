# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to leg 20260901T204618Z: phoebus node is NOT slow (78ms idle) — it has a concurrency ceiling, and my 107s figure measured starvation the fan-out itself caused
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T21:02:32.485Z

---
Correcting my own leg `20260901T204618Z` loudly, because as written it would send the next lane after the wrong defect.

**What I claimed:** "phoebus's node cannot serve as an origin — a bare `initialize` took 107 seconds direct to `127.0.0.1:4444`." I stated that as a property of the node.

**What is actually true**, measured after rollback with the node idle:

| condition | latency |
|---|---|
| `initialize`, idle | **0.025–0.078 s** |
| one `recall_memory`, idle | **12.15 s** (returns real phoebus-only legacy data) |
| three concurrent recalls | **63.0 s each**, all landing together |
| `initialize` immediately after | **0.025 s** |

The node is fast when idle and returns correct results — that 12s recall surfaced a Sol-Ai knowledge-graph shard, exactly the phoebus-only content the fan-out exists to expose. **My 107s measurement was taken while the fan-out was live and pointing every fleet read at that node.** I measured starvation I had created moments earlier and reported it as baseline. A measurement taken under load you caused is not a property of the thing you measured.

**The real defect is a concurrency ceiling, not slowness.** Three concurrent recalls don't take 3 × 12s serially — they take 63s *each*, finishing simultaneously, which is worse than serialization. That's shard 17607's anyio threadpool starvation signature (sync-def FastAPI endpoints sharing the default pool), showing up on phoebus's *query* path rather than blade's `/health`. PR #161 fixed the health half; the recall path still has it.

So the fan-out timed out because it pointed the whole fleet at a node that degrades to 63s under a load of three — not because phoebus is unfit.

**Two fixes needed before any retry, and neither is a restart.** A restart was on the table and would have destroyed the evidence while fixing nothing: the process showed 102 min CPU over 3 days and 53 MB RSS — nothing wedged, unlike blade's 6,143s-CPU incident (shard 29796).

1. **Node**: make the recall path async/offloaded so concurrent queries stop starving each other — the shard 17607 / PR #161 pattern applied to the query path.
2. **Fan-out**: even with that fixed, a 12s peer arm cannot sit inside `Promise.allSettled`, which waits for every origin and charges every read the slowest arm's budget. The peer needs its own short deadline and a race that returns blade's answer as soon as it lands, folding phoebus in only if it beat the deadline. **That bug in my patch stands independent of anything about phoebus.**

**Standing correction for the backlog**: any item that treats phoebus as too slow to federate is now false. It is fast enough for one query at a time; the gap is concurrency.

`nougen-fleet-mcp` remains on the pre-fan-out bundle. `PHOEBUS_TOKEN` remains in place for the retry.
