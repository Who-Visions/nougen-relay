# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build NRG uncertainty driven reasoning ladder across every provider and model
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T22:05:12.776Z

---
# NouGen NRG: uncertainty driven reasoning governor

Directive from Dave, 2026-09-04: reasoning must rise with uncertainty across every model and every frontier provider. The stadium already supplies context, precedent, repo structure, tests, shards, relays, and boundaries, so model prestige and reasoning effort must be decoupled.

## Core law

DO NOT route by importance alone. Route on two independent axes:

1. capability demand: how strong a model is needed for the task class, context width, tool complexity, multimodality, and cross system scope
2. uncertainty demand: how much reasoning effort is needed given ambiguity, novelty, contradictions, unknown failure cause, observability gaps, and freshness

This permits Opus or Fable at low effort for hard but well specified stadium work, and permits a cheaper balanced model at high effort when the task is smaller but genuinely ambiguous.

## Evidence before intelligence

Before raising effort, determine whether uncertainty is informational or inferential. If the missing answer can be obtained by git fetch, shard recall, tests, logs, source read, tracker state, health probe, or live provider state, fetch that evidence first. Do not spend max reasoning to hallucinate around stale state. Today's fleet doctrine already proved the rule: stale checkouts and short observation windows create confident false diagnoses.

## Canonical task vector

For every task construct:

A ambiguity 0..1
N novelty versus solved shards or prior legs 0..1
C contradiction density 0..1
F unknown failure cause 0..1
D dependency unknownness 0..1
O observability gap 0..1
X freshness gap 0..1
S stadium depth 0..1, where 1 means repo plus acceptance tests plus precedent plus current evidence plus known boundaries
B blast radius 0..1
I irreversibility 0..1
Q security, secret, data integrity sensitivity 0..1
P production exposure 0..1

Raw epistemic uncertainty:
U0 = .23A + .18N + .18C + .16F + .10D + .08O + .07X

Stadium adjusted uncertainty:
U = clamp(max(U0 - .30S, .70C, .65F), 0, 1)

Consequence risk:
R = .35B + .25I + .20Q + .20P

Canonical reasoning demand:
E = max(U, .70R)

Important: stadium context discounts ambiguity, novelty, and dependency search cost, but it must never erase live contradictions, unexplained failures, security boundaries, destructive operations, or production blast radius.

## Reasoning ladder

R0 E < .12: none or minimal. Deterministic edits, formatting, known migrations, test reruns, summaries, mechanical code changes.
R1 .12 to .28: low. Normal stadium implementation with clear acceptance criteria.
R2 .28 to .45: medium. Multi file work, moderate design choices, unfamiliar but bounded code.
R3 .45 to .62: high. Root cause analysis, nontrivial integration, conflicting tests, cross service changes.
R4 .62 to .80: xhigh where supported, otherwise next supported level upward. Architecture, security boundaries, persistent contradictions, novel failures.
R5 >= .80: max or extreme where supported. Frontier uncertainty, novel architecture with high blast radius, unresolved contradiction after evidence gathering.
R6 council: not simply more tokens. Spawn independent diagnoses on two provider families, then arbitrate with the strongest appropriate model. Use only when R5 remains unresolved or evidence is genuinely contradictory.

Provider adapter rule: map canonical effort to the nearest SUPPORTED level AT OR ABOVE the requested rung. Never silently map downward. If a model cannot support the requested effort or tool capability, either move to another model in the same provider or another provider.

## Capability ladder, separate from effort

C0 local bulk: Ollama and open weights for extraction, formatting, classification, summaries, grep triage, repetitive transformations.
C1 fast frontier: routine code, simple tool work, bounded fixes.
C2 balanced frontier: default production coding and review.
C3 flagship: deep codebase analysis, architecture, long context, complex tool loops.
C4 strongest or multi agent: only when capability itself, not just uncertainty, demands it.

The router chooses a tuple (provider, model, effort), not just a model.

## Provider capability registry

