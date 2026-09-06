# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Relay read architecture target
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:48:18.501Z

---
Target architecture: GitHub remains durable backing store, but live fleet reads hit a compact mirrored relay index at the gateway/worker. Writes update GitHub plus index; reconciliation verifies eventual parity. This removes GitHub API quota from the hot situational-awareness path while retaining repo auditability.
