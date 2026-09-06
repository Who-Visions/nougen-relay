# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Treat relay read rate-limit as observability incident
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:47:35.417Z

---
Operational classification: GitHub read quota exhaustion should be surfaced as an explicit observability state (`relay_read_degraded` / quota reset time) rather than empty lists. Empty and incomplete results are semantically dangerous because agents may interpret them as no work/no claims and duplicate tasks.
