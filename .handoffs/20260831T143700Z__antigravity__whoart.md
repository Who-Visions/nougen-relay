# 🤝 Git Handoff — antigravity / whoart

**Goal**: Integrated universal live-ping bridges across Antigravity, Codex, Claude Code, and Ollama
**Branch**: `main`
**When**: 2026-08-31T14:37:00.000Z

---

## Live Ping Surfaces

1. **Claude Code:** Local and remote Named Pipes (`\\.\pipe\LOCAL\cc-msg-*`) & UDS.
2. **Antigravity IDE:** `~/.gemini/config/inbox/` event drops and active lifecycle hooks.
3. **Codex:** `~/.codex/inbox/` event drops and relay triggers.
4. **Ollama GPU:** Sub-300ms slot inference and model wake pings on port `:11434`.
