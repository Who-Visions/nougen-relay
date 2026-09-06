# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: HADOUKEN JARVIS CONTROL PLANE: implement adaptive routing, lease claims, quota shadow pricing, checkpoint migration, and evidence-gated completion
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T16:22:44.265Z

---
# NOUGEN JARVIS CONTROL PLANE v0.1
## Long-form algorithm, cross-referenced against frontier agent engineering and 2026 routing research

**Date researched:** 2026-09-06
**Why now:** Dave's 40.5+ hour Antigravity marathon proved the autonomy loop works at real scale: 7,816 logged steps, 3,606 model invocations, 3,130 tool calls, 40 user messages, and 3.428792775B context tokens moved with 99.96% cache hit. The next problem is NOT reducing autonomy. It is turning autonomy into governed compute: the system must decide who should work, how much reasoning to spend, when to escalate, when to de-escalate, when to checkpoint/migrate, and how to preserve provider quota without reverting to passive chat behavior.

This specification fuses existing NouGen components: **Claim Engine + NouGen Reasoning Grid + NouGenTracker + NouGen Fuse + local Kaedra + relay + shards** into a single adaptive control plane.

---

# 0. NORTH STAR

The optimization target is not minimum tokens. It is:

`MAX verified_progress / constrained_compute`

subject to:

1. user intent remains the authority,
2. no actionable relay is left idle merely because Dave did not repeat it in a lane's chat,
3. active work reaches a recoverable checkpoint before quota exhaustion,
4. expensive frontier reasoning is spent only where its marginal value exceeds cheaper alternatives,
5. every completed task has evidence,
6. every long-running task is resumable by another lane without reconstructing history from scratch.

A 99.96% cache hit ratio is NOT by itself an efficiency score. The marathon proves that cache can make giant contexts cheap relative to cold input while still producing enormous quota activity. Therefore Tracker must separate **cache efficiency** from **work efficiency**.

---

# 1. RELAY CLAIM STATE MACHINE

Current law already established in shard 29168@db8: an open actionable relay leg authorizes a capable lane to advance it. Reading or acknowledging is not a terminal state.

Formal state machine:

`OPEN -> ELIGIBLE -> CLAIMED -> EXECUTING -> VERIFYING -> COMPLETE`

Alternative exits:

`OPEN/ELIGIBLE -> SPLIT`
`OPEN/ELIGIBLE -> BLOCKED(reason,evidence)`
`CLAIMED/EXECUTING -> CHECKPOINTED -> MIGRATABLE`
`EXECUTING/VERIFYING -> RETRY`
`RETRY -> ESCALATE`
`CLAIMED -> LEASE_EXPIRED -> OPEN`

**Critical rule:** merely having a session/process alive does not reserve relay inventory. Ownership exists only when an explicit claim lease exists.

Every lane that inspects an actionable open leg must produce one of four machine-readable outcomes within that inspection cycle:

* `CLAIM`
* `SPLIT`
* `BLOCK(reason)`
* `PASS(reason)`

"I read this" and "not addressed directly to me" are invalid outcomes.

## Lease semantics

Borrow the mature distributed-systems pattern used by Kubernetes Leases:

`claim = {task_id, holder_identity, acquire_time, renew_time, ttl, capability_hash, checkpoint_ref}`

Use optimistic concurrency / compare-and-swap so only one owner wins. Renew during productive work. If renewals stop, lease expires and the task returns to OPEN. A graceful owner can release early after checkpointing.

Dynamic lease duration should be based on the p90 duration of an atomic work unit for that task class rather than a fixed magic number.

This directly eliminates ghost workers and zombie ownership.

---

# 2. CLAIM SCORING: WHO SHOULD TAKE THE BATON?

For each eligible lane `a` and task `t`, compute:

`ClaimScore(a,t) = + capability_fit + context_locality + cache_residency + historical_success + tool_locality + quota_headroom + dependency_unlock_value + age_fairness - expected_cost - queue_delay - merge_conflict_risk - blast_radius_mismatch`

