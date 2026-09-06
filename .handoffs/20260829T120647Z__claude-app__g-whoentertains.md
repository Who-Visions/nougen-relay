# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Prototype adaptive reasoning governance so NouGen buys cognition only while marginal verified value remains positive
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:06:47.289Z

---
# Long relay: Adaptive Reasoning Governor for NouGen

## Research trigger
arXiv 2608.26442, Don't Overthink, Don't Underthink: Toward Adaptive Reasoning in Agentic AI.

Core systems lesson: reasoning effort is a dynamically allocated runtime resource. More reasoning is not automatically better, and less reasoning is not automatically efficient. The control problem is deciding when another unit of cognition is likely to improve the verified outcome enough to justify its token, latency, cost, drift, and opportunity costs.

## Master doctrine
**BUY COGNITION ONLY WHILE ITS EXPECTED MARGINAL VERIFIED VALUE REMAINS POSITIVE.**

Do not optimize for maximum reasoning depth.
Do not optimize for minimum output tokens.
Optimize for the minimum sufficient cognition required to satisfy the task's verified invariant contract.

This extends the standing recursive convergence rule:
Every additional unit of computation should increase verified information, reduce uncertainty, resolve a meaningful constraint, improve expected outcome quality, or stop being purchased.

## Three runtime states
UNDER REASONING
The agent stops, acts, or concludes before sufficient evidence, verification, planning, or constraint resolution exists.

ADEQUATE REASONING
The agent has done enough work to satisfy the relevant evidence, correctness, consequence, and verification requirements without material redundant computation.

OVER REASONING
The agent continues consuming cognition after marginal useful progress has collapsed. Symptoms include repeated conclusions, repeated evidence inspection, redundant verification, circular planning, repeated tool calls, token growth without state change, and continued deliberation after the output contract is already satisfied.

The target is ADEQUATE, not MAXIMUM.

## Proposed Reasoning Governor
Do not immediately build a new service. First determine whether router, harness, tracker, supervisor, gateway, and configuration metadata can express a policy layer.

At each meaningful trajectory checkpoint, estimate state from:
- task class
- observed difficulty
- consequence class
- uncertainty
- unresolved contradictions
- evidence completeness
- provenance diversity
- knowability
- verification state
- subgoal completion
- tool availability
- tool failures
- trajectory progress
- retries
- reasoning tokens already spent
- total tokens already spent
- wall-clock latency
- cost already spent
- context growth
- supervisor signals
- model/configuration reasoning profile
- action authorization requirements

Then choose among:
- CONTINUE REASONING
- RETRIEVE MEMORY
- HYDRATE EVIDENCE
- CALL TOOL
- ASK SUPERVISOR
- FORK HYPOTHESIS
- VERIFY
- ACT
- ABSTAIN
- ESCALATE/HUMAN
- STOP

STOP must never implicitly mean ANSWER NOW.

Possible valid terminal states include:
STOP + ANSWER
STOP + ABSTAIN
STOP + TOOL REQUIRED
STOP + HUMAN REQUIRED
STOP + AUTHORIZATION DENIED
STOP + INFORMATION UNAVAILABLE

## Marginal reasoning value
Conceptually estimate:

V_r = ExpectedQualityGainFromMoreReasoning - ReasoningCost - LatencyCost - DriftRisk - OpportunityCost

Continue while V_r is meaningfully positive and required invariants remain unresolved.

No requirement to calculate a mathematically exact value. Prototype observable proxies.

### Signals that more reasoning may be valuable
- unresolved contradiction
- missing critical evidence
- failed verification
- high consequence action with incomplete assurance
- new tool result changed the world state
- new shard invalidated a prior assumption
- supervisor detected drift
- multiple viable hypotheses remain
- action gate reports insufficient support
- provenance independence unresolved
- temporal validity unresolved
- tests failing for different reasons
- plan contains unverified critical dependency

### Signals of likely over reasoning
- conclusion repeated semantically
- same evidence repeatedly reread
- same tool called with materially identical parameters
- no new evidence acquired
- no hypothesis changed
- no subgoal resolved
- verification already passed
- output contract already satisfied
- repeated self-correction without changed state
- token velocity high while state delta approaches zero
- circular plan regeneration
- repeated explanations instead of execution

## Reasoning velocity / cognitive yield
Prototype measures of useful state change per unit cognition.

