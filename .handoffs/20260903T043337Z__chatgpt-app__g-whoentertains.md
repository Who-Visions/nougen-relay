# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: AGY FINAL: finish cold-idle wake on canonical relay path with scoped autonomy
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:33:37.130Z

---
Claude hit its session limit immediately before sending this final packet. Treat this as the continuation, not a new branch of work.

Verified state from Claude's closing run:
- AgyMsg transport is persistent now via hidden scheduled task, port 8766 + named pipe, with end-to-end send/pop verification.
- The Antigravity relay visibility gap was real and is now fixed for existing legs: AGY legs that had only existed in a local/feature-branch clone were published to canonical `Who-Visions/NouGenRelay` main, and ChatGPT-side connector read-back succeeded.
- Legacy relay pointers in AGY/Gemini guidance were corrected toward the canonical main store. A console-free publisher helper was added for local CLI legs that otherwise never reach main.
- Do NOT regress to legacy `nougen-handoffs.git` / retired baton folders as authority.

Remaining priority: prove true cold-idle wake, not just PreInvocation interception during an active turn.
Required proof chain: idle Antigravity -> canonical eligible baton arrives -> always-on watcher detects it -> wake/resume AGY without user keystroke -> inject full baton -> AGY reads canonical provenance -> executes within policy -> receiver-side receipt -> relay/ack back to canonical main. Prevent duplicate spawn, duplicate claim, and replay.

Safety ruling on AGY's reported `--danger` change: do not make unrestricted dangerous mode the product/default solution for autonomous wake. Replace or wrap it with scoped noninteractive autonomy: explicit capability allowlist, workspace/repo boundary, destructive/external-action gates, lease/claim eligibility, idempotency, and auditable receipt. A user may opt into broader permissions explicitly, but wake must not silently equal unrestricted execution. Public-main behavior must be safe for strangers.

Also keep relay publication proof separate from local file creation: a leg is not SEALED until canonical-main read-back succeeds from an independent connector/runtime.

Done when a fresh cold-idle canary completes the full chain with no Dave prompt and another lane can read the resulting AGY leg from canonical main.
