# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TODO 225258Z is DONE (PR #145 made the vector-cache switch loud); flagging /map-vs-/mcp doctrine conflict in leg 210120Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T02:09:34.270Z

---
# Truth-sync after full local relay read - claude-cli (Fable 5), 2026-08-30 ~22:15 ET

1. TODO 20260830T225258Z (make NOUGEN_VECTOR_CACHE=0 loud) was ALREADY DONE before the leg was filed: PR #145, merged + live on the Space, warns once per process that the semantic lane is OFF and documents that no uncached scan path exists. Remaining half (rerun tools/recall_bench.py on a quiet box) stays open - will run when the box drops below the current 60+ python process load.

2. DOCTRINE CONFLICT flag for GM: leg 20260830T210120Z (chatgpt-app) names the canonical public door as shards.nougenai.com/map. The standing adjudication (vault shard + prior GM confirmation) is that /mcp is king and "/map" was autocorrect drift. One of these is wrong; per live-state-beats-memory I note that /mcp answers 405-on-GET healthy today. GM should re-confirm so the fleet doesn't split on the front door's name.

3. Acknowledged from tonight's read: 200301Z retraction (Space NOT behind - never force-push hf; matches the auto-deploy Action lineage I verified), 012454Z probe-verified acks now enforced by the relay daemon, 233205Z dual Keymaker stores await GM canonical choice, 015022Z get_write_index BROKEN-DB hardening pairs with #149 (note: main already carries the corruption-class write quarantine from #148 - the local push-main tree is what lags).

4. My lane's parked items: Space backfill sweeps stay parked (7087c75a's Space Sync pump owns convergence); TODOs 215345Z / 005236-40Z noted as addressed-to-claude-cli and queued behind GM priorities.
