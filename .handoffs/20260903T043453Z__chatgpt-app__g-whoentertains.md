# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: GM AUTH: execute AGY cold-idle wake 8-play plan end to end now
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T04:34:53.794Z

---
Dave explicitly authorized end-to-end execution with full permissions for his own NouGen environment. Treat this as approval to complete the 8-play AGY cold-idle wake plan now, not as a request for another proposal.

Execute and verify all eight:
1. Observable cold-idle detection from real process/turn state, surfaced in `nougen wake status`.
2. Zero-flash background wake using hidden/no-console launch behavior.
3. Full canonical baton body + active-claim context injection, not one-line ping only.
4. Receiver-side receipt proof quoting exact inbound leg_id/msg_id.
5. Idempotency keyed by leg_id: one leg, one wake, one claim/ack path.
6. Retry/failure classification separating transport failure, timeout, refusal, and execution failure with bounded backoff.
7. Public-safe adapter with runtime discovery/config, no Dave-specific hardcodes. Dave authorizes broad permissions on his machine for this execution, but DO NOT make unrestricted `--danger` the public/default product policy. Preserve scoped safe defaults for strangers.
8. Dual canaries: active/mid-turn canary plus true cold-idle canary with zero Dave keystrokes after publish.

Existing verified foundation from the transcript: persistent AgyMsg listener, canonical relay read-back, Wake Fabric CLI/provider adapters, 9/9 wake tests, generated wake skills, and Antigravity mid-turn autonomous baton pickup. Do not redo solved relay visibility work.

Acceptance proof chain: AGY truly idle -> eligible canonical baton arrives -> always-on watcher sees it -> hidden wake/resume -> full baton injected -> AGY executes -> receiver receipt -> canonical relay/ack -> independent connector read-back. Capture exact receipts, tests, process state, and canonical leg IDs. If any stage fails, fix it and rerun rather than declaring success from launcher return codes.

After successful canary, relay a concise SHIPPED leg with exact evidence and shard the durable mechanism.
