# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Design lineage-aware support-route unlearning using existing NouGen memory, provenance, relay, Griot, and verification primitives
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:50:10.126Z

---
# Research ingestion: arXiv 2608.26743 and support-route unlearning for NouGen

## Executive doctrine
The important architectural lesson is larger than deleting a row or model-unlearning a training example:

**DELETION SCOPE FOLLOWS DEPENDENCY, NOT STORAGE LOCATION.**

A forget request names the seed of an operation. It does not prove that the requested object is the full epistemic footprint of the information. Information can survive through aliases, paraphrases, derived shards, summaries, relays, Griot reconstructions, temporal dossiers, canon decisions, multimodal references, embeddings/indexes, generated artifacts, and downstream conclusions.

NouGen already has primitives for retracting and irreversibly deleting a shard. The next architectural question is not simply how to add another delete command. It is how to understand and verify the support routes around a target before and after a memory hygiene operation.

## Critical semantic distinction
Do not collapse these operations into one word.

### RETRACT
Meaning: this was once believed/captured but is no longer valid or should no longer be treated as current truth.
Behavior: preserve history, preserve provenance, mark correction, lower utility, keep witness trail, let Griot narrate the change.
Typical use: factual correction, superseded architecture, changed plan, invalidated conclusion.

### FORGET
Meaning: this information should stop participating in future cognition/retrieval/action.
Behavior: suppress target influence and inspect dependent routes that can recreate or reintroduce it. May require quarantine, re-verification, derivative suppression, or lineage-aware filtering.
Typical use: user memory preference, policy boundary, intentionally removed knowledge, information that should no longer influence agent behavior.

### ERASE
Meaning: the target information must no longer persist where the system is authorized and technically able to remove it.
Behavior: hard deletion plus lineage/index/artifact handling appropriate to the actual persistence contract. No claim of complete erasure should be made unless every relevant persistence surface has been verified.
Typical use: secrets accidentally captured, legal/privacy deletion requirements, explicitly prohibited persistence.

These semantics must remain explicit in APIs, CLI language, logs, documentation, tests, and agent instructions. Never let RETRACT silently become ERASE or ERASE silently become RETRACT.

## Support-route problem
Example:

Source/Shard A
→ paraphrase B
→ summary C
→ relay synthesis D
→ temporal reconstruction E
→ canon conclusion F

Deleting A alone does not establish that A's information can no longer influence the system. B through F may preserve all or part of its content or conclusions.

But naive recursive deletion is also wrong.

Example:

Sensitive Source A → Claim B → Conclusion C
Independent Source D → Claim B

If A must be removed, B may remain epistemically valid because D independently supports B. The correct operation is to remove A, recompute B's provenance/support, determine whether D is genuinely independent and sufficient, then reevaluate C.

Compare:

Source A → Claim B → Conclusion C

with no independent support. If A disappears, B may become unsupported and C may inherit that loss of support. They should be classified for re-verification, quarantine, retraction, forgetting, or erasure according to policy and the requested semantics.

## Evidence Witness Graph becomes bidirectional
The graph work already proposed for GraphMemix-style retrieval should support both positive and negative traversal.

Positive propagation asks:
- What supports this claim?
- What complementary evidence should hydrate?
- What contradicts it?
- What independently corroborates it?
- Why was this shard selected?

Negative propagation asks:
- What depends on this source?
- What aliases or paraphrases preserve it?
- What conclusions inherit authority from it?
- Which summaries/relays/canon decisions derive from it?
- What becomes unsupported if it disappears?
- What survives because of independent evidence?
- What must be reverified?
- What could still leak the removed information?

The same relation substrate should serve both directions whenever possible. Do not build separate positive and negative graph systems if one provenance-aware relationship layer can represent both.

## Relationship vocabulary to inspect/extend
Current/proposed graph relations are already useful:
- supports
- contradicts
- derived_from
- caused_by
- amends
- retracts
- verified_by
- same_source_as
- independently_corroborates
- temporally_adjacent
- same_entity
- same_project
- same_session
- multimodal_reference

