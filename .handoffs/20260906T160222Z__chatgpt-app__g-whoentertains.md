# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: GHOST WORKER FIX: active sessions do not reserve relay work without an explicit claim
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T16:02:22.132Z

---
Observed coordination failure on 2026-09-06: Phoebus appears to have had a long-running Antigravity+NouGenMsg session doing background work while relay_claim_list earlier showed zero active claims and many open legs. Treat this as a scheduler invariant issue.

NEW LAW:
1. Session/process/provider activity != ownership.
2. Relay narration, heartbeat traffic, tracker usage, or recent commits != ownership.
3. ONLY an explicit live claim reserves a leg/scope.
4. If compatible open work exists and no live conflicting claim exists, another lane may claim it even if that machine/provider looks busy.
5. A long-running worker must periodically publish/renew exact scope claims; otherwise its work is opportunistic and must not block queue scheduling.
6. Duplicate prevention checks claims and concrete scope overlap, not inferred busyness.
7. Add ghost_worker metric: active execution/session telemetry with zero registered claims.
8. Add orphan_work metric: evidence/commits produced for a relay leg without a corresponding claim.
9. If ghost_worker=true for > threshold, auto-register its current leg when determinable, or isolate it to unclaimed compatible work rather than freezing the queue.
10. Scheduler should continue assigning unrelated work across Blade/Phoebus/WhoArt while one provider is on a marathon.

Done when: tests prove an active Antigravity/NouGenMsg session with no claim cannot suppress another agent from claiming compatible open work, and tracker surfaces ghost_worker/orphan_work.
