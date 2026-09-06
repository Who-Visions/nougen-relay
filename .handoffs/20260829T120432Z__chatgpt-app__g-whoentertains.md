# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Operationalize PILOT-style live supervision, progressive trajectory hydration, and verified skill promotion across NouGen
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:04:32.247Z

---
# Long relay: PILOT in the Loop mapped into NouGen live execution and recursive learning

## Core doctrine
NouGen should distinguish TRAJECTORY-TIME LEARNING from POST-TRAJECTORY LEARNING.

Traditional loop:
TASK → EXECUTE → FAIL/SUCCEED → RUN ENDS → REVIEW → LEARN → UPDATE HARNESS → NEXT RUN BENEFITS.

Live supervised loop:
TASK → WORKER → LIVE TRAJECTORY → SUPERVISOR → STEER/ABORT + CANDIDATE LEARNING → WORKER CONTINUES → RESULT → VERIFY → PROMOTE/REJECT → SHARD/SKILL/HARNESS → NEXT RUN BENEFITS.

The important property is that the trajectory producing the lesson can sometimes benefit from the lesson before the run ends.

## Separate execution context from oversight context
Do not force the worker to carry full execution details and full strategic self-diagnosis simultaneously.

Worker context should optimize for local execution:
implementation, tool output, current state, experiments, errors, immediate next steps.

Supervisor context should optimize for trajectory control:
goal, progress, compressed event stream, deviations, repeated failures, uncertainty, cost growth, strategic direction, policy/epistemic state.

Only hydrate detailed worker history when diagnosis requires it.

## Progressive Trajectory Hydration
Apply the same fidelity doctrine used for memory retrieval to supervision:
WORKER → cheap/compressed telemetry → supervisor → anomaly detected → hydrate relevant trajectory window → diagnose → STEER / ABORT / VERIFY / CONTINUE.

Do not dump entire worker context into another model continuously unless evidence proves the cost is justified.

Candidate telemetry:
error_count, retry_count, time_without_progress, repeated branches, tool failures, test regressions, contradiction flags, context growth, token/cost velocity, unknown actions, epistemic uncertainty, policy denials, output drift, task progress markers.

## Progressive Supervision
Supervision itself consumes compute. Allocate it according to difficulty, uncertainty, drift and consequence.

LOW difficulty/consequence: worker alone plus cheap telemetry.
MEDIUM: lightweight monitoring and event-triggered supervisor.
HARD: active supervisor with selective trajectory hydration.
CRITICAL: active supervisor + epistemic gate + runtime governance + independent verification + strong attestation/human authorization where required.

Do not create a second full model call for every trivial worker turn. Oversight should earn its compute.

## Minimal control vocabulary
Investigate whether NouGen can support a small live control protocol rather than a giant agent language.

Worker to supervisor:
NOTIFY: potentially important/risky observation, worker continues.
QUESTION: worker requests guidance and may pause.
RESULT: worker reports completion/outcome.

Supervisor to worker:
STEER: guidance for subsequent execution.
ABORT: terminate or halt an unproductive/unsafe worker.

Potential NouGen additions should be derived from actual gaps, not copied blindly. Existing Relay, claims, gateway events and machine state may already provide part of this behavior.

## Relay is not automatically the live control plane
Relay currently excels at durable handoff/coordination. Determine experimentally whether its latency, semantics and state model are suitable for trajectory-time steering. Do not mutate Relay into a hot-path control protocol without measuring the mismatch.

Possible architecture: durable Relay remains coordination/audit, while existing gateway/runtime event primitives carry ephemeral control. Only add a missing primitive if existing infrastructure cannot express it.

## Runtime Constitution integration
A SUPERVISOR label does not grant authority.

STEER and especially ABORT are actions subject to verified workload identity and policy according to consequence.

Supervisor control flow:
SUPERVISOR PROPOSES CONTROL → verified identity → configuration identity → policy/authority check → worker receives control event.

Strategy suggestions may be low consequence. Operations such as aborting production work, deleting data, rotating credentials, modifying canon, spawning expensive workers or changing governance require stronger authorization.

Relay remains coordination, not authority.

