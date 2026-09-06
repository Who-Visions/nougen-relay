# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: HADOUKEN FORWARD: bake token-to-action efficiency math into Tracker + Claim Engine
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T15:50:57.049Z

---
# 🥋 HADOUKEN — Tracker Execution Economics

This relay is AUTHORIZED WORK INVENTORY under Fleet Execution Law. Do not merely acknowledge it.

## Objective
Instrument NouGen Tracker + relay claim lifecycle so every machine/agent can be scored on how many tokens and how much elapsed time it burns BEFORE producing its first executable action and first verified artifact.

## Required event model
For every relay leg / claim, persist timestamps and token counters for:

1. `leg_seen_at`
2. `claim_at`
3. `first_action_at`
4. `first_evidence_at`
5. `complete_at`

And token snapshots:

1. `tokens_at_seen`
2. `tokens_at_claim`
3. `tokens_at_first_action`
4. `tokens_at_first_evidence`
5. `tokens_at_complete`

Track exact tokens where provider telemetry permits; keep estimated values explicitly marked when exact telemetry is unavailable.

## Core math

### Token To Action
`TTA_tokens = tokens_at_first_action - tokens_at_seen`

### Claim To Action
`CTA_tokens = tokens_at_first_action - tokens_at_claim`

### Time To Action
`TTA_seconds = first_action_at - leg_seen_at`

### Time Claim To Action
`CTA_seconds = first_action_at - claim_at`

### Token To Evidence
`TTE_tokens = tokens_at_first_evidence - tokens_at_seen`

### Execution Tokens
`execution_tokens = tokens_at_complete - tokens_at_first_action`

### Narration / Coordination Tax
`coordination_tax_tokens = max(0, tokens_at_first_action - tokens_at_seen)`

### Coordination Tax Ratio
`coordination_tax_ratio = coordination_tax_tokens / max(1, tokens_at_complete - tokens_at_seen)`

### Evidence Yield
`evidence_yield = verified_artifact_count / max(1, total_tokens_spent_on_leg / 1000)`

### Productive Token Ratio
`productive_token_ratio = execution_tokens / max(1, tokens_at_complete - tokens_at_seen)`

## Idle fault
If compatible open work exists AND active_claims == 0 for that agent/machine, accumulate:

`idle_with_work_seconds`

This is not a moral score. It is scheduler telemetry. It should feed routing so agents that reliably begin useful work quickly become more likely to receive compatible legs.

## Anti-gaming rules

* Reading / summarizing / acknowledging a relay does NOT count as first action.
* `first_action_at` requires a machine-verifiable side effect or executable operation: command launched, code/file edit, test run, branch created, issue/PR action, API mutation, shard capture, relay routing with named owner, or equivalent concrete operation.
* `first_evidence_at` requires an artifact such as commit SHA, diff, test output, log, benchmark, reproduced failure, verified state, PR/issue URL/id, or stored shard/relay identifier.
* Self-reported prose alone never increments evidence count.
* Failed executable attempts DO count as action, but evidence must record failure output honestly.
* Do not reward agents for generating tiny meaningless actions. Evidence quality must remain separate from speed.

## Scheduler use
Do NOT create a simplistic lowest-token winner. Feed efficiency into the existing claim score as one bounded factor.

Suggested normalized component:

`execution_efficiency = clamp(0, 1, 1 - normalized_coordination_tax_ratio)`

Then add at most +2 scheduler points for strong historical execution efficiency. Capability, locality, unblock value, safety, and claim conflicts remain more important.

## Rollups
Tracker should expose per agent, machine, provider, model, day, and rolling 7 / 30 day:

* median TTA_tokens
* p90 TTA_tokens
* median TTA_seconds
* p90 TTA_seconds
* median coordination_tax_ratio
* productive_token_ratio
* evidence_yield
* idle_with_work_seconds
* claimed legs
* completed legs
* blocked legs
* abandoned / expired claims

Prefer medians + p90 over averages so one giant job does not distort the fleet.

## Done when
1. Schema + migration landed.
2. Claim lifecycle emits all required timestamps and counters.
3. Tracker daily aggregation includes the new metrics.
4. Tests prove acknowledgment alone cannot satisfy `first_action_at`.
5. Tests prove duplicate claims do not double-count tokens.
6. At least one real fleet relay leg produces a complete observed lifecycle from seen → claim → action → evidence → completion.
7. Relay back exact commit SHA(s), tests, sample metric output, and any telemetry blind spots.

## Routing
Phoebus currently owns the Claim Engine build. Extend that work rather than duplicate it. If Tracker repo changes belong on another machine, split that concrete sub-leg to the best compatible node and continue the scheduler half immediately.

NO ACK-ONLY TERMINAL STATE. CLAIM, SPLIT, EXECUTE, VERIFY, OR PROVE BLOCKER.
