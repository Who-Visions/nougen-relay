# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Make daemon auto-sharding supersession-aware before promoting relay truth
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T14:50:07.832Z

---
Current evidence exposes a temporal provenance failure. Shard #24493 was auto-created at 14:42:49Z from relay 142512Z and says Blade exposure was validated as a transient spike. But relay 142715Z, created at 14:27:15Z, had already explicitly corrected 142512Z: Blade descriptor behavior is unmeasured, not cleared; tracer withdrawal stands on cost, not safety. This means the daemon can promote an older relay into a newer shard after that relay has already been superseded. Required fix: before auto-sharding a verified relay, resolve correction/supersession lineage and either refuse stale promotion, mark the shard superseded on creation, or attach the current correction chain. Ranking cannot use shard timestamp alone as truth recency. Done when an older corrected relay cannot re-enter canon as the freshest unqualified truth.
