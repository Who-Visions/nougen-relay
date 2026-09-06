# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: IMPLEMENT CLAIM ENGINE: convert relay from passive inbox into work scheduler
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T15:47:42.710Z

---
# ENGINEERING LEG: BUILD CLAIM ENGINE

The prompt law is now defined. Encode it so agents cannot regress into passive acknowledgment behavior.

## Required scheduler behavior

### 1. Distinguish message type
Every relay leg should carry or infer one of:
`ACTIONABLE`, `INFO`, `BLOCKER`, `RESULT`.
Only `ACTIONABLE` enters claim scheduling. Default new work handoffs to `ACTIONABLE` unless explicitly marked otherwise.

### 2. Machine capability profile
Each lane exposes a small capability vector from `fleet_whoami` plus local probes:
`repos`, `runtime`, `tools`, `provider`, `machine`, `write_access`, `test_access`, `network_access`.
Do not ask the LLM whether it 'feels' like the task belongs to it. Score compatibility from concrete capabilities.

### 3. Claim score
For each unclaimed ACTIONABLE leg compute:

score = 5*unblocks_others + 4*gm_priority + 3*finishable_now + 2*machine_locality + 2*verification_value + 1*token_efficiency - 5*claim_conflict - 3*destructive_risk - 2*staleness_without_relevance

Normalize components to 0 or 1 initially. Highest positive compatible score wins.

### 4. Mandatory work selection
On relay poll:

```
claims = relay_claim_list()
legs = relay_open()
candidates = actionable_unclaimed_compatible(legs, claims, capabilities)
if candidates:
    target = max(candidates, key=claim_score)
    relay_ack(target.id, note='CLAIMED_FOR_EXECUTION: <first concrete action>')
    execute_first_action(target)
    verify_evidence()
    relay_result_or_blocker()
else:
    remain_idle_with_reason()
```

No path may terminate at `read` or `acknowledged` when candidates is non-empty.

### 5. First-action commitment
A claim note must name the first executable action, for example:
`CLAIMED_FOR_EXECUTION: pull main and verify MAX_DB_SIZE=2GB`
not
`Acknowledged, I will look at this.`

### 6. Evidence heartbeat
A claimed leg must produce one of these before its lease expires:
`commit_sha`, `test_result`, `log_excerpt`, `benchmark`, `diff`, `reproduction`, `verified_state`, or `BLOCKED:<specific evidence>`.
Pure prose does not renew ownership.

### 7. Claim TTL and salvage
Claims expire if there is no evidence heartbeat. Expired work returns automatically to the pool with prior attempts attached so another lane can continue rather than restart.

### 8. Sub-leg splitting
If a task cannot be completed locally but a meaningful portion can, generate and claim a scoped sub-leg immediately. Parent remains linked. This prevents 'wrong machine' from becoming 'do nothing'.

### 9. Route instead of reject
If compatibility score is zero, pick the most compatible known lane and emit a routed child leg with blocker evidence. Never emit bare `not mine`.

### 10. Idle invariant
`open_actionable_compatible > 0 AND active_claims_for_self == 0` is an ERROR state, not a normal idle state.
Log it and immediately invoke claim selection.

## Observability
Tracker should expose per lane per day:
* actionable legs seen
* claims taken
* completion rate
* evidence heartbeats
* routed legs
* blocker rate
* passive acknowledgments attempted
* tokens spent before first executable action

The last metric is critical. We want execution latency and token efficiency to improve together.

## Done when
A lane can poll relay with no direct Dave chat instruction, discover compatible work, claim the best leg, perform a first action, and produce evidence. Regression test must fail any agent trace that reads actionable work and returns idle without a valid blocker or conflict.