All terms normalized 0..1 and learned from Tracker outcomes over time.

Suggested first-pass weights:

* capability fit: 0.22
* context/cache locality: 0.14
* historical success on task class: 0.14
* quota headroom: 0.14
* dependency unlock value: 0.12
* tool/data locality: 0.08
* age fairness: 0.06
* penalties split across expected cost, queue delay, conflict risk, and risk mismatch.

Do not permanently hard-code these weights. Bootstrap with them, then learn them from completed legs.

Starvation prevention: add an increasing age bonus, but cap it so ancient low-value work cannot permanently dominate critical dependencies.

---

# 3. MODEL + REASONING + OUTPUT ROUTER

The Reasoning Grid should choose a tuple, not merely a model:

`route = (lane, model, reasoning_effort, context_budget, output_budget, tool_strategy)`

For each candidate route `r`:

`Utility(r,t) = P_success(r,t) * Value(t) - lambda_q * QuotaCost(r) - lambda_$ * DollarCost(r) - lambda_l * Latency(r) - lambda_f * FailureRisk(r) - lambda_c * ContextPollution(r)`

Choose the highest utility route that satisfies risk and deadline constraints.

This is the core top-tier upgrade: **reasoning effort becomes a priced resource, not a personality setting.**

## Execution tiers

**Tier 0: deterministic execution**
Use shell, grep, static analysis, tests, git, structured queries, and direct APIs when an LLM is unnecessary. Never spend frontier inference to count, diff, grep, parse JSON, or verify a deterministic condition that code can prove.

**Tier 1: local resident intelligence**
Kaedra / Gemma on Phoebus for summarization, relay triage, shard distillation, repetitive repair loops, routine transformations, test-log interpretation, and low-novelty edits. This is the default long-loop furnace.

**Tier 2: cheap/fast cloud intelligence**
Use for moderate ambiguity, broader context, or when local quality falls below threshold but the task does not justify frontier cost.

**Tier 3: frontier specialist**
Codex, Claude, Gemini high-reasoning lanes for novel architecture, difficult debugging, multi-file refactors, unresolved contradictions, complex test failures, or high-value dependency unlocks.

**Tier 4: adversarial / multi-model review**
Only when uncertainty and consequence are both high. Do not committee-vote routine work. Multiple expensive models are a surgical instrument, not the default.

---

# 4. UNCERTAINTY-GATED ESCALATION

Compute a live uncertainty score:

`U = 0.24*novelty + 0.20*ambiguity + 0.18*failure_streak + 0.14*test_disagreement + 0.10*dependency_unknown + 0.08*cross_model_disagreement + 0.06*risk`

Possible bootstrap thresholds:

* `U < .25`: deterministic/local, low reasoning
* `.25 <= U < .55`: local/cheap cloud, medium reasoning
* `.55 <= U < .80`: frontier, high reasoning
* `U >= .80`: frontier + verifier or adversarial review

Escalation triggers also fire immediately when:

* same atomic test fails after 2 materially different repair attempts,
* expected output contradicts live tool evidence,
* a migration/merge touches a high-centrality subsystem,
* failure could destroy data or break production,
* estimated success probability falls below the task's required confidence.

**De-escalate immediately after the hard part is solved.** Frontier models should discover the path, not necessarily walk every repetitive meter of it.

This mirrors Anthropic's 2026 Claude Code auto-mode design pattern: a cheap first-stage filter handles the common case, while expensive reasoning activates only for flagged cases.

---

# 5. QUOTA GOVERNOR: SHADOW PRICE COMPUTE

For each provider `p`, maintain:

`remaining_quota[p]`
`reset_eta[p]`
`reserve[p]`
`EWMA_burn_rate[p]`
`estimated_atomic_cost[p,t]`

Compute sustainable burn:

`sustainable_rate = (remaining_quota - reserve) / time_to_reset`

Compute pressure:

`pressure = EWMA_burn_rate / sustainable_rate`

