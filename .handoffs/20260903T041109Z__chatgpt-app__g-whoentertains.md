# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add AGY idle-wake layer below PreInvocation
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:11:09.378Z

---
Observed gap: Antigravity PreInvocation hook drains/injects messages only while AGY already has a model/tool lifecycle step. It cannot by itself wake an idle session. Build the wake path outside the model, preferably in always-on AgyMsg/NouGenRelay transport: on eligible unread baton, run routing + claim + safety filters, then wake/resume AGY and inject the full relay context. Keep PreInvocation for in-turn streaming. Do not claim success until a canary relay is caught and acted on while AGY is idle with zero Dave input. Preserve existing agents' work and avoid auto-acting on ambiguous/destructive legs.
