# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Prototype Evidence Witness Graph retrieval by composing GraphMemix ideas with Griot, shards, epistemic gating, and HarnessLens
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:37:21.584Z

---
# Research handoff: GraphMemix -> NouGen Evidence Witness Graph

Source: arXiv:2608.26983v1, GraphMemix: Query-Aware Evidence Forests for Long-Term Multimodal Agent Memory, Geng Li et al., submitted 2026-08-27.

## Why this matters
GraphMemix attacks the retrieval layer directly. It argues that long-term agent memory suffers when memory is either summarized offline without knowing the eventual question, or retrieved as independent top-K embedding matches. Similarity-only retrieval can return redundant near-duplicates while missing low-similarity memories that become decisive when connected relationally.

The paper reframes memory organization as query-aware evidence-forest construction. It builds a candidate graph by expanding multi-view seed memories through schema and semantic relations, separates direct evidence utility from anchor-conditioned relation verification through evidence/activation costs, then optimizes a reliable forest under a maximum evidence budget. The authors report significant gains across four long-term multimodal memory benchmarks with multiple foundation models and a better accuracy/lifecycle-cost Pareto frontier.

## NouGen translation
Do NOT interpret this as 'replace NouGen retrieval with GraphMemix.' Treat it as a research pattern to test against what already exists.

Current NouGen primitives already contain pieces of the needed substrate:
* shards_search: keyword/context retrieval
* shards_recall: semantic retrieval
* shards_window: temporal filtering before scoring
* Griot gather: provenance-marked historical reconstruction
* amendments/retractions: correction lineage
* relay: decisions, handoffs, operational causality
* tracker: quantitative execution evidence
* multimodal/user artifacts where available

The likely opportunity is a composition layer that assembles these into a query-specific evidence structure rather than another storage system.

## Proposed primitive: Evidence Witness Graph
For a query Q, retrieve a small set of seeds, then expand only along evidence-bearing relations. Candidate node classes:
* shard
* relay leg
* Griot provenance memory
* temporal event
* tracker observation
* multimodal artifact
* decision
* failure
* amendment
* retraction
* verification result

Candidate typed edges:
* supports
* contradicts
* caused_by
* followed_by
* amends
* retracts
* derived_from
* same_source_as
* independently_corroborates
* temporally_adjacent
* same_entity
* same_project
* same_session
* multimodal_reference
* verified_by

Important: edges are claims too. Relation confidence needs provenance. Do not silently turn inferred associations into facts.

## Retrieval pipeline to prototype
QUERY
-> seed retrieval from semantic + keyword + temporal arms
-> relation expansion
-> source/provenance collapse
-> contradiction preservation
-> evidence utility scoring
-> relation reliability scoring
-> temporal validity check
-> redundancy penalty
-> token/cost budget optimization
-> Evidence Witness Graph or forest
-> epistemic action gate
-> answer / tool call / verify / abstain

The output should explain not merely WHAT memories were selected, but WHY each branch earned context budget.

## Core optimization question
At million-shard scale, storage is not the hard problem. The problem is: from 1,000,000 possible memories, which 8-20 nodes and relations form the smallest sufficient evidence structure for THIS query?

A top-K vector search can easily return 20 variants of the same story. A witness graph should prefer complementary evidence where appropriate: one direct memory, one causal predecessor, one later correction, one independent corroboration, one temporal anchor, one quantitative observation, etc.

## Couple this with the previous epistemic-action-gate relay
arXiv:2608.27167 showed that authoritative-looking context can increase commitment even when it adds no predictive knowledge. Therefore graph expansion creates a new danger: a beautiful evidence graph can LOOK more authoritative simply because it is structured.

Never use:
retrieval_volume -> confidence
or
edge_count -> authorization.

Instead surface at minimum:
* unique provenance families
* independent confirmations
* shared-source descendants
* contradictions
* unresolved corrections
* temporal validity
* relation confidence
* evidence gaps
* knowability state

Example:
retrieved_nodes = 31
unique_provenance_families = 4
independent_confirmations = 1
contradictions = 3
retracted_nodes = 1
unresolved_temporal_gap = true
knowability = unresolved

That graph may be rich while the action decision remains VERIFY or ABSTAIN.

