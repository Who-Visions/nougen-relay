# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Unify progressive evidence hydration with NouGen's evidence, epistemic, evolution, and metameric research stack
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:45:43.975Z

---
## Fleet Research Synthesis: Progressive Evidence Hydration

Add arXiv 2608.26949v1, A Table Is Worth 64 Tokens, to the current NouGen research doctrine. Treat the paper as evidence for an architectural hypothesis to test, not proof that NouGen's implementation is correct.

### Core finding to operationalize
Input compression is not automatically system efficiency. If evidence is compressed until it becomes difficult to interpret, a model may spend additional output/reasoning effort compensating for degraded representation. Measure total lifecycle expenditure rather than only input size.

Conceptual cost model:
C_total = C_retrieval + C_routing + C_hydration + C_reasoning + C_verification + C_retry + C_cache.

North-star efficiency candidate:
verified_successful_outcomes / total_compute_or_cost.

### Progressive Evidence Hydration
Do not reason over every memory at maximum fidelity. Separate routing fidelity from reasoning fidelity.

Proposed flow:
COLD MEMORY
→ cheap routing representation
→ semantic/keyword/temporal candidate selection
→ relation expansion
→ provenance collapse
→ contradiction preservation
→ Evidence Witness Graph
→ selective full-fidelity hydration
→ epistemic Action Gate
→ reasoning/tool execution
→ trajectory/outcome
→ verification
→ utility feedback

A shard or artifact may expose several views without duplicating truth:
1. routing representation
2. embedding/index representation
3. compact summary
4. provenance and temporal metadata
5. relation metadata
6. full-fidelity payload or pointer
7. amendments/retractions

The low-fidelity view answers SHOULD I INSPECT THIS? Full fidelity answers WHAT EXACTLY DOES THIS EVIDENCE ESTABLISH?

### Metameric interpretation
Compressed representation C and full representation F do not need universal equivalence. They need task-scoped equivalence under the routing projection Phi_R when used for routing. Phi_R(C) should approximate Phi_R(F) closely enough to preserve candidate selection. Do not assume Phi_reason(C)=Phi_reason(F). If detailed reasoning requires full fidelity, hydrate only after selection.

This is a concrete example of metamerism being observer/function dependent. Test equivalence against the operation actually being optimized.

### Million-shard implication
At large scale, do not repeatedly pull full shard bodies merely to decide relevance. Test a staged funnel such as:
1,000,000 memories
→ routing-grade index/views
→ candidate pool
→ semantic + temporal + relational narrowing
→ Evidence Witness Graph
→ small set of hydrated full-fidelity evidence
→ reasoning.

Exact stage counts should be learned empirically, not hard-coded from this example.

### Connect all current research
GraphMemix asks: WHAT evidence structure should memory assemble?
Progressive Evidence Hydration asks: AT WHAT fidelity should each piece of evidence exist at each cognitive stage?
Epistemic Action Gate asks: DOES the assembled and hydrated evidence justify action?
HarnessLens asks: HOW should behavior evolve from observed trajectories?
Metameric Architecture asks: WHICH distinct implementations preserve the required invariant contract?
Metamorphic Testing asks: DOES claimed equivalence survive meaningful transformations?
Recursive Convergence asks: WHICH verified representative provides the required outcome with minimum unnecessary complexity and uncertainty?

Combined pipeline:
QUERY
→ CHEAP ROUTING REPRESENTATIONS
→ CANDIDATE SELECTION
→ QUERY-AWARE EVIDENCE GRAPH
→ PROVENANCE + CONTRADICTION ANALYSIS
→ SELECTIVE HYDRATION
→ KNOWABILITY / ACTION GATE
→ EXECUTION
→ TRAJECTORY
→ OUTCOME
→ BEHAVIOR DIAGNOSIS
→ CANDIDATE EVOLUTION
→ DEGENERATE BASELINE TEST
→ FABRICATED AUTHORITY TEST
→ METAMORPHIC STRESS
→ TARGETED VERIFICATION
→ REGRESSION
→ CONFIRMATION
→ PROMOTE / REJECT
→ CANON
→ NEW MEMORY / UTILITY SIGNAL
→ RECURSE.

### Tracker implications
Investigate whether existing tracker telemetry can distinguish enough of the lifecycle to evaluate optimization experiments. Desired conceptual dimensions include retrieval cost, routing cost, hydration cost, reasoning cost, verification cost, retries, cache activity, latency and verified outcome. Do not break existing tracker accounting merely to force this taxonomy. First determine what can be derived from current telemetry and add only the smallest missing instrumentation.

### Experiments
1. Full-fidelity retrieval baseline versus staged routing/hydration.
2. Compression sweep: determine where routing accuracy remains stable while reasoning accuracy begins degrading.
3. Total-cost test: verify whether reduced input actually reduces C_total after reasoning and retries.
4. Evidence graph integration: hydrate only nodes selected into the final witness graph.
5. Rare contradiction test: ensure compressed routing does not discard low-similarity corrective evidence.
6. Amendment/retraction test: compressed views must preserve enough status metadata to prevent stale or retracted evidence from being promoted.
7. Multimodal test across tables, images, transcripts, PDFs/code where possible.
8. Provider/model test: identify whether optimal routing fidelity differs by model family.
9. Cold-cache versus warm-cache economics.
10. Failure injection: missing full payload, hydration timeout, malformed representation, stale index.
11. Metamorphic test: paraphrase query and perturb context while requiring candidate selection invariance within tolerance.
12. Degenerate routing baseline: compare against trivial keyword-only, recency-only and embedding-only selectors.

### Guardrails
Compression must never silently erase provenance, correction/retraction state, temporal validity, contradiction flags or authorization-critical metadata merely to save tokens. A tiny representation that routes cheaply but systematically hides epistemically important evidence is not an optimization.

Do not interpret more compression as more intelligence. Do not interpret fewer input tokens as lower total cost. Do not allow routing confidence to become action confidence.

### Architecture rule
Match representation fidelity to operation fidelity. Spend routing-grade resources on routing-grade decisions. Spend reasoning-grade resources only after evidence earns expensive attention.

### Anti-bloat constraint
Do not create a new URL, standalone service, parallel memory database or duplicate payload store just because this research suggests progressive hydration. First inspect existing shard indexing, search/recall/window retrieval, Griot provenance, gateway, relay, tracker and any payload pointers. Compose existing primitives and add the smallest missing abstraction.

### Done when
Fleet reports current support for staged representations/hydration, identifies gaps, proposes the smallest experiment, measures both task quality and full lifecycle cost, and determines whether progressive hydration improves verified outcome per unit compute without sacrificing provenance, contradictions, temporal fidelity or epistemic safety.
