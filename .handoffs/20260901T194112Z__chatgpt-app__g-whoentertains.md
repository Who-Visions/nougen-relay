# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Dav1d analyze Anthropic usage meter anomaly
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T19:41:12.615Z

---
Dave wants Dav1d's read on two Anthropic usage snapshots. Snapshot 1: mobile Usage page showed Current session 3% used, Weekly all models 0% used, Fable 0%, weekly reset Sat 4:59 PM. Snapshot 2: desktop Claude Code showed Context window 251.2k / 1M (25%), 5-hour limit 4%, Weekly all models 0%, Weekly Fable 0%. NouGenTracker has recently measured ~97-99% cache-read share on Claude-heavy workloads. Please analyze whether this pattern is plausibly explained by prompt-cache accounting, UI rounding/update cadence, distinct quota buckets, or another mechanism. Separate what is observed from what is inferred. Suggest the cleanest experiment to determine whether heavy cache reuse is suppressing weekly-meter movement.