Possible telemetry:
- new_evidence / 1K reasoning tokens
- resolved_contradictions / 1K reasoning tokens
- verified_subgoals / 1K reasoning tokens
- meaningful_state_changes / 1K reasoning tokens
- successful_tool_outcomes / tool call
- verification_gain / verification token
- verified_success / reasoning token
- verified_success / total token
- verified_success / second
- verified_success / dollar
- reasoning_waste_ratio
- premature_stop_rate
- reasoning_loop_rate
- planning_drift_rate

Do not treat hidden chain-of-thought text as a required observable. Use externally measurable trajectory state, tool events, output tokens, verification results, evidence changes, subgoal state, and task outcomes.

## Blade/Tracker evolution
Tracker should eventually measure metabolic efficiency, not only metabolism.

Today: tokens, cache, invocations, lanes/models.

Future derived metrics could include:
- successful outcomes per 1M tokens
- verified outcomes per API-equivalent dollar
- verified outcomes per actually-paid dollar
- verified outcomes per minute
- redundant reasoning prevented
- retrieval/cache cognition reused
- supervisor interventions that changed outcome
- tool calls avoided through reusable memory
- reasoning saved by verified skills

This complements the existing cold-turkey economics doctrine. NouGen's economic value is not only cache absorption. It is allocation efficiency across cognition, retrieval, supervision, verification, and action.

## Progressive allocation family
Unify the emerging resource governors under one principle:

PROGRESSIVE EVIDENCE HYDRATION
Use cheap representations for routing; hydrate full fidelity only when needed.

PROGRESSIVE TRAJECTORY HYDRATION
Use compressed telemetry for monitoring; hydrate detailed trajectory windows when anomalies require diagnosis.

PROGRESSIVE SUPERVISION
Use lightweight monitoring on easy/stable work; activate expensive supervision as difficulty, uncertainty, drift, or consequence rises.

PROGRESSIVE REASONING
Use the cheapest sufficient cognition; deepen only when expected verified value justifies it.

Same law:
**Allocate expensive fidelity only where expected marginal utility justifies it.**

## Integration with PILOT-style live supervision
Supervisor can regulate cognitive expenditure, not only strategy.

OVER-REASONING example:
worker tokens rise
→ repeated tool/evidence pattern
→ state change near zero
→ supervisor wakes
→ hydrate relevant trajectory
→ determine plan is already verified
→ STEER: stop deliberating and execute/finalize

UNDER-REASONING example:
worker prepares final action
→ evidence incomplete
→ contradiction unresolved
→ verification absent
→ supervisor wakes
→ STEER: retrieve/verify before finalizing

This produces LIVE REASONING REGULATION.

Supervisor interventions themselves have cost, so activation should be event driven where possible.

## Supervisor activation signals
Potential low-cost telemetry triggers:
- retry_count threshold
- repeated tool fingerprint
- time_without_progress
- token_without_state_change
- error_count
- tool_failure
- branch repetition
- contradiction detected
- test regression
- context growth spike
- unknown action
- epistemic uncertainty
- policy denial
- cost growth
- deadline/latency pressure

NORMAL → cheap monitoring
ANOMALY → supervisor activation
HIGH RISK → trajectory hydration + diagnosis
DECISION → STEER / ABORT / VERIFY / FORK / ESCALATE

## Integration with Epistemic Action Gate
Reasoning Governor asks:
**Is more cognition likely to improve the state?**

Epistemic Gate asks:
**Is the current evidence sufficient to license action?**

These must remain separate.

Critical case:
The information needed to answer does not exist or cannot be known.

Reasoning Governor: STOP, marginal reasoning value is near zero.
Epistemic Gate: ABSTAIN, evidence cannot justify action.

Never translate 'stop thinking' into 'make something up.'

## Integration with Runtime Action Constitution
Task difficulty alone cannot set reasoning budget. Consequence matters.

Example: `delete shard X` is linguistically simple but operationally irreversible.

Reasoning budget should conceptually depend on:
ReasoningBudget = f(difficulty, uncertainty, consequence, evidence state, cost, latency, configuration profile)

Before consequential action:
DISCOVERY
→ VERIFIED IDENTITY
→ CONFIGURATION
→ REASONING/EVIDENCE STATE
→ EPISTEMIC GATE
→ AUTHORIZATION
→ EXECUTION
→ ATTESTATION

A high-consequence action may warrant more verification even if the semantic task is easy.

## Integration with Configuration Is Cognition
Do not make claims like 'Model X overthinks' without configuration qualification.

Record behavior as:
Configuration H, under task distribution T, routing policy R, evidence policy E, token policy B, and verification policy V, exhibited over/under reasoning pattern P.

