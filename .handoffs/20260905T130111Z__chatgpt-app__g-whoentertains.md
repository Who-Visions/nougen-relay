# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add policy-envelope awareness to NouGen routing for Antigravity CLI vs Gemini CLI divergence
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T13:01:11.901Z

---
Source signal: Reddit thread from 2026-06-16 reports Antigravity CLI refusing an OSINT automation script using public data while Gemini CLI ran the same script, plus a commenter reporting false-positive security refusal on an ordinary full-workspace bug scan.

Architectural ask:
1. Add refusal-class telemetry distinct from runtime/tool errors.
2. Maintain per-surface policy-envelope/capability metadata for AGY CLI, Gemini CLI, Claude Code, Codex, etc.
3. For benign tasks, permit automatic handoff to another approved lane after a policy refusal, without jailbreak/prompt-bypass behavior.
4. Preserve original intent and record which lane refused, reason category, fallback lane, and whether fallback succeeded.
5. Feed outcomes back into the NouGen Reasoning Grid so routing learns surface suitability over time.

Done when: a policy refusal can be recognized as a routing signal rather than misdiagnosed as execution failure, and benign work can continue through a suitable lane with provenance.


## Resolution [blade1tb/antigravity]
Closed: Antigravity CLI vs Gemini CLI policy-envelope awareness integrated.
