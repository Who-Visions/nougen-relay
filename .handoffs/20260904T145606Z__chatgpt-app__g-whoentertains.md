# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS CODEX: 12-leg closure queue for relay debt and fleet hardening
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T14:56:06.913Z

---
Dave wants Phoebus Mac mini Codex fed a list of 10+ concrete open legs it can close. Treat this as an ordered closure queue. Before starting each item, check relay_claim_list and current correction lineage so stale legs are not resurrected.

1. Supersession-aware daemon auto-sharding: before promoting a relay into a daemon shard, detect later correction, withdrawal, amendment, or superseding relay. Mark stale lineage instead of minting newer-timestamp old truth.

2. True-origin / Message from Unknown chain: unify legacy sender/source parsing, preserve backwards compatibility, and emit non-optional per-session identity at source rather than node-only provenance.

3. Timeout failure taxonomy beyond PR #214: distinguish timeout, auth failure, downstream unavailable, local resource exhaustion, partial fanout, and unknown. Do not infer root cause merely from timeout.

4. Close the corrected Phoebus descriptor thread: encode the surviving truth only. Concurrent recall drives ~44 -> 202 -> 229 descriptors, then reclamation to ~46 within several minutes idle. Sustained bursts can hit EMFILE/503; not an unbounded leak. Mark superseded leak/not-leak relay legs stale where appropriate.

5. Add observation-window metadata to diagnostics: measurements that depend on time/window must carry the observed interval in structured output so 'flat for 120s' cannot silently become 'no decay'.

6. Add independent-measure cross-check hooks for resource diagnostics: for FD counting, require numeric FD rows and compare against max FD number / process RLIMIT. Reject or warn on proxy counts such as raw lsof line count.

7. Round Robin + Roll Call identity recovery: implement the standardized pattern from leg 135955Z so live sessions can announce who/where/provider/session and stale Unknown identities can be repaired without guessing.

8. Busy-pipe retry + persistent relay-live notifier propagation: take 135953Z and make retry/backoff and durable notifier behavior consistent across supported NouGen lanes. Verify no terminal-focus stealing or flashing foreground windows.

9. NouGenLine transport preflight: do not build the whole protocol yet. First codify the measured constraints into executable tests/spec checks: identity at emit, delivery-path-specific success, causal receipt binding, truthful entrypoint, failure taxonomy, break-glass queue semantics, and no single-node provenance dependency.

10. Provider continuity state model: encode provider quota/reset as lane state, not fleet state. Preserve resumable handoff metadata so Claude/Codex/Antigravity/local lanes can rotate without reconstructing context.

11. Quota/context telemetry schema: create a provider-neutral representation separating context used/capacity, quota state, reset time, confidence/source, and semantics_verified. Use the Sept 4 Claude proof clip as a fixture but do not hardcode Claude semantics.

12. Relay debt closer: after items above land, scan open relay legs for ones made obsolete by their fixes or by later corrections. Produce a closure report with: leg id, reason safe to close, superseding commit/test/relay, and any leg that must remain open. Do not ack/close ambiguous historical legs merely because they are old.

Execution rule: prefer small PRs or atomic commits, tests before closure claims, exact observed evidence, and no destructive cleanup of provenance. Done when each completed item has code/tests or an explicit verified closure artifact, and the final debt report names which historical legs can now be retired.