Maintain a live registry per model:
provider, model id, capability tier, supported effort values, context limit, tool support, multimodal support, coding score, latency EMA, success EMA, retry EMA, quota burn EMA, cache efficiency, current quota pressure, rate limit pressure, known task affinities, freshness timestamp.

Do not hardcode effort semantics forever. Probe or refresh capability metadata after provider/model updates.

Current adapter examples verified from provider docs 2026-09-04:
OpenAI GPT 5.6 family supports none, low, medium, high, xhigh, max.
Anthropic current adaptive thinking uses effort; Opus 5 supports low, medium, high, xhigh, max; Fable 5 adaptive thinking is always on. Sonnet 5 uses adaptive thinking and effort.
Google Gemini 3 family uses thinking_level, generally minimal/low/medium/high depending model. OpenAI compatible reasoning_effort maps to Gemini thinking levels.
Kimi K3 supports low/high/max; medium maps upward to high, xhigh/max map to max. K3 Cluster is a separate scale lever for large parallel work.
xAI Grok 4.6 supports low/medium/high/xhigh, reasoning cannot be disabled.
Hugging Face Responses API exposes reasoning effort low/medium/high on models that support it and can route by provider.
OpenRouter and other gateways must be treated as transport plus model capability lookup. Pass native effort only when the selected upstream model advertises it. Otherwise adapt explicitly.

## Runtime escalation rules

A hard contradiction raises at least one rung immediately.
A second failure with the SAME signature may not simply repeat the same route. Escalate effort, change model, or gather missing evidence.
An unknown or stale source should trigger retrieval before reasoning escalation.
Auth, secrets, destructive database changes, schema migration, deployment routing, and cross node trust changes impose a minimum risk floor even when the implementation is familiar.
More than two machines, repos, or providers raises coupling and can force at least R2 or R3 depending observability.
A passing acceptance test lowers uncertainty, but descent requires two clean evidence cycles. One contradiction can raise immediately. This hysteresis prevents effort flapping.
If progress is monotonic and the last two actions verified cleanly, step effort down one rung for continuation work.
Do not keep the architect at max while workers execute a proven plan. One high reasoning scout can produce the plan, many low reasoning workers can execute it, and a medium or high validator can verify independently.

## Constrained learning router

Above deterministic safety and capability floors, learn which route is cheapest for each task class with a contextual bandit.

Candidate action = (provider, model, effort).
Reject any action that lacks required context, tools, modality, effort floor, or trust boundary.
For allowed actions estimate P(verified success) from tracker plus relay outcomes.
Choose the lowest expected quota burn route whose success probability clears the target threshold, initially 0.85 for routine work and 0.95 for high consequence work.

Suggested reward:
+3 verified completion
+1 no retry
+1 clean independent validation
minus quota burn weight
minus latency weight
minus retry penalty
minus rollback penalty
large penalty for confident unverified claim or false completion

Primary optimization metric: verified work completed per quota percentage consumed, segmented by task class, model, effort, and provider.

## Routing pseudocode

normalize task -> gather evidence -> compute capability demand -> compute U/R/E -> set minimum effort and capability -> enumerate provider/model/effort candidates -> remove incompatible candidates -> apply current quota and latency pressure -> choose cheapest candidate above predicted success threshold -> execute -> verify -> update uncertainty and bandit statistics -> descend after two clean cycles or ascend on contradiction/failure -> invoke cross provider council only at persistent R5.

## Stadium meaning

The stadium is not merely context. It is a reduction in entropy. Shards, relays, tests, current source, known architecture, prior fixes, naming conventions, and acceptance criteria convert open world search into bounded execution. NRG should quantify that reduction and cash it out as lower reasoning spend.

## Implementation targets

Likely modules: tools/reasoning_governor.py, provider capability registry, tracker outcome join, relay outcome hooks, per provider effort adapters, CLI status showing chosen tuple and why, and an audit record containing the feature vector, chosen rung, provider/model/effort, verification outcome, quota burn, and escalation/deescalation reason.

Done when: the same task can start low inside a deeply grounded stadium, climb automatically on contradiction or unknown failure, cross provider only when needed, fall back after verification, and learn over time which model plus effort delivers the most verified work per quota unit.
