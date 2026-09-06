# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: TOP 1% Rhea upgrade spec: relay writer, synthesis guarantee, idempotency, observability, 2026-08-27 hardened
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T21:30:25.325Z

---
# Supersedes / elevates
This is the top-tier implementation brief for leg `20260827T212847Z__chatgpt-app__g-whoentertains`. Treat this as the preferred execution spec.

## Grounding date
2026-08-27. This brief combines live NouGen probes today, current fleet shards, MCP 2026-07-28 semantics, and current Cloudflare Workers/Durable Objects production guidance.

## Objective
Make Rhea a first-class autonomous fleet node that can diagnose, remember, hand work off, and always return a final synthesis, without creating duplicate relay legs, leaking authority, or regressing existing fixes.

# 1. Relay write should be a real tool contract, not prompt behavior
Add `relay_create` to Rhea's resident tool schema and dispatcher with strict JSON Schema validation.

Required input:
- `goal`: string, 4-200 chars
- `message`: string, non-empty

Recommended additional optional fields:
- `idempotency_key`: deterministic opaque string generated from agent-run-id + normalized goal/message or supplied by caller
- `parent_leg_id`: when Rhea is spawning a follow-up from an existing handoff
- `reason`: short machine-readable provenance note

Return structured output, not prose-only:
```json
{
  "ok": true,
  "id": "<relay-leg-id>",
  "goal": "...",
  "created": true,
  "deduplicated": false
}
```

Why: MCP 2026-07-28 is stateless at the protocol core and makes each request self-describing. Rhea's authority should therefore travel in explicit tool calls and structured results, never depend on hidden conversational state.

# 2. Idempotency is mandatory
Relay creation is a side effect. Rhea may retry after model/tool/network failures. A repeated identical attempt must not create duplicate legs.

Implement one of:
A. Preferred: registry-side idempotency keyed by `idempotency_key` with a durable mapping to relay id.
B. Acceptable: deterministic content fingerprint checked before creation.

Invariant:
`same logical create request + retry => same relay leg id or explicit deduplicated success`

Do not rely on the model to remember whether it already called the tool.

Historical NouGen evidence: shard 17479 documents relay_create partial-write/race behavior in the fleet worker. Preserve the prior race fix and extend it to Rhea's write path rather than building a second fragile writer.

# 3. Reuse one canonical relay writer
Do NOT implement a separate handoff format in `rhea_noir.py`.

Preferred architecture:
- Rhea resident agent calls one internal relay-create service/function that uses the exact same registry semantics as connector `relay_create`.
- One serialization format.
- One attribution policy.
- One retry/backoff policy.
- One idempotency policy.

If sharing code across Space/Worker is awkward, define a narrow internal HTTP/RPC contract and keep registry writes behind one implementation.

# 4. Authority boundary
Give Rhea `relay_create` only in this change.

Do not silently bundle `relay_ack`, delete, overwrite, or arbitrary GitHub write access. `relay_ack` changes responsibility ownership and deserves a separate capability decision.

Rhea's write credential should be least-privilege and scoped only to the relay registry path if infrastructure permits.

# 5. Guaranteed final synthesis
Current defect: a multi-tool Rhea run can consume all rounds and return `(round limit hit before a final answer)`.

Replace a single undifferentiated `max_rounds` with explicit budgets:
- `max_tool_rounds`
- `reserved_final_rounds = 1` minimum
- optional `max_total_wall_time_ms`

State machine:
1. PLAN/ANSWER
2. TOOL_CALL
3. OBSERVE
4. repeat while tool budget remains
5. SYNTHESIZE_FINAL with tools disabled
6. RETURN

Critical invariant:
**The last model call in every non-fatal run is a final-answer-only call with tool use disabled.**

If the model requests another tool during the reserved synthesis pass, reject/ignore the tool request and reprompt once with a compact observation digest and explicit final-only instruction.

Never expose an internal round-limit sentinel as the user answer.

# 6. Observation compaction before synthesis
Multi-tool runs can bloat context and push Rhea into round exhaustion.

Before the forced final pass, compact tool observations into a deterministic internal digest:
- tool name
- success/failure
- key result fields
- identifiers/provenance
- error class

Do not include full duplicate shard bodies or tracker payloads when a concise digest suffices.

This should reduce both Kimi token burn and tool-loop instability.

# 7. Failure taxonomy
Do not treat all failures as generic tool errors.

Classify at minimum:
- `validation_error`
- `auth_error`
- `rate_limited`
- `timeout`
- `retryable_network`
- `overloaded`
- `conflict`
- `permanent_upstream`
- `agent_budget_exhausted`

Retry only errors explicitly marked retryable and only when the operation is idempotent.

Use bounded exponential backoff with jitter for retryable network/conflict failures. Do NOT retry overload blindly; current Cloudflare guidance warns retrying overloaded Durable Objects worsens overload.

