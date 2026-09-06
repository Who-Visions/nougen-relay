# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TODO 225258Z fully closed: quiet-box recall bench PASS - retrieve p95 3.86s, federated p95 5.69s, accuracy 1.0 both lanes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T03:35:34.498Z

---
# Quiet-box recall bench - claude-cli (Fable 5), 2026-08-30 ~22:20 ET

tools/recall_bench.py at main 4105142, box at 33% CPU / 46 python procs, grid 235k rows all-healthy post-recovery.

retrieve: p50 2.92s / p95 3.86s / mean 2.75s, accuracy 1.0 (canary top-1)
federated: p50 3.73s / p95 5.69s / mean 4.01s, accuracy 1.0
warmup (one-time vector cache load): 13.67s. Verdict: PASS under default budgets.

The earlier 11.4s retrieve outlier is CONFIRMED box contention, not code - same code, 66% lower p95 once duplicate daemons were culled. Both halves of TODO 20260830T225258Z are now done (#145 loud switch + this bench). Results sharded to the grid. Baseline stands: pre-#143 was 14-35s with a dead vector lane.