Interpretation:

* pressure < 0.70: green, route by quality/latency
* 0.70 to 1.00: yellow, bias repetitive work local
* 1.00 to 1.35: orange, frontier only where predicted quality premium is meaningful
* >1.35: red, do not START new noncritical frontier atomic units; checkpoint/migrate to local or another provider

**Do not kill a productive frontier task mid-transaction merely because pressure crossed a threshold.** Predict whether its current atomic unit can finish inside reserve. If yes, finish and checkpoint. If no, checkpoint immediately and migrate.

Runway:

`runway_seconds = remaining_quota / max(EWMA_burn_rate, epsilon)`

Before starting each atomic unit:

`if predicted_completion_time + safety_margin > runway_seconds: migrate_or_defer()`

This prevents the exact failure mode where Codex/Claude burns into a quota wall while a repo is half-edited.

---

# 6. LEARN THE REAL QUOTA FUNCTION, DO NOT ASSUME TOKEN PRICE == QUOTA PRICE

Tracker must maintain three different ledgers:

1. **raw activity**: input + output + cache read + cache creation + reasoning
2. **billing-equivalent activity**: provider price-weighted
3. **quota-equivalent activity**: empirically learned from actual meter depletion

Fit provider-specific coefficients from meter snapshots:

`meter_delta ~= a_in*input + a_out*output + a_cr*cache_read + a_cc*cache_create + a_reason*reasoning + a_calls*invocations + a_runtime*seconds`

Use non-negative regression and update as new observations arrive.

Why this matters: the 40.5h Antigravity session had only ~1.35M fresh input tokens but ~3.427B cache reads. If the provider's quota meter reacts strongly to cache reads, the cache hit ratio can look spectacular while the quota still evaporates. NouGen must learn the provider's actual quota physics from telemetry.

---

# 7. CONTEXT ENGINE: CACHE THE STABLE CORE, MOVE VOLATILE STATE OUT

Frontier context-engineering practice says context is finite and should be curated. Apply that literally.

Context layout:

1. stable system/core policy
2. stable repo/project canon
3. compact task contract and acceptance criteria
4. selectively recalled shards / progress checkpoint
5. current diff/test evidence
6. immediate instruction

Keep stable prefixes stable to maximize cache reuse. Do not inject timestamps, noisy trackers, full relay history, or volatile telemetry near the front unless needed.

Move long histories to shards, git, progress files, and structured state. Recall just the pieces needed for the next decision.

## Tool definitions

Do not stuff 30, 100, or 1,000 tool schemas into every turn. Use lazy tool discovery and code execution. Anthropic reports that large tool libraries can consume 50K+ tokens before the request is even read. NouGen already has MCP surfaces; the router should load only capability summaries first, then fetch exact schemas on demand.

Prefer:

`model -> write small program -> program calls tools -> program filters/aggregates -> compact result -> model`

instead of:

`model -> huge tool schema -> tool result dump -> model -> another huge dump`.

---

# 8. LONG-RUNNING HARNESS: ATOMIC PROGRESS, NOT 40-HOUR AMNESIA

The marathon proves a single session can survive compaction, but it should still leave recoverable state continuously.

For every substantial leg create/maintain:

* structured acceptance criteria, ideally JSON
* current progress/checkpoint file
* git branch/commit state
* most recent baseline test result
* current failing test/error fingerprint
* next executable action
* claim lease identity

Each loop works on **one atomic verifiable unit**.

At unit completion:

1. run the relevant test,
2. run integration/E2E evidence where required,
3. update acceptance state,
4. commit or checkpoint cleanly,
5. write a compact progress note,
6. renew/release lease,
7. only then choose the next unit.

This directly matches Anthropic's long-running harness findings: initializer + structured feature list + incremental one-feature work + git commits + progress artifact + explicit end-to-end verification.

A context compaction or provider migration should therefore cost minutes, not hours of rediscovery.

---

# 9. EVIDENCE-GATED COMPLETION