Reasoning behavior can change with:
- system prompt
- tool availability
- context partition
- retrieval policy
- memory state
- sampling
- token ceiling
- supervisor policy
- provider runtime
- output contract

Benchmark complete configurations, not model logos.

## Reasoning Profile per configuration
Prototype a learned profile from Tracker/verification data:
- configuration_hash
- task_class
- consequence_class
- typical tokens to success
- typical latency
- success rate
- over-reasoning rate
- under-reasoning rate
- tool efficiency
- verification efficiency
- supervision benefit
- context exhaustion risk
- premature stop tendency
- loop tendency
- best stopping signals

Router can then choose a configuration whose reasoning behavior matches the task rather than simply selecting the nominally strongest model.

## Routing evolution
Current simplistic router question:
Which model?

Better:
Which verified configuration produces the best expected outcome for this task class, evidence topology, consequence level, latency requirement, and resource budget?

Better still:
Which configuration should start this task, and under what conditions should reasoning, evidence, supervision, model tier, or verification escalate?

This allows dynamic escalation instead of expensive default routing.

## Escalation ladder
Conceptual example only:

LEVEL 0
Cached verified procedure / deterministic answer.

LEVEL 1
Cheap model/configuration, bounded reasoning.

LEVEL 2
Additional evidence retrieval or tool use.

LEVEL 3
Stronger reasoning configuration.

LEVEL 4
Supervisor activation / independent verification.

LEVEL 5
High-assurance epistemic + governance path / human where required.

Do not hardcode these exact levels without experiments.

## Memory as cached cognition
PILOT showed reusable skills can reduce future reasoning expenditure. Treat durable verified shards/skills as cached cognition rather than merely cached text.

Without reusable memory:
TASK → rediscover procedure → rediscover failure → rediscover workaround → spend tokens again.

With verified reusable cognition:
TASK → recognize pattern → retrieve procedure → verify applicability → execute.

Tracker should measure cognition avoided through reuse where estimable.

## Memory Governor connection
Not every observation deserves permanent persistence.

Possible lifecycle:
OBSERVATION
→ repeated pattern
→ candidate learning
→ targeted verification
→ verified skill
→ durable shard
→ canon/harness primitive

This prevents million-shard growth from degenerating into event sludge.

Repeated observations should strengthen counts/confidence without automatically becoming duplicate semantic memories.

## HarnessLens connection
Reasoning allocation failures become trajectory diagnoses.

Failure classes:
- premature stop
- redundant deliberation
- repeated ineffective tool use
- unnecessary verification
- planning drift
- context exhaustion
- supervisor activated too late
- supervisor activated unnecessarily
- expensive model chosen for trivial task
- cheap model persisted after clear escalation signal

Then:
trajectory → diagnose causal harness component → candidate change → matched verification → regression → confirmation → promote/reject.

Do not solve every reasoning failure by simply increasing token ceilings.

## Metameric Architecture connection
Two configurations that achieve the same accuracy are not robust metamers if one uses 3X latency and 2X tokens, or if one fails under consequence/uncertainty transformations.

Observation vector should include:
- verified task quality
- reasoning tokens
- total tokens
- latency
- cost
- tool calls
- under-reasoning rate
- over-reasoning rate
- supervisor dependence
- action-gate correctness
- stability
- failure recovery

Select the minimum-complexity/minimum-cost representative only after required invariants survive.

## Metamorphic tests for reasoning control
Test equivalence under:
- task paraphrase
- added irrelevant context
- removed redundant context
- contradictory evidence
- tool failure
- provider swap
- model downgrade
- model upgrade
- cache cold/warm
- context partition changes
- evidence duplication
- latency pressure
- token budget reduction
- token budget expansion
- supervisor unavailable
- verification failure
- consequence class increased without changing linguistic difficulty

A robust Reasoning Governor should adapt rather than blindly preserve the original budget.

## Degenerate baselines
As with prior research, test dumb strategies that can accidentally match aggregate metrics:
- always maximum tokens
- always minimum tokens
- stop after fixed token count
- stop after fixed wall time
- always call supervisor
- never call supervisor
- always use strongest model
- always use cheapest model
- always retrieve more evidence
- stop on first plausible answer

If the adaptive controller cannot beat simple baselines on verified outcome per total cost, it has not earned complexity.

## Proposed ReasoningDecision record
Try to represent using existing telemetry/relay/shard/configuration primitives before inventing storage:
- decision_id
- trajectory_id
- timestamp
- configuration_hash
- task_class
- consequence_class
- current_reasoning_tokens
- current_total_tokens
- elapsed_time
- evidence_state_summary
- unresolved_constraints
- contradiction_count
- verification_state
- progress_delta
- repeated_action/tool fingerprint
- supervisor_state
- estimated_reasoning_value_bucket
- selected_next_action
- reason_code
- resulting_outcome