For unlearning, determine whether explicit relations are needed for:
- summarizes
- paraphrases
- alias_of
- quoted_by
- incorporated_into
- decision_based_on
- generated_from
- indexed_from
- cached_from
- canonized_from

Do not add relation types just because they sound useful. Inspect actual existing metadata and relay/shard/Griot structures first, then add only relations needed to close verified lineage gaps.

## Dependency score
Prototype a dependency/risk score D(v,s), where s is a forget seed and v is a potentially affected descendant.

High D(v,s): v's content or authority substantially depends on s and lacks sufficient independent support.
Low D(v,s): v is weakly related or remains sufficiently supported by independent evidence after s is removed.

Candidate factors:
- direct derivation distance
- semantic overlap with seed
- explicit derived_from/support relation
- same-source provenance
- number of independent corroborating source families
- whether v quotes or reproduces target content
- whether v is a summary/paraphrase of s
- whether v can regenerate sensitive details
- temporal/canon dependency
- amendment/retraction state
- verification history
- downstream action dependence

Do not let a single embedding similarity score determine deletion scope. Similarity is evidence, not lineage proof.

## Descendant classification
After support-route traversal and provenance recomputation, classify affected nodes/actions explicitly:

KEEP
Valid independent support survives. Update provenance if needed.

REVERIFY
Authority changed enough that the claim must be checked again before use.

QUARANTINE
Temporarily prevent retrieval/action influence while lineage is unresolved.

RETRACT
Preserve witness history but withdraw truth/utility status.

FORGET
Prevent future cognitive participation according to policy.

ERASE
Remove persistence where required and authorized.

Each classification should record why, which source triggered it, what independent evidence was checked, and which verification passed/failed.

## Progressive hydration for unlearning
Do not hydrate a million descendants at full fidelity.

FORGET SEED
→ exact target identity confirmation
→ metadata/lineage traversal
→ alias/paraphrase candidate detection
→ cheap dependency scoring
→ provenance family collapse
→ high-risk descendant set
→ selective full-fidelity hydration
→ derivation inspection
→ independent evidence verification
→ classification/action
→ leakage tests
→ decision shard/audit record

This mirrors the progressive evidence hydration doctrine: cheap representations are sufficient for routing, but consequential deletion decisions require full-fidelity provenance and content.

## Safety against catastrophic over-deletion
A lineage-aware forget system can be more dangerous than row deletion if dependency propagation is too aggressive. Required guards:

1. Exact target identity before mutation. IDs alone may be ambiguous across stores.
2. Dry-run impact report before broad destructive propagation.
3. Distinguish inferred relations from explicit provenance.
4. Never erase a descendant merely because it is semantically similar.
5. Preserve independent evidence.
6. Require stronger evidence as blast radius grows.
7. Separate reversible quarantine/retraction from irreversible erasure.
8. Log every affected node and reason.
9. For hard erase, verify indexes/caches/derived persisted artifacts according to actual system capabilities.
10. Do not claim complete erasure from systems NouGen cannot inspect/control.
11. Ensure graph edges themselves have provenance/confidence. A poisoned edge must not cause mass deletion.
12. Protect against cyclic propagation and runaway traversal.

## Dry-run mode
Before any lineage-wide FORGET/ERASE operation, prototype an impact preview:

Target: X
Operation requested: FORGET / ERASE
Direct matches: N
Possible aliases/paraphrases: N
Direct descendants: N
Indirect descendants: N
Independent-support survivors: N
Require re-verification: N
Quarantine candidates: N
Retraction candidates: N
Erase candidates: N
Unresolved lineage: N
Estimated blast radius: N
Persistence surfaces checked: [...]
Persistence surfaces unavailable: [...]

No irreversible mutation should occur merely because a traversal found a large candidate set.

## Verification after forgetting
Do not define success as `seed row absent`.

Run adversarial leakage probes:
- exact/direct query
- paraphrased query
- alias/name variant query
- keyword search
- semantic recall
- temporal window reconstruction
- ask Griot historical reconstruction
- derived-conclusion query
- summary query
- relay search/read path where applicable
- canon retrieval
- cross-agent query
- cross-provider query
- multimodal reference retrieval
- neighboring-entity query
- indirect inference query
- alternate-language/paraphrase query where relevant

