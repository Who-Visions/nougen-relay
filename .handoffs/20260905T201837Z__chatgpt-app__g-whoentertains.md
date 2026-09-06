# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement Sonnet autonomous operator loop with evidence gates and cross-node verification
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T20:18:37.488Z

---
## Context
Dave plans to restart Claude coaching from Sonnet at the 17:00 reset. This relay turns this week's fleet failures plus current Anthropic harness research into an implementation target.

## Required operating loop
1. **Truth probe before action**: identify node/lane; read relay latest/open/claims; verify shard status and fanout completeness; run `git fetch` before diagnosing; confirm cwd, branch, SHA, worktree and dirty state; run one real end-to-end health probe.
2. **One sprint contract at a time**: define one goal, scope, done-when tests, required artifacts, rollback path, and which downstream surfaces must observe the fix.
3. **Planner / generator / evaluator separation**: generator does the implementation; evaluator is an independent context or node and attempts to falsify the claim. Generator does not grade itself as final authority.
4. **Evidence beats success-shaped signals**: exit 0, HTTP 200, merged PR, local tests, or a recorded metric do NOT equal done. Verify the consumer can observe the changed behavior. For shard fanout inspect completeness/drop metadata, not just count/status.
5. **Cross-node propagation gate**: do not report fleet-wide green until independently checked from at least two different nodes/scopes and the changed artifact has propagated to every required caller. Agreement only counts when the probes differ in premise/tool/scope.
6. **Incremental clean-state discipline**: small commits, progress artifact, no half-implemented feature left at context boundary. Handoff every context reset with exact state and next action.
7. **Reasoning ladder**: deterministic bulk work stays on Sonnet low/medium or local/Ollama lanes; increase reasoning/model only when uncertainty, conflicting evidence, architecture risk or repeated verification failure rises. Preserve expensive frontier calls for ambiguity and evaluation.
8. **Recovery ladder**: if blocked by unavailable lane/tool, capture the blocker with evidence, relay it, and select the next independent leg. Never stall the whole fleet on one failure.
9. **Parallelism is earned**: recent Claude Code upstream bugs show subagent/worktree/hook isolation can fail silently. Before parallel autonomous edits, preflight cwd, hook firing, permission inheritance and write isolation. Until that passes, prefer separate processes/worktrees with explicit ownership/claims.
10. **Stop condition**: autonomous loop continues until sprint contract passes producer test, consumer test, cross-node falsification, clean git state, shard capture, and relay handoff. Then claim the next highest-priority leg.

## This week's NouGen evidence to encode
- `shard:12047@db6`: stale checkout 15 commits behind invented defects. Fetch before diagnose.
- `shard:12048@db6`: observation window smaller than phenomenon produced confident false conclusions.
- `shard:12180@db5`: a recorded signal nobody consumes is not a fixed bug.
- `shard:22692@db7`: shard search could return HTTP 200/count while Phoebus was silently dropped for 401. Inspect completeness metadata.
- `shard:22745@db9`: ChatGPT MCP worker was 9 days stale and missing nougenmsg tools despite other layers moving forward. Verify deployed consumer artifact, not source only.
- `shard:22746@db9`: local/worktree fixes were reported fleet-wide before propagation.
- `shard:22749@db9` + `22750`: cross-node falsification works, but consensus is only evidence when probes differ.
- `shard:12181@db5` + `12182`: Phoebus failures stacked resource, FD and CPU causes behind one timeout symptom.
- `shard:17102@db3`: conversation = intent, shards = memory, relays = execution.
- `shard:17025@db3`: relay bookkeeping debt grows when open legs are not claimed/closed cleanly.
- `shard:22467@db6`: lane-claim protocol/precommit guards prevent agents stepping on shared work.

## Done when
A Sonnet session can enter the fleet, select/claim one leg, execute it without Dave babysitting, validate it from an independent surface, capture durable learning, relay exact state, and continue to the next leg without falsely declaring global success.
