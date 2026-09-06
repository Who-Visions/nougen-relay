# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Preserve machine independent continuity rule
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-26T14:54:27.881Z

---
Canonical fleet rule: durable context gets captured as a shard, active work gets handed off through relay, and any machine or lane should be able to resume from shard plus baton state without Dave reconstructing prior prompts. Treat this as the default continuity model for NouGen work. Done when future lanes can rehydrate scene and task state from the grid and relay alone.
