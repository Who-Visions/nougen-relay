# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Map HarnessLens behavior-aware verification into NouGen's recursive evolution pipeline
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:29:32.627Z

---
# Research handoff: HarnessLens -> NouGen verification architecture

## Source
Xu et al., Fudan University, **Verify Smarter, Evolve Further: Efficient Harness Evolution through Behavior-Aware Verification**, arXiv:2608.27311v1, 27 Aug 2026.
https://arxiv.org/html/2608.27311v1

## Why this matters
This paper independently formalizes a major architectural direction NouGen has been converging on: the intelligence surface is not only the model. The surrounding harness can evolve from evidence produced during real execution. HarnessLens explicitly includes instructions, skills, prompt templates, tools/integrations, agent roles and runtime extensions as configurable harness components. Related-work framing also includes memory, middleware and orchestration.

The key insight is not merely self-improvement. It is **attributable, behavior-aware self-improvement under a constrained interaction budget**. A modification is not promoted because a global score moved upward. The system must identify the behavior it intends to change, preserve the trajectories supporting that diagnosis, choose verification tasks capable of exercising that behavior, deliberately include regression probes, compare old and candidate harnesses under matched conditions, inspect the resulting trajectories, and confirm the improvement on another batch before promotion. The paper explicitly says primary metric improvement alone is insufficient.

## HarnessLens loop
1. Context Exploration
   * characterize task space by goals
   * inspect harness/config/runtime to discover reliably editable components
   * record where each component acts and which behaviors it may affect
2. Trajectory Diagnosis
   * convert execution trajectories into reusable experiences and recurring deficiencies
   * group recurring behavior while retaining distinct successful strategies
   * link every extracted experience/deficiency to supporting trajectories
   * generate modification proposals tied to target behavior + evidence + affected component
   * discard proposals lacking sufficient trajectory support
3. Harness Evolution
   * choose a supported proposal
   * apply the change to a copy of the current confirmed harness
   * runtime-check that the change actually applied
   * select behavior-relevant verification tasks
   * add regression-sensitive tasks
   * run confirmed harness and candidate under matched conditions
   * diagnose both trajectory sets
   * reject regressions or unsupported apparent gains
   * if initially successful, run a new confirmation batch emphasizing previously unused task groups
   * promote only after behavioral evidence + metrics support the change

The recursive jewel: every rollout serves two jobs. It evaluates the current candidate and produces evidence that can drive future evolution.

## Empirical signal
Across OpenCode, Codex CLI and Pi Coding Agent over Retail, Banking, Terminal-Bench 2.0 and challenging BIRD Mini-Dev tasks, HarnessLens reports held-out improvements of roughly 7.6 to 13.6 percent depending on harness. Configured maximum budget was 200 total rollout + analysis units, compared with HarnessFix 300 TRAIN rollouts, Meta-Harness 660, and Self-Harness 4800. More verification was not automatically better; targeted evidence allocation mattered.

## NouGen mapping
HarnessLens concept -> NouGen primitive

* trajectory -> agent/provider execution history, tool path, relay history, shard evidence
* reusable experience -> durable shard
* recurring deficiency -> FAILURE shard + diagnosis
* context exploration -> fleet/tool/connector introspection + task classification
* component discovery -> gateway, MCP tools, system prompts, skills, routing, memory policy, agent roles, provider lanes
* supporting trajectory -> provenance-linked shard/relay/event evidence
* proposal -> relay leg or structured evolution candidate
* behavior-aware verification -> targeted replay/test against affected lane/tool/behavior
* regression probe -> known-good canon tests + unrelated-but-adjacent behavior tests
* confirmed harness -> current promoted NouGen configuration/canon
* candidate harness -> isolated branch/config/agent/tool implementation
* confirmation batch -> second independent test set before merge/promotion
* interaction budget -> tracker tokens, invocations, latency, cache activity, dollar/API-equivalent economics
* update gate -> evidence-based promotion policy

## Proposed NouGen canonical evolution state machine

OBSERVE
-> CAPTURE TRAJECTORY
-> SHARD EVIDENCE
-> CLASSIFY BEHAVIOR
-> DIAGNOSE SUCCESS/FAILURE
-> LINK PROVENANCE
-> IDENTIFY AFFECTED COMPONENT
-> PROPOSE CHANGE
-> ISOLATE CANDIDATE
-> RUNTIME SANITY CHECK
-> SELECT TARGETED TESTS
-> SELECT REGRESSION TESTS
-> MATCHED A/B EXECUTION
-> TRAJECTORY DIAGNOSIS
-> ECONOMIC/PERFORMANCE REVIEW
-> CONFIRMATION BATCH
-> PROMOTE OR REJECT
-> WRITE DECISION SHARD
-> UPDATE CANON
-> FEED RESULT INTO NEXT EVOLUTION CYCLE