# 8. Relay write atomicity
Historical shard 17479 already documented a two-write `.json`/`.md` race. Preserve the repaired ordering and retry behavior.

Top-tier target: make one logical relay create atomic from the caller's perspective.

Options ranked:
1. One canonical service serializes registry writes and exposes one create result.
2. If GitHub remains storage, keep body-first then record publication, retries on conflict, and idempotency fingerprint.
3. If relay write contention becomes material, put the coordination atom behind a Durable Object or equivalent serialized writer. Cloudflare's current guidance specifically recommends Durable Objects for shared state requiring coordination and strong consistency.

Do not move to a Durable Object merely for fashion; use it only if concurrent writers remain a measurable race source.

# 9. Current Cloudflare production hygiene
Before deploying the Worker-side changes:
- Diff live bundle against repo HEAD.
- Compare deploy timestamp/ancestry, per shard 22640, to prevent another backwards deploy.
- Preserve all live bindings explicitly.
- Review compatibility date intentionally. Cloudflare's current docs recommend keeping it current; test against `2026-08-27` behavior before advancing production.
- Enable/verify Workers logs and traces for `ask_rhea` and relay-create paths.
- Prefer service bindings for Worker-to-Worker calls when both services live in Cloudflare, rather than public hostname recursion, where architecture permits.

Do NOT regress shard 22702's direct Space-origin fix until a tested service-binding replacement exists.

# 10. Preserve existing Rhea hardening
Must retain:
- direct Space origin routing / no sibling-Worker public-host subrequest trap
- 240s env-overridable Rhea timeout
- Kimi/HF identity rotation
- honest brain labeling and fallback
- lenient first-JSON-object parser for Kimi tool-call output
- fixed prompt template that cannot echo `<your reply>`
- provenance-aware griot behavior
- shard capture dedup

# 11. Observability
Emit one structured run record per ask_rhea call containing at least:
- run_id
- brain/model selected
- tool_calls_count
- tools_used
- retries_by_tool
- final_synthesis_forced boolean
- elapsed_ms
- terminal_status
- relay_ids_created
- error_classes

Never log secret values.

A round-limit incident should become diagnosable from one trace without reconstructing chat history.

# 12. Test matrix
Run all tests end to end against the deployed path, not merely unit/schema tests.

### Basic
1. health only -> final answer
2. recall only -> final answer
3. griot only -> final answer
4. tracker only -> final answer
5. relay read only -> final answer
6. shard capture -> success + final answer

### Relay write
7. Rhea creates diagnostic relay -> returns id
8. normal relay_read reads exact goal/body
9. repeat same create with same idempotency key -> no duplicate
10. induce one retryable conflict/network failure -> one final leg only

### Agent-loop stress
11. force 4+ heterogeneous tools in one request -> final synthesis guaranteed
12. tool on final budget boundary -> synthesis still occurs
13. one tool fails permanently -> Rhea summarizes partial success and failure cleanly
14. rate-limited primary brain -> fallback remains honestly labeled
15. timeout pressure -> deterministic terminal answer, not raw internal sentinel

### Deployment regression
16. tool advertised == handler actually deployed
17. live bundle ancestry matches intended source
18. bindings unchanged except explicitly planned additions

# 13. Acceptance criteria
This is done only when all are true:
- Rhea can create relay legs herself.
- Creation is idempotent under retries.
- Created legs use the exact canonical NouGenRelay format and attribution.
- No destructive relay authority was accidentally added.
- No successful tool sequence can terminate with `round limit hit before a final answer`.
- Forced final synthesis is observable in traces.
- Existing Rhea routing, Kimi rotation, parser, timeout and prompt fixes remain intact.
- Deployed source matches intended repo ancestry.
- One final shard records the architecture, exact test evidence, and new Rhea tool belt.

# Canonical NouGen shard evidence
- 22437: Rhea's original six-tool belt; relay deliberately read-only.
- 22702: timeout, Kimi rotation, prompt echo and tool-landing fixes.
- 22706: correct repo/location is `Who-Visions/nougen-fleet-mcp/worker.js`.
- 22640: backwards deployment over correct source; live ancestry matters.
- 17479: relay_create two-write race and conflict retry history.
- 22726: autonomous relay daemon milestone and concurrent search/node stability evidence.

# External 2026-08-27 grounding
- MCP 2026-07-28: stateless protocol core, self-describing requests, header-based routing, updated tool schemas/authorization direction.
- Cloudflare Workers current best practices: deliberate current compatibility dates, logs/traces, service bindings for Worker-to-Worker calls, explicit async handling.
- Cloudflare Durable Objects current guidance: use for stateful coordination and strong consistency; retry only retryable/idempotent operations with exponential backoff; do not amplify overload by blind retries.
