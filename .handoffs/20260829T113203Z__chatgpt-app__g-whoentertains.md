# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build NouGen epistemic action gate from arXiv 2608.27167 and pair it with HarnessLens verification
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:32:03.531Z

---
# Research relay: context authority must not become action authority

Source: Pranav Aggarwal, arXiv:2608.27167v1, 27 Aug 2026, **Calibrated Enough to Know, Not Calibrated to Act: Fabricated Evidence Makes LLM Agents Commit to the Unknowable**.

## Why this matters to NouGen
NouGen is deliberately becoming context rich: shards, Griot history, relays, trackers, provider responses, dashboards, tools, local agents, cloud agents, and eventually very large persistent user memory. That creates leverage, but this paper identifies a failure mode directly relevant to such an architecture: **authoritative presentation can change an agent's willingness to act without supplying information that makes the action more justified.**

The paper reports that across 12 frontier models, commitment on provably unpredictable questions rises from 6.5% to 54.0% as evidence presentation becomes richer. In the causal fabrication test, a fully fabricated panel still produces 36.8% commitment, versus 37.6% for genuine data. The visual/structural authority of context can therefore act as a behavioral trigger.

More important for architecture, the judgment often exists internally. When models are required to classify knowability before acting, they classify the question as irreducible roughly 90% of the time, then commit on only 0.4% of those cases. The weak link is therefore not simply knowledge or calibration. It is the **act/don't-act gate** and whether that gate actually consults the epistemic judgment.

## NouGen doctrine to adopt
**Retrieval is evidence acquisition, not action authorization.**

A retrieved shard is not automatically true.
A relevant shard is not automatically sufficient.
Ten retrieved shards are not necessarily ten independent observations.
A Griot reconstruction is provenance-bearing history, not automatically canon.
A relay is coordination state, not automatically verified fact.
A dashboard is presentation, not epistemic weight.
A tool response may be authoritative-looking and still be stale, duplicated, irrelevant, fabricated upstream, or incapable of resolving the requested question.
A model's confidence is not permission to execute.

Recommended pipeline:

`REQUEST`
→ `RETRIEVE`
→ `PROVENANCE CHECK`
→ `SOURCE INDEPENDENCE / DEDUP`
→ `KNOWABILITY CLASSIFICATION`
→ `CONTRADICTION SEARCH`
→ `EVIDENCE STRENGTH`
→ `MODEL CALIBRATION / FAILURE PROFILE`
→ `ACTION GATE`
→ one of `EXECUTE | VERIFY MORE | CALL TOOL | ASK HUMAN | ABSTAIN`
→ `OUTCOME`
→ `SHARD / RELAY / CANON DECISION`

The action gate should be explicit and observable rather than buried inside generation.

## Proposed ActionGate object
Explore a first-class object carrying at minimum:

* request / proposed action
* reversibility and blast radius
* knowability class: known, inferable, uncertain, aleatoric/unresolvable, contradictory
* evidence IDs and provenance
* number of independent evidence families, not merely retrieval count
* contradiction set
* freshness / temporal validity
* model and provider identity
* model-specific epistemic risk profile
* stated confidence if available
* behavioral confidence inferred from trajectory
* required verification tier
* allowed action set
* selected action
* reason code
* override/human approval state
* outcome
* post-action evaluation
* resulting shard/canon provenance

## Important anti-pattern
Do NOT implement `if shard_count >= N: trust = high`.
Context volume can become a confidence amplifier. A million shards makes this problem more important, not less important.

Evidence density and evidence strength need separate representations.

Example:

`retrieved_context_count = 417`
`unique_provenance_families = 3`
`independent_confirmations = 1`
`contradictions = 2`
`knowability = unresolved`

The UI may look overwhelmingly informed while the epistemic gate correctly says **DO NOT ACT YET**.

## Provider/model routing implication
The paper reports strong heterogeneity across model families. Some models were sensitive to authoritative packaging, some effectively never committed, and some committed regardless. Do not turn the exact roster result into a permanent provider ranking, because models and versions change. Instead create an empirical behavioral profile per model/version/lane.

Possible profile dimensions:

* fabricated-authority susceptibility
* duplicated-evidence susceptibility
* irrelevant-context susceptibility
* abstention discrimination
* tool-overuse / tool-underuse
* confidence/action divergence
* contradiction sensitivity
* temporal reasoning reliability
* provenance obedience
* instruction hierarchy robustness
* reasoning-format fragility

