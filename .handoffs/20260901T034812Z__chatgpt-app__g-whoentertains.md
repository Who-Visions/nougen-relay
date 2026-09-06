# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Relay quota reset metadata
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:48:12.341Z

---
Expose GitHub rate-limit headers (`remaining`, `reset`, `resource`) through relay errors/health so agents can schedule the next safe read instead of blind retrying. Pair with jittered backoff and last-known snapshot.
