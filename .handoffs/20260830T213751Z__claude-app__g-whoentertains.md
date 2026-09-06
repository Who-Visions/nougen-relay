# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Recall fixed local + gridion-tested + PR #143 up; deploy to node/Space pending
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T21:37:51.807Z

---
# Recall latency/accuracy fix - blade / claude-cli (Fable 5) 2026-08-30

PR: Who-Visions/NouGenShards#143 (branch claude-cli/recall-perf-fix, commit 9210876, rebased on 4b25bbc).

MEASURED root causes: (1) per-DB scans serial ~1.6s x 9; (2) scoped + whole-brain passes serial; (3) history.log_event one commit PER RESULT ROW (~360/recall); (4) vector lane permanent no-op - no caller ever embedded the query; naive awakening costs 27s (embedding column read = 10.7GB full-record scan); (5) federation RRF weighted 45 side vaults equal to core grid so filename rows beat real shards.

FIXES: parallel DB fan-out (NOUGEN_RETRIEVE_DB_WORKERS), concurrent passes, batched log_events + writer lock, query-time embedding (NOUGEN_QUERY_EMBED), per-DB embedding matrix cache with WAL-aware staleness + incremental append (NOUGEN_VECTOR_CACHE, ~800MB RSS), weighted RRF core 1.0 / side NOUGEN_FED_LANE_WEIGHT 0.35, lane deadline NOUGEN_RECALL_DEADLINE_S 20s.

NUMBERS (live grid): retrieve 14-35s -> 1.6-3.2s warm; federated 14-20s+aborts -> 5-9s; canary top-1; golden accuracy 0.8; tools/recall_bench.py = repeatable gridion gate.

NOT DEPLOYED: node service 8765 (PID 17020) runs old code - restart after merge; HF Space / failover worker unchanged - rebuild is GM-gated. shards_capture via connector returned {} again (known defect, leg 20260829T120001Z).

OBSERVED, LEFT ALONE: another agent switching this checkout's branches mid-session; untracked docs/nougen_sovereign_intelligence_doctrine.md uses a BANNED brand term in a PUBLIC repo - owner should rename.

Full suite running in isolated worktree; codex review in flight - verified findings become follow-ups on the PR branch.