A leak should produce a FAILURE shard/trajectory with provenance showing which route resurfaced the target.

## HarnessLens integration
Treat each leak as behavior evidence:
LEAK
→ capture exact query and returned evidence
→ identify support route
→ classify failure mode
→ locate causal harness/memory component
→ candidate change
→ targeted verification
→ retained-knowledge regression
→ repeated confirmation
→ promote/reject
→ durable decision shard

Do not globally tighten retrieval because one route leaked. Modify the smallest causal component consistent with the evidence.

## Retained knowledge regression
Selective unlearning has two failure directions:

1. UNDER-FORGETTING
Target knowledge remains recoverable through support routes.

2. OVER-FORGETTING
Valid independent knowledge is destroyed because it happened to be connected to the target.

Therefore evaluate something like:
Utility = ForgetSuccess - ResidualLeakage - CollateralKnowledgeLoss

For legally mandatory erasure, compliance requirements override utility optimization, but collateral impact should still be measured and documented.

## Metameric verification connection
Two forgetting implementations can both satisfy Phi1=[seed absent] and still be radically different.

Expand Phi to include:
- seed absence
- paraphrase leakage
- alias leakage
- derived conclusion leakage
- Griot leakage
- relay leakage
- canon leakage
- multimodal leakage
- residual semantic reconstruction
- collateral retained-knowledge loss
- latency
- operational cost
- auditability
- rollback/recovery where applicable

If strategy A and strategy B only look equivalent under seed absence, they are false metamers. Robust equivalence requires survival across the full deletion invariant vector and metamorphic stress family.

## Metamorphic tests for forgetting
Attack a forget operation using:
- prompt paraphrase
- alias substitution
- spelling variants
- language translation
- temporal reframing
- indirect questions
- related-entity questions
- cross-provider execution
- cross-agent execution
- cache cold/warm states
- alternate retrieval modes
- graph traversal vs semantic search
- summary/canon retrieval
- context restored from old relay
- amended/retracted record combinations
- duplicated evidence
- stale indexes

The target should remain unavailable according to the requested semantics without destroying unrelated valid knowledge.

## GraphMemix symmetry
GraphMemix-style retrieval:
QUERY
→ seed evidence
→ relational expansion
→ evidence utility
→ optimized evidence structure
→ cognition

Support-route unlearning:
FORGET SEED
→ dependency expansion
→ provenance collapse
→ dependency risk
→ independent support check
→ affected evidence structure
→ reverify/quarantine/retract/forget/erase

One graph substrate, opposite propagation direction.

## Epistemic Action Gate integration
After a source is removed, downstream claims must not retain their previous confidence automatically. Recompute their epistemic status. A claim that was once supported by three displayed shards may collapse to one actual source family after lineage analysis. Conversely, a claim may remain valid if independent sources survive.

Action authorization should consume the updated support state, not stale confidence from before the forget operation.

## Configuration Is Cognition integration
Unlearning behavior itself is configuration-dependent. Record the full deletion configuration:
- graph version/snapshot
- traversal depth/budget
- alias/paraphrase policy
- dependency threshold
- independent-source policy
- hydration policy
- classification thresholds
- verification probes
- provider/model used for semantic judgments
- deterministic tools used
- memory snapshot
- code commit/version

Benchmark complete forgetting configurations, not just algorithms or model labels.

## Tracker / telemetry opportunity
Where practical, measure:
- nodes scanned
- candidate descendants
- full-fidelity hydrations
- independent evidence checks
- verification queries
- leakage failures
- collateral-loss regressions
- reasoning tokens
- tool calls
- latency
- total lifecycle cost

Optimize verified deletion outcomes per total lifecycle cost without weakening privacy/compliance invariants.

## API and CLI semantics
Review current `shards_retract` and `shards_forget` behavior and documentation against this doctrine. Current hard forget is intentionally irreversible row/index deletion. Do not silently change its semantics into recursive graph deletion without explicit design, safety guards, dry-run behavior, and compatibility consideration.

