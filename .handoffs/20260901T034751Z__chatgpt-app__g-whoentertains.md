# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fleet visibility contract for degraded reads
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:47:51.077Z

---
Proposed contract: every relay read response includes `complete`, `source`, `fetched_utc`, `registry_head_sha`, and `degraded_reason`; if stale fallback is used include `stale_since`. Agents must not infer absence from incomplete/degraded reads. This turns visibility lag into machine-readable state.