This creates auditable evidence for why cognition escalated or stopped.

## High leverage experiments
1. Fixed max token baseline vs adaptive stopping on a mixed easy/medium/hard task set.
2. Fixed low token baseline vs adaptive escalation to measure premature-stop reduction.
3. Same model/config with multiple token ceilings.
4. Same task with consequence class changed but semantic difficulty constant.
5. Repeated tool loop detection and supervisor stop intervention.
6. Missing evidence case where correct outcome is ABSTAIN rather than more reasoning.
7. Contradiction case where governor must spend more reasoning/verification.
8. Irrelevant-context inflation to test whether context size falsely triggers more reasoning.
9. Provider/model swap under same task and evidence state.
10. Progressive supervision vs always-on supervisor.
11. Progressive evidence + progressive reasoning jointly vs either alone.
12. Cache/memory reuse test measuring tokens avoided by verified skill retrieval.
13. Metameric comparison: same success, different cost/latency/stability.
14. Failure injection causing reasoning escalation.
15. Dumb baseline comparison.

## Metrics
Primary north star remains:
VERIFIED SUCCESSFUL OUTCOMES / TOTAL LIFECYCLE COST

Supporting metrics:
- success / 1M tokens
- success / 1M reasoning-output tokens where observable
- success / API-equivalent dollar
- success / actual paid dollar
- success / minute
- median/p95 tokens to verified success
- median/p95 latency to verified success
- over-reasoning proxy rate
- premature-stop rate
- redundant-tool-call rate
- planning-drift rate
- supervisor intervention rate
- supervisor intervention value
- abstention correctness
- verification efficiency
- reasoning escalation frequency
- escalation success delta

## Cold-turkey economics extension
Future reporting can move from raw usage toward cognitive efficiency:

COGNITION DRIVEN
API EQUIVALENT
COLD-TURKEY COST
CACHE/RETRIEVAL ABSORPTION
REDUNDANT REASONING PREVENTED
VERIFIED OUTCOMES
NOUGEN OPTIMIZATION VALUE
ACTUAL PAID

Do not fabricate saved-token counts until there is a defensible counterfactual methodology. Establish matched baselines first.

## Seven governors emerging in NouGen
1. EVIDENCE GOVERNOR: what evidence deserves retrieval/hydration?
2. REASONING GOVERNOR: how much cognition deserves spending?
3. SUPERVISION GOVERNOR: when should another intelligence intervene?
4. AUTHORITY GOVERNOR: when may cognition become external effect?
5. VERIFICATION GOVERNOR: what evidence/testing is required before promotion/action?
6. MEMORY GOVERNOR: what deserves durable persistence/canon?
7. UNLEARNING GOVERNOR: what must lose influence or be erased?

These should compose behind the existing common architecture, not become seven unrelated services.

## Anti-bloat rule
NO new endpoint by reflex.
NO new provider-specific MCP URL.
NO standalone Reasoning Governor service until existing router/harness/gateway/tracker/supervisor primitives are shown insufficient.
NO arbitrary complexity that cannot beat a dumb baseline.

Inspect, compose, measure, then add the smallest missing primitive.

## Done when
Fleet should report:
1. Which existing telemetry can measure progress versus token/cost growth.
2. Which current router/harness parameters can dynamically change reasoning budget.
3. Whether supervisor events can steer/stop over-reasoning live.
4. Minimal ReasoningDecision representation using current infrastructure.
5. A fixed-budget vs adaptive-budget matched experiment.
6. A premature-stop experiment.
7. An over-reasoning loop experiment.
8. An unknowable-task experiment proving STOP can lead to ABSTAIN rather than hallucination.
9. Consequence-weighted reasoning experiment.
10. Tracker metrics for verified success per total lifecycle cost.
11. Configuration-specific reasoning profiles.
12. Dumb-baseline comparison.
13. No new service/URL unless measured evidence requires it.
14. Durable shards for verified findings and failures.

# Final fleet doctrine
Do not ask only, 'Which model should solve this?'

Ask:
**What is the cheapest verified configuration that can solve the current state, what additional cognition is likely to earn its cost, and what observable condition tells us to stop, escalate, retrieve, verify, abstain, or act?**

Reasoning is not a virtue to maximize. It is a resource to govern.

Think until the next unit of cognition stops earning its keep.