Agents may not declare "done" from narrative confidence.

Completion requires a task-class evidence contract:

`EvidenceScore = weighted(sum(test_pass, integration_pass, lint_pass, live_probe, diff_review, deployment_probe, user_acceptance_if_required))`

`COMPLETE` only if EvidenceScore >= required threshold and all mandatory evidence bits are present.

For production paths, verify through the served surface, not just unit code. The Kaedra Move 3 relay is the template: native tool call emitted, dispatcher executed, second turn consumed tool output, final response matched live identity, audit log written.

---

# 10. PARALLELISM: WORK STEALING WITH CONFLICT AWARENESS

OpenAI reports that its 99th-percentile Codex users were already generating 60+ hours of agent turns per day by June 2026 through multiple parallel agents. Anthropic's 16-agent C compiler experiment demonstrates the upside and the bill: ~2,000 Claude Code sessions and ~$20K to produce ~100K lines and compile Linux. Parallelism is power AND a burn multiplier.

NouGen rule:

Parallelize when child tasks have low write overlap and clear acceptance boundaries.

`ParallelGain = expected_wallclock_saved - merge_conflict_cost - duplicate_context_cost - quota_pressure_cost`

Spawn only when ParallelGain > 0.

Use child relay legs with disjoint scope. One owner lease per write scope. Reviewers may inspect without taking ownership. Idle lanes steal eligible open work from the queue, but never steal an unexpired healthy lease.

Concurrency limit is dynamic:

`max_parallel = f(provider_pressure, merge_conflict_rate, machine_health, queue_age, critical_path_width)`

Do not set a global fixed "16 agents because 16 is cool" number.

---

# 11. CHECKPOINT MIGRATION: THE QUOTA RESET BRIDGE

Before any provider reset wall, context reset, app restart, machine sleep, or model switch, produce a migration capsule:

`{task_id, goal, claim_state, branch, commit, changed_files, tests_passed, tests_failing, failure_fingerprint, evidence_refs, unresolved_questions, next_action, required_tools, recalled_shard_refs}`

The receiving lane must verify repo state + one baseline test before editing.

Migration policy:

* frontier -> local after architecture/diagnosis is settled
* local -> frontier after escalation trigger
* provider A -> provider B when runway cannot cover next atomic unit
* machine A -> machine B only after durable checkpoint exists

This makes quota boundaries a routing event instead of a work stoppage.

---

# 12. HADOUKEN METRICS: MEASURE WORK, NOT CHAT

Existing shard 1@db3 already defines TTA/CTA token economics. Extend Tracker with:

**Responsiveness**
* TTA_seconds: relay seen -> first executable action
* TTA_tokens: tokens burned before first executable action
* CTA_seconds/tokens: claim -> first evidence

**Completion economics**
* TTE_tokens: total tokens -> verified evidence
* verified_units_per_M_tokens
* verified_units_per_provider_quota_percent
* frontier_premium: additional verified success from frontier vs cheapest viable lane

**Autonomy**
* autonomy_yield = verified atomic units / user interventions
* human_turn_leverage = executable actions / user message
* resume_cost = tokens + seconds from checkpoint load -> productive action

**Context**
* cache_hit_ratio
* cache_drag = cache_read_tokens / verified_atomic_units
* context_ROI = decision-relevant evidence tokens / total context supplied
* compaction_recovery_cost

**Claims**
* open_age_p50/p95
* claim_latency
* lease_expiry_rate
* duplicate_claim_attempts
* passive_ack_rate (target 0)
* blocked_without_evidence_rate

**Quality**
* retry count
* revert rate
* escaped defect rate
* test pass rate
* hallucinated-state incidents

The marathon's 99.96% cache hit looks excellent on cache_hit_ratio but may look terrible on cache_drag. Both are necessary.

---

# 13. ONLINE LEARNING ROUTER

Do not leave the thresholds heuristic forever.

Each completed atomic unit writes a training row:

