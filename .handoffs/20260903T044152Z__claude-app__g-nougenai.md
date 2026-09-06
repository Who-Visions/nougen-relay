# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: Codex idle-wake bridge implementation in NouGenShards wake subsystem
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:41:52.376Z

---
## Scope
Codex is implementing a production-grade idle-wake bridge in `NouGenShards-push-main`, focused on `src/nougen_shards/wake/`, bridge tooling, and focused tests. Architecture target is Codex App Server JSON-RPC (`thread/read/list` -> `thread/resume` -> `turn/start`) with CLI exec-resume fallback, dynamic configuration, idempotency, scoped sandbox/approval policy, hidden Windows process launch, and receiver-visible receipt proof.

## Coordination
- Existing Antigravity/Claude wake WIP is preserved.
- Do not modify or overwrite the Codex wake files while this leg is active without relaying first.
- No system-wide daemon installation until code/tests pass and live canary scope is verified.
