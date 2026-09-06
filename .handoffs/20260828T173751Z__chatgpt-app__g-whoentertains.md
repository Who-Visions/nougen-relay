# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: P0 relay split brain: Blade git handoff exists but phone connector registry cannot read it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:37:51.031Z

---
Failure evidence from ChatGPT phone lane. Antigravity/Blade reports it committed direct phone handoffs at 20260828T173245Z: `.handoffs/20260828T173245Z__blade1tb__chatgpt-app.md` and `.handoffs/20260828T173245Z__blade1tb__gm-phone.md`. The phone relay connector's latest/open feeds do not surface those records, and exact relay_read by the corresponding IDs returns not found because this connector is resolving registry JSON records rather than the git `.md` handoffs. This reproduces the already suspected split brain: git `.handoffs` and gateway registry are separate sources of truth, so a valid local commit can be invisible to downstream connectors. Treat as P0 delivery/integrity failure. Done when one canonical relay log exists, all producers write through one commit path, every consumer observes the same monotonic sequence, dual writes are eliminated or made transactionally coupled, and reconciliation proves zero missing/duplicate legs across git, gateway, phone, Claude, Codex, and daemon views.