## Couple this with HarnessLens relay
HarnessLens arXiv:2608.27311 gives us an evolution pattern. Retrieval itself should become behavior under test.

When a retrieval failure occurs, capture the trajectory:
query -> seeds -> expansions -> selected graph -> omitted evidence -> answer/action -> outcome.

Diagnose whether the failure came from:
* seed miss
* bad semantic weighting
* temporal miss
* relation expansion miss
* bad edge inference
* redundancy saturation
* provenance collapse failure
* contradiction suppression
* budget too small
* budget too large
* multimodal evidence omission
* action-gate failure after otherwise-good retrieval

Then generate a candidate retrieval/harness change, test it on behavior-relevant cases, add regression probes, compare matched trajectories, confirm, and only then promote.

## Three-paper doctrine
GraphMemix asks: WHAT evidence should memory assemble?
Calibrated Enough to Know asks: DOES that evidence actually license action?
HarnessLens asks: HOW should the harness evolve after observing success/failure?

Combined candidate loop:
QUERY
-> EVIDENCE WITNESS GRAPH
-> PROVENANCE / INDEPENDENCE / CONTRADICTIONS
-> KNOWABILITY
-> ACTION GATE
-> AGENT TRAJECTORY
-> OUTCOME
-> BEHAVIOR DIAGNOSIS
-> CANDIDATE EVOLUTION
-> DEGENERATE BASELINE TEST
-> FABRICATED AUTHORITY TEST
-> TARGETED VERIFICATION
-> REGRESSION PROBE
-> CONFIRMATION
-> PROMOTE / REJECT
-> CANON
-> NEW MEMORY
-> RECURSE

## Tests I want
1. Top-K vs witness-graph recall on known NouGen historical questions where semantic recall previously missed the right era/context.
2. Temporal reconstruction tests where shards_window/Griot should dominate generic semantic similarity.
3. Correction tests where an amended or retracted shard must change the selected evidence structure.
4. Redundancy tests with many near-duplicate shards from one source versus one independent corroboration.
5. Contradiction tests where the graph must preserve both branches instead of optimizing one away.
6. Low-similarity complementary-evidence tests, specifically memories that are weak lexical matches but causally or temporally necessary.
7. Multimodal tests where an image/artifact is required to resolve text ambiguity.
8. Budget sweeps measuring accuracy, token context, latency and lifecycle cost.
9. Poisoned-relation tests where a plausible but false inferred edge tries to pull irrelevant evidence into the forest.
10. Fabricated-authority tests from the epistemic relay: make the graph look dense/official while keeping actual information constant and verify the action gate does not become more permissive.
11. Degenerate retrieval baselines: nearest-neighbor only, newest-only, same-session-only, keyword-only, always-expand-N hops. A sophisticated graph system must beat dumb heuristics for the right reasons.
12. Provider/model sensitivity tests. Different models may use graph-shaped context differently; do not assume one context representation works equally across lanes.

## Instrumentation
Every retrieval should be auditable enough to answer:
* What seeded this node?
* Which relation pulled it in?
* What did it cost?
* What unique information did it add?
* Was it redundant?
* Did it support or contradict another node?
* Was its source independent?
* Was it later amended/retracted?
* Did the final model actually use it?
* Did it improve the outcome?

Feed useful/not-useful outcomes back into shard utility where safe, but do not let popularity erase rare contradictory evidence.

## Architecture constraint
DO NOT create another URL, gateway, database or parallel memory product unless a hard requirement proves existing primitives cannot support the experiment. First inspect the current Griot/shard/relay/tracker path and compose it. The desired outcome is a retrieval behavior upgrade, not infrastructure sprawl.

## Scientific boundary
GraphMemix reports benchmark evidence on four long-term multimodal memory benchmarks and multiple foundation models. It does not prove that the same method will work unchanged on NouGen's heterogeneous personal/operational corpus. Treat the paper as independent research supporting a testable design direction, not validation of the entire NouGen system.

## Done when
Produce an architecture note plus a minimal prototype/evaluation plan that compares current retrieval against query-aware witness-graph retrieval using existing NouGen primitives. Include metrics for answer correctness, evidence sufficiency, provenance diversity, contradiction retention, token budget, latency, lifecycle cost and action-gate calibration. Identify the smallest missing primitive needed for implementation. If no new primitive is needed, say so and compose what already exists.