`features = {task_class, repo, novelty, ambiguity, diff_size, tools_needed, failure_streak, context_size, cache_residency, provider_pressure, time_to_reset, lane, model, reasoning_effort, output_budget}`

`outcomes = {verified_success, retries, elapsed, raw_tokens, quota_delta, cost, defects, user_intervention}`

Then update:

* `P_success(route | task)`
* expected quota cost
* expected latency
* escalation value
* task-class-specific ClaimScore coefficients

Use a constrained contextual-bandit policy for routine routing: exploit best historical route most of the time, explore cheap alternatives on low-risk work, and suppress exploration on high-consequence tasks.

This maps directly to 2026 research:

* **WISERouter (Jul 2026):** workload-budget-constrained routing framed as a contextual multi-armed bandit; offline + online learning; evaluated on RouterBench and SWE-Bench.
* **LLMRouter / xRouteBench (Aug 2026):** routing as a sequential decision process; learned routers reportedly beat the strongest fixed-model baseline by 14.6% relative; lightweight routers get more competitive under tight budgets.
* **R2-Router (Feb 2026):** jointly selects model AND output-length budget; reports 4-5x lower cost than prior routers. Therefore NouGen's router must price output budget, not only model identity.
* **Adaptive Test-Time Compute via Constrained Policy Optimization (Apr 2026):** allocate extra compute per instance based on marginal value under a global budget rather than uniform reasoning effort; reports up to 12.8% relative accuracy improvement on MATH at matched budget.

These are research results, not guarantees for NouGen. Use them as design evidence, then validate on NouGen's own task distribution.

---

# 14. EVAL THE HARNESS, NOT JUST THE MODEL

Anthropic's Feb 2026 infrastructure-noise study found Terminal-Bench results could move ~6 percentage points solely from resource configuration, larger than many leaderboard model gaps. Therefore NouGen must record environment as part of every serious eval:

`{CPU, RAM, disk headroom, model, model version, tool set, network, timeout, context size, concurrency, cache state, repo commit}`

A provider/model "win" under one machine profile is not a universal win.

Run routing A/B tests across multiple days and machines. Compare against a fixed-model baseline and a simple static-tier baseline. Promote a router policy only when it wins on verified progress at matched quota/cost with controlled infrastructure.

---

# 15. SAFER HIGH AUTONOMY WITHOUT APPROVAL FATIGUE

High autonomy should not mean constant permission popups and should not mean unrestricted blast radius.

Use a two-stage action gate inspired by Claude Code auto mode:

**Stage A cheap deterministic policy:** automatically allow read-only and pre-approved reversible operations.

**Stage B classifier/reasoning gate:** only ambiguous/high-impact actions pay extra reasoning. Check alignment to the active relay goal, reversibility, environment, and scope.

For destructive/irreversible or external-state operations, require explicit policy authorization or a durable reversible checkpoint first.

The point is to keep routine work flowing while expensive supervision focuses on the few actions where it matters.

---

# 16. IMPLEMENTATION ORDER

## Phase A: stop wasting work immediately
1. Enforce `CLAIM / SPLIT / BLOCK / PASS` after relay inspection.
2. Add leases with TTL + heartbeat + holder identity.
3. Make active sessions without claims invisible to ownership logic.
4. Add migration capsules/checkpoints.

## Phase B: make quota visible
5. Add provider runway + EWMA burn + reset ETA.
6. Split raw, billing-equivalent, and quota-equivalent token ledgers.
7. Fit empirical provider quota coefficients from meter deltas.
8. Add cache_drag and verified_units_per_quota_percent.

## Phase C: dynamic routing
9. Build initial heuristic Reasoning Grid with deterministic/local/cheap/frontier/review tiers.
10. Route by uncertainty + provider pressure.
11. Control reasoning effort and output budget independently of model.
12. De-escalate after the hard uncertainty collapses.

## Phase D: learn
13. Log per-atomic-unit features/outcomes.
14. Train task-class success/cost estimators.
15. Move router toward constrained contextual-bandit selection.
16. A/B against fixed-model and static-tier baselines under matched infrastructure.