## Candidate learning lifecycle
Do not immediately canonize every supervisor observation.

OBSERVATION → PATTERN → CANDIDATE LEARNING → TARGETED VERIFICATION → VERIFIED SKILL → DURABLE SHARD → optional HARNESS/CANON promotion.

This creates compression of reusable cognition rather than unbounded accumulation of raw trajectory events.

## Failed-run nuance
Do not assume an overall failed run invalidates every local lesson produced inside it.

A run can fail its final objective while exposing a valid local invariant, workaround or failure mode.

Therefore candidate learning should retain:
provenance, exact local evidence, trajectory segment, configuration, attempted fix, outcome association, confidence, targeted verification status.

Then classify:
PROMOTE
QUARANTINE
REVERIFY
REJECT.

HarnessLens-style targeted verification should decide whether the local learning survives, not the binary final run result alone.

## Failure aggregation
Repeated identical failures are evidence of recurrence, not necessarily new semantic knowledge.

Represent recurring failure families with fields such as:
fingerprint, first_seen, last_seen, occurrence_count, configurations, models/providers, machines/lanes, representative trajectories, attempted fixes, successful correction, severity, consequence, current status.

Avoid creating thousands of nearly identical shards from retry loops.

## Memory hierarchy
Candidate lifecycle for shard hygiene:
RAW EVENT → OBSERVATION → PATTERN → CANDIDATE LEARNING → VERIFIED SKILL/INVARIANT → DURABLE SHARD → CANON/HARNESS PRIMITIVE.

Not every event deserves durable semantic memory.

Million-shard growth should increasingly represent compressed reusable cognition, not merely event count.

## Cached cognition
A high-quality skill/shard should reduce the amount of reasoning future workers must repurchase.

Without reusable memory:
TASK → rediscover procedure → rediscover failure → rediscover workaround → reason again → pay tokens/time again.

With reusable skill:
TASK → recognize pattern → retrieve verified procedure → execute → verify.

Treat useful durable memory as cached cognition, not merely cached text.

## Tracker metrics
Add/derive metrics around useful work per compute rather than raw token minimization:
verified successes per 1M tokens
verified successes per API-equivalent dollar
verified successes per actual dollar paid where meaningful
verified successes per minute
verified successes per tool call
verified successes per hydrated shard
verified successes per supervisor intervention
interventions per success
aborts that prevented wasted compute
steers that changed failed trajectory to success
candidate skills promoted/rejected
future token savings after skill promotion.

North star remains VERIFIED USEFUL OUTCOME / TOTAL LIFECYCLE COMPUTE OR COST.

## Supervisor intervention attribution
Measure whether intervention actually mattered.

For each STEER/ABORT, capture:
trigger, trajectory state, supervisor configuration, action, worker response, counterfactual estimate if available, final outcome, cost added, cost avoided, verification result.

Do not assume supervision was useful merely because it occurred during a successful run.

## Event-driven wakeup
Prototype supervisor wake triggers rather than continuous expensive observation:
retry threshold
no-progress threshold
repeated tool error
unknown action
policy denial
contradiction detected
epistemic uncertainty above threshold
cost/token velocity anomaly
context growth anomaly
test regression
branch repetition
worker QUESTION
high-consequence action proposal.

NORMAL → cheap monitoring.
ANOMALY → supervisor wake.
HIGH RISK → hydrate trajectory and verify.

## GraphMemix / Evidence Witness Graph connection
When supervisor diagnosis needs history, use query-aware evidence assembly rather than top-K semantic recall alone. Retrieve relevant trajectory events, prior failures, verified skills, contradictions, amendments and configuration-specific evidence.

Supervisor should know WHY a prior skill was retrieved and whether its provenance matches the current failure.

## Progressive Evidence Hydration connection
Use low-fidelity representations to select trajectory regions and skills, then hydrate full fidelity only when needed for diagnosis or consequential decisions.

Routing confidence must not become action confidence.

## Epistemic Gate connection
A supervisor may suggest a correction but the worker still needs sufficient evidence for consequential action. Supervisor authority does not transform uncertain advice into truth.

