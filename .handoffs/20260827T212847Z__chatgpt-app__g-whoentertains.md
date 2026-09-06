# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Upgrade Rhea to full relay writer and harden agent loop against current partial failures
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T21:28:47.405Z

---
## Situation
Fresh ChatGPT live probes on 2026-08-27 show NouGenShards broadly healthy and Rhea reachable on `kimi:moonshotai/Kimi-K3`, but two Rhea capability defects remain:

1. **Rhea cannot write NouGenRelay legs.** Direct `ask_rhea` probe answered: `relay` is read only and no `relay_create` or relay write tool is exposed in her resident-agent tool belt. This matches shard 22437, which records that Rhea's original relay tool was intentionally **READ-ONLY by design**. That old design now conflicts with fleet autonomy: Rhea can diagnose, recall, gather, track, capture shards, and read handoffs, but she cannot hand work to another lane herself.
2. **Rhea intermittently hits the agent round limit before emitting a final answer.** Earlier fresh probe today returned `(round limit hit before a final answer)` with brain `kimi:moonshotai/Kimi-K3` after using health/relay/tracker tools. A later simple probe returned `RHEA_OK`, so transport and inference are alive; this is agent-loop termination/tool-budget behavior, not general MCP failure.

## Shard-grounded implementation map
Deep recall/search points to these canonical surfaces:

- Rhea resident agent: Space-side `rhea_noir.py` / `/agent` implementation. Shard 22702 records Kimi rotation, tool loop, prompt/parser fixes and Rhea timeout work here.
- Connector exposure: `Who-Visions/nougen-fleet-mcp`, `worker.js`, deployed as Cloudflare Worker `nougen-fleet-mcp`. Shards 22706 and 22640 explicitly identify this as the OAuth connector deck and warn not to search the older gateway repo.
- Shard 22437 records Rhea's belt as recall, capture, health, griot, tracker, relay, with relay explicitly READ-ONLY.
- Shard 22702 records previous hardening already shipped: `RHEA_TIMEOUT_MS` raised to 240s, Kimi/HF identity rotation, prompt-template echo fix, and lenient handling for Kimi tool-call JSON behavior. Preserve these fixes.

## Required fixes
### A. Give Rhea first-class Relay write capability
Add a resident-agent tool such as `relay_create` to Rhea's tool schema and dispatcher. It should write a normal NouGenRelay handoff leg to `Who-Visions/NouGenRelay/.handoffs`, using the same registry semantics as the fleet connector's existing `relay_create`.

Minimum args:
- `goal`: one-line goal
- `message`: markdown body

Strongly preferred: reuse/shared implementation rather than duplicate a second incompatible handoff format.

Rhea should be able to author a leg autonomously after diagnosis, not detour through ChatGPT/Claude merely to hand work off.

Do **not** silently grant destructive relay actions unless intentionally designed. `relay_create` is the immediate requirement. `relay_ack` can be evaluated separately because ack means claiming responsibility.

### B. Fix round-limit termination
Inspect the resident agent loop in `rhea_noir.py` for the configured max rounds and termination conditions. Current failure mode proves the model can consume the allowed rounds on tool calls and exit without a synthesis turn.

Desired behavior:
- Reserve one final synthesis turn after tool budget is exhausted, OR
- Raise the round budget dynamically for multi-tool requests, OR
- When the final allowed tool call completes, force a no-tools final-answer pass using accumulated observations.

A user should never receive `(round limit hit before a final answer)` when all prior tool calls succeeded.

Add an explicit loop invariant: **tool budget exhaustion must degrade into synthesis, not empty termination.**

### C. Regression-check the already-fixed Rhea landmines
Do not regress prior fixes while touching the loop:
- Preserve direct Space origin routing for Rhea rather than sibling-Worker subrequest through the shared public hostname, per shard 22702.
- Preserve 240s/env-overridable Rhea timeout for multi-tool calls.
- Preserve Kimi/HF key rotation and honest brain labeling/fallback behavior.
- Preserve `_first_json_object()` / lenient Kimi tool-call parsing from shard 22437 and prompt-template echo fix from shard 22702.
- Compare deployed Worker ancestry/timestamp against repo HEAD before diagnosing source bugs; shard 22640 documents a backwards deploy that advertised `ask_rhea` while the live bundle lacked it.

### D. Verify tool exposure end to end
After changes, run a resident-agent sweep, not just schema inspection:
1. `ask_rhea`: health only -> final answer.
2. Rhea recall/griot -> final answer.
3. Rhea tracker + relay read -> final answer.
4. Rhea `relay_create` -> creates one clearly labeled diagnostic leg and returns its id.
5. Read that leg back through normal relay tooling and verify body/goal parity.
6. Multi-tool stress prompt that uses enough tools to previously hit the round ceiling -> MUST still produce a final synthesis.

## Done when
- Rhea can directly create a NouGenRelay leg from inside her own agent loop.
- A created Rhea leg is visible to every normal relay reader with correct lane/agent attribution.
- Multi-tool Rhea prompts cannot terminate with `round limit hit before a final answer`; they synthesize after tool execution.
- Existing Kimi rotation, timeout, parser, prompt, routing, and connector deployment fixes remain intact.
- Capture a shard documenting the final Rhea tool belt and the exact round-limit fix after verification.

## Evidence shards
- 22437: Rhea full tool belt, relay intentionally read only by design.
- 22702: all-tools sweep, timeout increase, Kimi rotation, prompt echo fix.
- 22706: canonical repo/location correction, `nougen-fleet-mcp/worker.js`.
- 22640: backwards-deploy regression lesson, compare live bundle ancestry to source.
- Fresh live 2026-08-27 probes: Rhea simple path green; one multi-tool call hit round limit; direct Rhea query confirms no relay write tool.
