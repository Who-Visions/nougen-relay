# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: CONTINUE Codex baton: update stale NouGenMsg tests, then wire native Codex AgentControl/App Server transport
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:27:42.174Z

---
Dave's pasted Codex transcript ends at a rate-limit boundary after `go`. Continue from the exact landed state, not from architecture notes.

Verified current state:
1. Claude's authenticated NouGenMsg bridge is CLOSED/live: SessionStart registry hook, auth-line + type=user cc-msg wire, UserPromptSubmit drain, tests 4/4, live mid-turn receiver proof at 20:18 EDT. Latest Claude leg: `20260903T002114Z__claude-app__g-whoentertains`.
2. Codex independently ran the combined suite and found its two older low-level tests stale because they assert the superseded unauthenticated broadcast contract. Bridge tests themselves pass 4/4. Codex had started updating only those stale tests and explicitly was not touching Claude's bridge when the 5h limit hit.
3. The still-open architectural target is leg `20260903T001459Z__chatgpt-app__g-whoentertains`: NouGen should hook Codex's native internal cross-session/subagent messaging at AgentControl/App Server, not bolt relay polling onto Codex.

Execution order:
A. Re-run `tests/test_nougenmsg_bridge.py tests/test_nougenmsg.py` against the landed tree.
B. Update/remove only obsolete unauthenticated-broadcast assertions; preserve authenticated registry bridge semantics. Get the full focused suite green and report exact test counts.
C. Inspect the installed/current Codex source/runtime for the native AgentControl/App Server collaboration path and implement the thinnest NouGen adapter that targets real Codex ThreadId/agent identities, using native send_message/followup/send_input semantics where available. Relay remains durable cross-provider ledger; native Codex transport is the local fast path.
D. For long code, send references/manifests (repo, commit, path, hash, ranges) when shared storage exists; do not stuff huge code blobs into chat unless necessary.
E. Prove receiver-visible Codex-to-Codex or agent-to-agent delivery end to end, then relay exact evidence and shard the durable contract.

Do not race or rewrite the working Claude bridge. Do not declare Codex native transport complete from design notes alone.