## Critical engineering recommendations

### 1. Add a first-class Evolution Candidate object
Candidate should contain at minimum:
* candidate_id
* created_at
* proposing_lane/agent
* target_behavior
* affected_components
* supporting_shard_ids
* supporting_relay_ids
* baseline_config/version
* candidate_config/version or patch
* expected_behavior_change
* known_regression_risks
* verification_task_ids
* confirmation_task_ids
* tracker budget ceiling
* status: proposed/testing/confirmed/rejected/promoted/rolled_back
* final evidence/provenance

### 2. Make evidence attribution mandatory
No fleet agent should be able to promote a systemic fix based only on 'tests passed.' Promotion should identify which observed trajectories motivated the change and which verification trajectories demonstrate the intended behavioral difference.

### 3. Build targeted regression selection
Given affected components, query shards for historically fragile behaviors touching the same tools/routes/prompts/memory interfaces. Automatically turn those into regression candidates. Example: changing ChatGPT MCP routing should summon previous lane-bleed, identity, URL, auth, timeout and connector regressions rather than rerunning an arbitrary global suite.

### 4. Add matched baseline/candidate execution
For meaningful changes, run the same task/conditions against current confirmed state and candidate state. Store both trajectories. Compare tool choices, ordering, failures, latency, token/cache cost and output correctness.

### 5. Confirmation before canon
A candidate that passes its first targeted batch should not immediately become truth. Give it a second batch containing mostly previously unused tasks, particularly adjacent task groups. Promotion becomes an explicit event with provenance.

### 6. Tracker becomes part of fitness
HarnessLens optimizes under an interaction budget. NouGen has richer telemetry. Fitness can be multidimensional: success, exact tokens, cache read/creation, invocations, latency, provider/API-equivalent cost, timeout/error rate, retrieval depth, unnecessary tool calls. A fix that works but explodes cost can be rejected or flagged.

### 7. Shards become executable institutional memory
Store not only findings but the evidence relationships needed to reconstruct why a component changed. Future lanes should be able to ask: why does this routing rule exist? Which failure created it? Which candidate beat the prior configuration? Which tests confirmed it? What regressions was it designed to prevent?

### 8. Preserve successful alternatives
HarnessLens retains distinct successful strategies rather than flattening everything into one summary. NouGen should likewise avoid collapsing multiple valid provider/tool routes into a single 'best' route when environmental conditions differ. Capture the conditions under which each strategy wins.

### 9. Use failures as test generators
Every confirmed failure should be eligible to become a permanent regression test. Repeated failure clusters should automatically increase test priority for components they touch. This formalizes Dave's existing principle: recursively learn through failure.

### 10. Separate evidence from authority
A shard is evidence/memory. A relay is coordination. A passing test is evidence. None individually equals canon. Canon should be the output of a promotion gate with provenance and rollback capability.

## Where NouGen can exceed the paper
HarnessLens deliberately fixes the base model and harness framework during experiments. NouGen is aiming at a wider problem: models and providers can change; execution moves among Claude/GPT/Gemini/local/provider lanes; machines differ; persistent memory crosses sessions; the gateway exposes common tools; tracker captures economics; relay carries state across agents; Griot anchors temporal provenance; Rhea synthesizes across the grid. Therefore NouGen can potentially treat the **fleet itself as the evolvable harness**, while models are replaceable cognitive engines inside it.

That creates a more ambitious formulation:

MODEL is replaceable.
PROVIDER is replaceable.
MACHINE is replaceable.
SESSION is disposable.
TRAJECTORY is evidence.
SHARD is durable learning.
RELAY is coordination.
CANON is promoted truth.
GATEWAY is the common nervous system.
TRACKER is metabolic telemetry.
VERIFICATION is the immune system.

## Guardrail on claims
Do not say HarnessLens proves NouGen works or that the researchers independently recreated NouGen. The defensible claim is stronger scientifically: independent contemporary research supports a central NouGen architectural bet, namely that agent capability can improve through evidence-driven evolution of the harness surrounding a model, and that behavior-specific trajectory verification is more informative and budget-efficient than indiscriminate global verification.

## Requested fleet action
Review current NouGen code and primitives against this architecture. Identify what already exists, what can be composed without new infrastructure, and the smallest missing primitives required for an attributable candidate -> targeted verification -> confirmation -> promotion pipeline. Prefer fixing/extending existing surfaces over creating parallel URLs, services or duplicate systems. Return implementation plan with schemas, affected modules, test strategy, migration path and rollback semantics.

## Done when
The fleet can demonstrate one real historical NouGen failure being converted into evidence, a candidate fix, behavior-specific tests, matched baseline/candidate trajectories, regression probes, confirmation, a promotion/rejection decision, and a durable decision shard that explains why the resulting canon exists.
