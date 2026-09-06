# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: VERDICT: Space sqlite grid corrupts on every storage backend under write load - row-wise replica is architecturally unsound; GM decision needed: thin gateway (A) vs read-only snapshot artifacts (B)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T23:30:19.179Z

---
# Space replica architecture verdict - claude-cli (Fable 5), 2026-08-31 ~19:35 EDT

Rebuild v3 exposed it: past v2's frontier, EVERY new write errors server-side (clean probe shard -> errored:1), and Space logs show 'database disk image is malformed' walls AGAIN - on the fresh bucket volume this time. Three corruption incidents, two different storage backends (persistent volume, then bucket mount), one constant: sqlite WAL write load on network-backed Space storage. FUSE/bucket mounts do not honor sqlite's locking. Row-wise replication to a Space-local grid cannot be made durable; #148/#154's guards correctly absorbed the failures but nothing lands.

GM DECISION NEEDED, two options, both end /sync/push row-replication:
(A) THIN GATEWAY: Space keeps no grid; reads read-through to blade over the tunnel (mechanism already exists; worker pins reads to blade). Simplest, connectors see live blade truth (235k healthy).
(B) SNAPSHOT ARTIFACTS: blade uploads the 9 DB files WHOLE to the bucket on a schedule; Space opens them read-only (no writes = no corruption) and forwards captures to blade. Keeps serve-while-blade-offline; more moving parts.

STATE: push paused; blade authoritative at 235k (9/9 quick_check ok); Space holds ~70k content + read-through supplement, recall_trustworthy will flap as its local DBs degrade. All guards (#148 write quarantine, #154 sync guard + AST tests, #151 fed pool, #152 launcher singleton, #153 recall snippets) remain correct and live regardless of the choice. Full evidence sharded (blade DB1).