---

# 17. DEFINITION OF DONE

This control plane is working when Dave can leave the fleet running and observe all of the following:

* open actionable relays become owned or explicitly blocked without Dave repeating himself,
* no ghost session silently reserves work,
* frontier providers automatically shed low-value repetitive loops to Kaedra/local lanes,
* Claude/Codex are escalated automatically when uncertainty warrants the premium,
* tasks approaching quota walls checkpoint before interruption and resume elsewhere,
* cache hit remains high but giant cache churn is penalized when it produces little verified progress,
* provider quota consumption becomes predictable from Tracker telemetry,
* completion requires test/tool evidence rather than narrative confidence,
* work can survive context compaction, machine restart, provider reset, and model swap,
* the control policy improves from its own outcome history.

That is the actual Jarvis architecture: **not one smartest model always awake, but a scheduler that continuously buys the right amount of intelligence for the next atomic decision.**

---

# PUBLIC CROSS-REFERENCE SET CHECKED 2026-09-06

1. Anthropic, *Effective harnesses for long-running agents* (2025-11-26): initializer, structured feature list, incremental work, git/progress state, E2E testing.
2. Anthropic, *Harness design for long-running application development* (2026-03-24): harness design materially moves frontier agent performance.
3. Anthropic, *Effective context engineering for AI agents* (2025-09-29): curate context as a finite resource.
4. Anthropic, *Code execution with MCP: building more efficient AI agents* (2025-11-04): use code/tool discovery to avoid enormous tool-definition/result context overhead.
5. Anthropic, *Introducing advanced tool use* (2025-11-24): dynamic tool discovery and programmatic orchestration.
6. Anthropic, *How we built Claude Code auto mode* (2026-03-25): cheap first filter, reasoning only on flagged actions; reduce approval fatigue while retaining autonomy.
7. Anthropic, *Building a C compiler with a team of parallel Claudes* (2026-02-05): 16-agent autonomous parallelism can scale scope dramatically, but compute cost scales too.
8. Anthropic, *Quantifying infrastructure noise in agentic coding evals* (2026-02-05): resource configuration can move scores by multiple points; evaluate the whole system.
9. Anthropic, *Scaling Managed Agents: Decoupling the brain from the hands* (2026-04-08): stable execution interfaces should outlive changing model/harness assumptions.
10. OpenAI, *Codex-maxxing for long-running work* (2026-06-22): persistent workspaces, verifiable steps, continuity across long tasks.
11. OpenAI, *How agents are transforming work* (2026-06-25): long-horizon delegated work is the new unit; 99th-percentile users exceeded 60 hours of parallel Codex agent turns/day by June 2026.
12. OpenAI, *Introducing the Codex app* (2026-02-02): explicit multi-agent parallel orchestration for long-running work.
13. OpenAI, *Separating signal from noise in coding evaluations* (2026-07-08): benchmark quality itself must be audited; static leaderboard numbers are not enough.
14. Kubernetes, *Leases / Coordinated Leader Election* (current 2026 docs): holder identity, renew time, TTL, optimistic concurrency are mature primitives for claim ownership.
15. R2-Router, arXiv:2602.02823 (2026-02): joint model + output-length budget routing.
16. Adaptive Test-Time Compute Allocation, arXiv:2604.14853 (2026-04): constrained per-instance compute allocation.
17. WISERouter, arXiv:2607.23765 (2026-07): workload-budget-constrained contextual-bandit routing.
18. LLMRouter / xRouteBench, arXiv:2608.06867 (2026-08): unified sequential routing framework with learned routing under cost constraints.

**Important evidence discipline:** there is no public benchmark proving NouGen is literally in the top 0.01%. Treat "top .01%" as the engineering target. The closest public usage comparator found today is OpenAI's published 99th-percentile Codex usage. The architecture above imports frontier methods, but NouGen must earn the percentile claim by its own controlled evals.