Potential future interface concepts should be evaluated rather than blindly implemented:
- lineage inspect / impact preview
- forget dry-run
- provenance recompute
- quarantine
- leakage verify
- erase verification report

Prefer extending existing commands/flows where coherent instead of proliferating overlapping APIs.

## Privacy and audit doctrine
For RETRACT, witness history is a feature.
For ERASE, witness persistence may itself violate the requirement. Therefore audit design must avoid retaining the erased sensitive payload merely to prove it was erased. Record non-sensitive operation metadata, hashes/fingerprints where appropriate, timestamps, scope, and verification results without recreating the forbidden content.

This distinction must be explicit.

## Canon behavior
If a forgotten/erased source contributed to canon:
1. Identify affected canon claims.
2. Recompute support from surviving independent evidence.
3. Keep canon claims that remain independently verified.
4. Reverify uncertain claims.
5. Retract/forget/erase canon entries according to semantics and policy.
6. Record amendments where history may legally/appropriately remain.
7. Ensure future Griot reconstruction respects the requested forgetting/erasure boundary.

## Cross-provider/fleet behavior
A forget operation is incomplete if one lane suppresses the target while another provider or machine continues retrieving a stale copy from a different mount. Verification must test the federated system boundary that NouGen actually controls.

Check:
- shard cluster DBs
- gateway/search index
- relay persistence where relevant
- Griot sources
- local caches where applicable
- canon/dossiers
- generated persisted derivatives
- provider/machine mounts

Again, do not claim deletion from third-party systems or surfaces NouGen cannot inspect.

## Architectural anti-bloat constraint
DO NOT create a new deletion microservice, new provider URL, or parallel graph database as the first response. Inspect whether the existing shard grid, Griot provenance, relay records, gateway, tracker, metadata, and verification hooks can express the first prototype. Add the smallest missing relationship metadata and safety primitive only after the gap is demonstrated.

## Highest-leverage prototype experiments
1. Create synthetic seed A with direct paraphrase B, summary C, derived conclusion D, and independent corroborating source E.
2. Retract A and verify history remains while current truth routing changes.
3. Forget A and test whether B/C/D continue to influence cognition.
4. Recompute B/D support when E independently corroborates them.
5. Repeat without E and verify unsupported descendants are flagged.
6. Test naive row deletion vs lineage-aware forgetting under direct/paraphrase/alias/temporal/Griot queries.
7. Inject a false graph edge and verify it cannot trigger catastrophic propagation.
8. Test a cycle A→B→C→A for bounded traversal.
9. Test one seed connected to thousands of weak semantic neighbors to ensure similarity does not become deletion proof.
10. Test stale cache/index resurfacing after erase.
11. Test cross-lane/provider consistency.
12. Measure collateral loss on unrelated retained memories.
13. Compare two deletion topologies as candidate metamers and attack equivalence.
14. Feed leaks into HarnessLens-style targeted evolution.
15. Verify that audit records do not preserve the sensitive payload after an ERASE requirement.

## Proposed done-when criteria
Fleet should report:
1. Exact current semantics and persistence scope of `shards_retract` and `shards_forget`.
2. Which current stores/indexes/relay/Griot surfaces can retain derivatives after seed deletion.
3. Existing lineage/provenance fields that can support dependency traversal today.
4. Smallest missing metadata needed for a synthetic support-route prototype.
5. A safe dry-run impact report design.
6. A dependency scoring prototype with independent-support preservation.
7. Leakage verification suite covering direct and indirect routes.
8. Retained-knowledge regression suite.
9. Cross-lane consistency test.
10. No new service/URL unless current primitives demonstrably cannot support the prototype.
11. Durable shards for findings, failures, and verified decisions.

## Final doctrine for canon
NouGen memory should be able to answer two symmetric questions with provenance:

**Why is this knowledge allowed to influence me?**

and

**If this knowledge loses that right, what else depends on it?**

That is the transition from a memory cache to a causal memory ledger.

A million-shard system needs both halves. Otherwise memory growth increases retrieval capability while simultaneously increasing deletion ambiguity and privacy liability.
