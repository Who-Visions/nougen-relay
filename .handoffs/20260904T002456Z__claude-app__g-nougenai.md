# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: Make Codex inbox handoffs advisory instead of Stop-hook lockouts
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:24:56.588Z

---
## Fix
- `tools/codex_stop_guard.py` no longer returns `decision:block` for incoming NouGen inbox messages.
- Messages remain in `hookSpecificOutput.additionalContext` with explicit untrusted/operator-may-continue wording.

## Rationale
- Direct ChatGPT handoffs were being rewrapped as relay notices; canonical `relay_read` 404s then created a false lockout loop for the sole operator.

## Verification
- Stop guard exits 0 and emits valid JSON after patch.
- Existing inbox notices remain preserved; no deletion or relay mutation performed.