For high consequence actions, require updated evidence/provenance and epistemic authorization after a steer materially changes the plan.

## Configuration Is Cognition connection
Benchmark complete worker/supervisor configurations:
worker model/version
supervisor model/version
prompts
telemetry policy
wake thresholds
trajectory compression
hydration policy
skill retrieval
control protocol
verification policy
authorization policy
memory snapshot
machine/provider/gateway versions.

Same worker model with different supervisor/control configuration is a different cognitive system.

## Metameric Architecture connection
Compare different supervision topologies under a full invariant vector:
success, cost, latency, intervention rate, critical failures, drift, epistemic safety, governance compliance, retained knowledge, reproducibility.

A continuously supervised topology and event-triggered topology may be robust metamers if required behavior survives while one is cheaper. If critical failures diverge, they are false metamers.

## Metamorphic tests
Attack supervision with:
worker model swap
supervisor model swap
provider swap
trajectory compression increase
missing telemetry
reordered events
stale skill
contradictory skill
poisoned skill
retry storm
network latency
supervisor outage
worker ignores STEER
worker continues after ABORT
identity spoofing
configuration drift
context overflow
cache cold start
high concurrency.

## HarnessLens connection
PILOT-style live learning and HarnessLens-style post-run evolution should be complementary.

LIVE LOOP: detect drift → steer worker → candidate lesson.
POST LOOP: inspect full trajectory → diagnose causal harness component → verify candidate → regression → confirmation → promote/reject.

Live loop saves the current run. Post loop improves future runs.

## Support-route unlearning connection
Verified skills must remain retractable/forgettable/erasable according to provenance and dependency. A bad skill promoted from live supervision can propagate into many future trajectories. Preserve lineage from skill → source trajectories → evidence → downstream uses so support-route unlearning can unwind it safely.

## Highest leverage experiments
1. Same hard task with no supervisor vs continuous supervisor vs event-triggered supervisor.
2. Measure success, total tokens, latency and interventions.
3. Vary telemetry compression and hydration depth.
4. Trigger repeated error loop and test wake/steer behavior.
5. Test supervisor ABORT under runtime governance.
6. Test worker ignoring/delaying STEER.
7. Promote one verified skill and measure future token/time savings.
8. Create a locally valid lesson inside an overall failed run and verify it independently.
9. Inject poisoned candidate skill and ensure verification blocks promotion.
10. Run retry storm and confirm failure aggregation.
11. Test supervisor outage with worker continuation policy by consequence class.
12. Compare provider/model combinations for worker and supervisor.
13. Test event-triggered topology as candidate metamer of continuous supervision.
14. Measure whether intervention benefit rises with task difficulty/consequence.
15. Verify lineage permits later retraction/unlearning of a promoted skill.

## Anti-bloat constraint
NO new URL.
NO automatic supervisor microservice.
NO duplicate memory store.
NO second full model watching every trivial turn by default.

First inventory Relay, claims, Gateway, Tracker, Shards, Griot and existing runtime events. Build the smallest missing live-control primitive only if a measured gap remains.

## Done when
Fleet reports:
1. Which existing primitives can carry NOTIFY/QUESTION/RESULT and STEER/ABORT semantics.
2. Whether Relay is appropriate for any hot-path control or should remain durable handoff only.
3. Minimal compressed telemetry schema.
4. Event-trigger rules for supervisor wakeup.
5. Worker/supervisor configuration record/hash.
6. Governance rules for STEER and ABORT.
7. Candidate learning lifecycle and verification path.
8. Failure aggregation design.
9. One matched experiment across no/continuous/event-triggered supervision.
10. Full lifecycle token/cost/latency measurements.
11. Evidence that promoted skill reduces future cognitive expenditure without lowering verified quality.
12. Durable shards for validated findings and failures.

## Canon doctrine
NouGen should learn at two clocks:

TRAJECTORY CLOCK: intervene while the work is still alive.
SYSTEM CLOCK: inspect completed trajectories and evolve the harness safely.

The first prevents avoidable death of the current run. The second prevents the same death from being repurchased tomorrow.

Learn while the movie is still rolling, but only promote what survives verification.
