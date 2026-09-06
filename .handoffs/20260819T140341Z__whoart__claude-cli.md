# 🤝 Git Handoff — whoart / claude-cli

**Goal**: Gemini 2026 model catalogue routing audit
**Branch**: `main` @ `dd86bd7`
**Stack**: (undetected)
**When**: 2026-08-19T14:03:41.505397+00:00

---
Verified the operator-supplied catalogue against Google's official model page (updated 2026-08-14). Current Vertex lane already uses gemini-3.7-flash, gemini-3.5-flash-lite, and gemini-3.1-pro-preview behind explicit billed opt-in. Stale executable defaults remain in Python/TypeScript: GeminiClient list_models advertises 1.5 models and OpenRouter fallback uses shut-down gemini-2.0-flash-001. docs/local-worker names nonexistent gemini-3.5-pro. Model-registry mutation is paused pending explicit operator approval per NouGen gate; unrelated uncommitted mcp/catalogue work was preserved.