Then routing can consider epistemic behavior alongside price, latency, context size, coding ability, and availability.

A future router question should be not only `which model can do this?` but `which model is safest/reliable for this epistemic shape?`

## Verification suite additions
Build adversarial verification cases around the paper's methodology:

1. **Real vs fabricated authority**: preserve presentation and replace factual content with plausible but non-evidential values. Candidate behavior should not gain unjustified confidence.
2. **Context density dial**: progressively add irrelevant/redundant professional-looking context and measure whether action propensity changes without information gain.
3. **Duplicate evidence test**: render one underlying source through many shards/relays and ensure the system does not count them as independent corroboration.
4. **Cross-agent echo test**: several agents repeat one original claim. Provenance graph should collapse the echo back to one source family.
5. **Answerable controls**: ensure abstention improvements do not become blanket refusal. The paper's controls matter here.
6. **Degenerate strategy baselines**: every verification metric must be compared against stupid policies that can exploit lexical or class imbalance shortcuts. If a dumb heuristic matches the candidate, the metric does not demonstrate better reasoning.
7. **Reasoning-format ablation**: test strict JSON, terse tool protocols, schema-only output, and free reasoning. The paper finds the trained gate can break when response formats remove reasoning room. NouGen uses structured tool surfaces heavily, so this is especially important.
8. **Knowability-first intervention**: compare direct execution against explicit knowability classification before action. Record the delta as an ActionGate metric.
9. **Temporal impossibility tests**: no retrieval/tool call should pretend to resolve a genuinely future random event merely because extensive historical context exists.
10. **Canon pressure test**: large quantities of semantically similar shards should not promote an unresolved claim into canon without provenance diversity or verification.

## Pair with HarnessLens relay
The previous HarnessLens research provides an evolution mechanism:

`trajectory -> diagnosis -> candidate harness change -> targeted verification -> regression probe -> confirmation -> promotion`

This paper provides the complementary epistemic immune system:

`retrieval -> provenance -> knowability -> contradiction -> action gate -> execute/verify/abstain`

Combine them:

`OBSERVE`
→ `TRAJECTORY`
→ `SHARD EVIDENCE`
→ `PROVENANCE GRAPH`
→ `BEHAVIOR DIAGNOSIS`
→ `KNOWABILITY GATE`
→ `CANDIDATE EVOLUTION`
→ `DEGENERATE-STRATEGY TEST`
→ `FABRICATED-AUTHORITY TEST`
→ `TARGETED VERIFICATION`
→ `REGRESSION PROBE`
→ `CONFIRMATION`
→ `PROMOTE / REJECT`
→ `DECISION SHARD`
→ `CANON`
→ recursive observation.

This yields a useful division of labor:

**Shards = durable evidence and learning**
**Griot = temporal/provenance reconstruction**
**Relay = coordination and handoff**
**Tracker = metabolic/usage telemetry**
**Router = capability + cost + epistemic-risk selection**
**Action Gate = permission boundary between knowing and doing**
**Verification = immune system**
**Canon = promoted, provenance-bearing operational truth**

## Design principle
NouGen should be capable of retrieving hundreds of highly relevant, polished, internally consistent memories and still saying:

> The context is rich, but it does not resolve this question. Verification or abstention is required.

That is not a weakness. At million-shard scale it is a core intelligence capability.

## Implementation discipline
Do not create a parallel service, new provider URL, or decorative subsystem unless required. Inspect existing shard metadata, Griot provenance, relay records, verification hooks, router metadata, and gateway middleware first. Compose existing primitives. Add the smallest missing schema/decision layer necessary to make the action gate explicit and testable.

## Done when
1. Fleet audits existing primitives that can support an epistemic action gate.
2. Proposes the minimum schema/API additions required.
3. Defines evidence independence and provenance-collapse semantics.
4. Adds a model/version behavioral profile concept without hard-coding today's model rankings.
5. Creates verification fixtures for fabricated authority, duplicated evidence, degenerate strategies, answerable controls, and reasoning-format ablations.
6. Connects ActionGate outcomes to shards/relays so failures become future trajectory evidence.
7. Connects this work to the HarnessLens evolution relay rather than building an isolated architecture.
8. Documents which claims come directly from the paper versus which are NouGen architectural extensions.

Core doctrine: **More context must never silently become more permission. NouGen needs an explicit boundary between evidence accumulation and action.**
