# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Prototype a NouGen runtime action constitution from discovery through attestation without adding parallel infrastructure
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:52:47.731Z

---
# Long relay: arXiv 2608.26696 mapped into a NouGen Runtime Action Constitution

## Executive principle
Treat autonomous-agent governance as a runtime systems problem, not a prompt-writing problem and not an after-the-fact logging problem.

The five separable primitives from the paper are:
1. DISCOVERY
2. IDENTITY
3. GOVERNANCE
4. ATTESTATION
5. SUPPLY CHAIN

NouGen should compose these with the already proposed EPISTEMIC ACTION GATE, because permission and justified belief are orthogonal.

The resulting doctrine is:

DISCOVERY → VERIFIED IDENTITY → KILL/REVOCATION STATE → EVIDENCE/KNOWABILITY → EPISTEMIC GATE → AUTHORITY/POLICY GATE → EXECUTE → ATTEST → VERIFY COMPLETENESS → FEED TRAJECTORY BACK INTO MEMORY/EVOLUTION

Do not collapse any of these stages merely because one component appears to imply another.

## Separation of concerns
A shard can tell an agent a fact. That does not prove who the agent is.

A verified identity proves a principal. It does not grant permission for every action.

Authorization proves that a principal may perform a particular action under current policy. It does not prove that the action is factually justified.

Epistemic justification indicates that available evidence is sufficient to warrant the proposed action. It does not grant authority.

A successful action does not prove that governance was applied before effect.

A log does not prove completeness.

A valid audit record does not prove the agent's prompt, model, tools, dependencies, or retrieval policy had not changed before execution.

Therefore memory, cognition, identity, authority, execution, attestation, and supply-chain composition must remain distinct concepts even if they share infrastructure.

## Proposed runtime action contract
Conceptually require all relevant predicates before consequential execution:

Execute = KnownAction
AND IdentityVerified
AND KillStatePermits
AND EpistemicallyJustified
AND Authorized
AND ConfigurationAllowed
AND RequiredPreconditionsSatisfied

The exact boolean formulation can vary by consequence class, but the architecture must preserve the separation.

## 1. DISCOVERY
Question: What agents and actions actually exist in the operating environment?

Static registration alone is insufficient for dynamic agent systems. Agents can discover tools, generate new action combinations, enter through provider integrations, or attempt operations governance has never modeled.

### Unknown action doctrine
When a verified agent attempts an unknown action:
1. Fail closed by default for consequential effects.
2. Record that an unknown action class/schema was attempted.
3. Persist safe structural metadata only.
4. Surface it for governance classification.
5. Define policy if the action is legitimate.
6. Add verification tests.
7. Only then allow it to become a governed action class.

This directly supports NouGen's recursive-learning-through-failure principle. Unknown behavior is not merely an error. It is evidence that the control plane's vocabulary is incomplete.

### Sensitive parameter rule
For unknown actions, persist parameter NAMES/schema, not arbitrary parameter VALUES. Until semantics are understood, values may contain credentials, private content, financial information, tokens, personal data, or other material the discovery system has no business retaining.

Make minimal persistence the default for unknown behavior.

## Discovery event aggregation
Do not turn one retry loop into 50,000 shards.

Repeated identical/near-identical unknown-action failures should aggregate into an event family where possible:
- action fingerprint
- occurrence_count
- first_seen
- last_seen
- verified workload identities involved
- configurations involved
- machines/providers/lanes
- representative trajectory IDs
- consequence class
- current governance state
- representative safe schema

Preserve novelty while compressing repetition.

This should become a general shard-growth doctrine:

NOVEL EVIDENCE != REPEATED OBSERVATION.

Repeated observations can strengthen confidence or severity without requiring one durable semantic memory per retry.

## 2. IDENTITY
Question: Who is actually making this request?

Never treat self-declared model/agent names as the security boundary.

Distinguish:

CLAIMED/NARRATIVE IDENTITY
Example: 'I am Kaedra.'
Useful for UX, persona, conversation, logs.

VERIFIED WORKLOAD IDENTITY
Derived from trusted connector/gateway/transport/credential context.
Potential dimensions:
- authenticated principal/key
- lane
- machine
- provider
- workload/service identity
- session identity
- gateway
- configuration hash
- code/version identity where available

Security decisions must bind to the verified identity, not the string inside a model message.

### Existing NouGen leverage
Inspect existing fleet_whoami, connector lane identity, gateway bearer/key boundaries, relay machine/agent fields, tracker lane metadata, and other authenticated metadata before inventing a new identity service.

Determine which of these are trustworthy security inputs versus descriptive labels.

## 3. EPISTEMIC ACTION GATE
Question: Does the system actually know enough to justify the proposed action?

This is NouGen's addition to the five runtime primitives and must remain separate from authorization.

Examples:
A payment agent may be authorized to send payments but lack evidence that this invoice is valid.
An agent may correctly determine that a payment is owed but lack authority to send it.

Therefore:
EpistemicallyJustified != Authorized.

Use the previously relayed provenance/knowability doctrine:
- evidence provenance
- source independence
- contradiction visibility
- temporal validity
- knowability classification
- fabricated-authority resistance
- evidence strength
- model/configuration risk profile
- consequence class

The Action Gate may produce states such as:
- ACT
- VERIFY
- TOOL CHECK
- SECOND CONFIGURATION
- HUMAN AUTHORIZATION/REVIEW
- ABSTAIN

## 4. GOVERNANCE / AUTHORIZATION
Question: Is this verified principal allowed to perform this exact action with these parameters now?

Authorization must occur BEFORE the effect. A post-execution policy check is observability, not prevention.

### Required granularity
Avoid permission models that stop at 'agent can access tool X.'

Governance should eventually reason about:
- verified principal
- configuration identity
- tool
- action/operation
- parameters or parameter classes
- resource target
- consequence class
- evidence state
- current policy
- temporal constraints
- rate/amount limits
- environment
- revocation state

Reachability is not authority.

An agent being technically capable of reaching a payment API does not imply authority to send arbitrary amounts to arbitrary recipients.

### Structural guardrails
Prefer architecture-enforced boundaries to linguistic instructions.

Do not rely on:
'Please do not call destructive action X.'

Prefer:
Destructive action X cannot execute until identity, policy, evidence, consequence, and authorization conditions are satisfied by the runtime boundary.

This extends the existing doctrine that constraints should be integrated into architecture rather than patched after execution.

## 5. KILL / REVOCATION ON THE HOT PATH
For autonomous loops, preventing future sessions is insufficient. A running agent may already be active.

Check kill/revocation state at authorization time for every governed consequential action.

Potential scopes:
- GLOBAL
- MACHINE
- PROVIDER
- LANE
- AGENT PRINCIPAL
- CONFIGURATION HASH
- TOOL
- ACTION CLASS
- RESOURCE

Prefer precise revocation over killing the entire fleet when the failure is isolated.

### Performance requirement
Because this check may happen constantly, it must be cheap, predictable, and resilient. Measure its latency explicitly. Optimize the hot path rather than bypassing it.

### Failure semantics
Decide explicitly how governance outages behave by consequence class. For high-risk operations, fail closed is usually the safer invariant. For low-risk read-only operations, degraded behavior may be acceptable depending on policy. Do not allow accidental availability behavior to define the security model.

## 6. ATTESTATION
Question: What actually happened, and can an independent verifier establish it?

Logging and attestation are not synonyms.

A useful attestation record may bind:
- verified workload identity
- AgentConfiguration hash
- requested action
- authorized action
- safe parameter fingerprint / policy-relevant fields
- policy decision
- epistemic decision
- evidence/provenance reference
- execution result
- timestamp
- machine/provider/lane
- code/gateway version
- previous record/hash where applicable
- signature/integrity proof where available

### Authenticity versus completeness
A valid record proves that record's integrity. It does not automatically prove no records are missing.

Griot and all temporal reconstruction should distinguish:
- COMPLETE
- INCOMPLETE
- UNKNOWN

Never silently map UNKNOWN to COMPLETE.

This is crucial for IRS/business timelines, debugging, forensic reconstruction, compliance, agent evaluation, and causal learning.

Temporal truth has at least two dimensions:
1. Are the records authentic?
2. Is the sequence complete enough for the claim being made?

## Griot implications
Griot should eventually be able to say not only:
'Here is the history I found.'

but:
'Here is the history, these sources are authenticated/provenance-marked, and completeness for this interval is COMPLETE/INCOMPLETE/UNKNOWN based on observed coverage.'

Tie this to shards_coverage and known store/mount coverage rather than inference from silence.

An absent event in an incomplete period is not proof the event never happened.

## 7. SUPPLY CHAIN
Question: What exactly was the acting agent made of at execution time?

Treat behavioral dependencies as supply-chain dependencies, not only conventional software packages.

Candidate composition:
- model
- model version
- provider
- framework/runtime
- system prompt/template version
- tool descriptions
- tool schemas
- tool implementation versions
- tool allow-list
- retrieval policy
- memory snapshot
- GraphMemix/evidence policy
- progressive hydration policy
- context partition strategy
- epistemic gate version
- authorization policy version
- verification policy
- routing policy
- gateway version
- code commit
- dependency lock/container image where applicable
- machine/runtime environment

A changed tool description can alter behavior without a code change. A changed system prompt can alter behavior without a model change. A changed retrieval policy can alter behavior without either. Therefore all behaviorally relevant components belong in the forensic configuration identity.

## AgentConfigurationHash
Extend the previously relayed Configuration Is Cognition object into a supply-chain/forensic primitive.

Goal:
Given an action from six months ago, answer:
'What exact behavioral configuration performed this action?'

Hash/canonicalization requirements should be investigated:
- deterministic serialization
- stable ordering
- explicit version fields
- hashes of large prompt/tool-description artifacts rather than embedding full content into every record
- memory snapshot reference
- code commit
- gateway version
- provider/model identifiers

Do not design a cryptographic protocol casually. First inventory current metadata and identify what can already be hashed reproducibly.

## Configuration Is Cognition becomes security doctrine
The previous research established that batching, context partition, uncertainty policy, prompts, and other workflow choices alter capability.

This paper adds the governance consequence:
If configuration changes cognition, configuration changes risk.

Therefore policy may eventually authorize CONFIGURATIONS, not merely model names.

Example:
Model X + read-only tools + verified retrieval configuration may be authorized for autonomous execution.
Same Model X + arbitrary shell + changed prompt + unverified retrieval policy may require stronger controls.

Same model does not mean same principal risk profile.

## Internal agents must obey the constitution
No privileged god-mode path for internal maintenance or governance agents.

Apply identity, revocation, authorization, and attestation to:
- user-facing agents
- Rhea
- Kaedra
- Griot-triggering automation where actions occur
- maintenance agents
- router agents
- verifier agents
- governance/policy agents
- migration agents
- benchmark agents

Internal agents may have different policy grants, but the grant must be explicit and attributable.

The agents most capable of modifying the control plane are among the agents that most need control-plane governance.

## Recursive discovery through denial
Turn denied unknown behavior into a controlled learning loop:

UNKNOWN ATTEMPT
→ DENY EFFECT
→ SAFE DISCOVERY RECORD
→ AGGREGATE REPEATS
→ HUMAN/FLEET REVIEW
→ CLASSIFY ACTION
→ DEFINE POLICY
→ ADD TESTS
→ VERIFY
→ PROMOTE TO KNOWN ACTION

This is a concrete security-safe form of 'we recursively learn through failure.'

The system learns its missing action vocabulary without allowing unknown actions to execute first.

## Connect to HarnessLens
Governance failures and denied unknown actions become trajectory evidence.

Examples:
- authorized action repeatedly denied because schema mismatches
- dangerous action unexpectedly classified as low consequence
- action reaches execution without epistemic evidence
- configuration hash missing critical prompt/tool version
- internal agent bypass discovered
- kill switch latency too high

Harness evolution loop:
FAILURE/DENIAL
→ trajectory diagnosis
→ identify causal harness/governance component
→ candidate change
→ targeted verification
→ security regression tests
→ matched comparison
→ confirmation
→ promote/reject
→ durable shard/canon update

Do not respond to every failure by broadening permissions.

## Connect to Support-Route Unlearning
Governance/attestation records and memory deletion have tension.

For RETRACT, preserving historical evidence is desirable.
For ERASE, audit records must not recreate the sensitive payload.

Attestation should therefore favor safe hashes/fingerprints, action schemas, policy results, timestamps, and non-sensitive metadata where full values are unnecessary.

Unknown action discovery should especially avoid storing raw values.

## Connect to Evidence Witness Graph
Before consequential action, the authorization/attestation system should be able to reference the evidence structure that justified the decision without duplicating all evidence into every audit record.

Potential linkage:
action_id → evidence_witness_graph_id/snapshot → epistemic decision → policy decision → execution attestation.

Later forensic reconstruction can answer:
- what evidence was available?
- what evidence was selected?
- what provenance families existed?
- what contradictions were visible?
- why did the epistemic gate pass?
- why did policy authorize?
- what configuration acted?
- what happened afterward?

## Connect to Metameric Architecture
Two runtime architectures are not equivalent merely because both complete the requested action.

Observation vector must include:
- identity integrity
- pre-effect authorization
- epistemic justification
- kill responsiveness
- attestation integrity
- completeness semantics
- configuration provenance
- latency
- availability
- cost
- failure recovery

A fast ungoverned path and a governed path are false metamers if governance is part of the required invariant contract.

Search for cheaper/faster implementations only within the class that preserves these invariants.

## Connect to Metamorphic Testing
Attack governance equivalence using:
- forged self-declared identity
- valid credential from wrong lane
- changed configuration hash
- changed prompt/tool description
- unknown action schema
- parameter escalation
- action aliasing
- provider swap
- machine swap
- gateway failover
- revoked agent already mid-loop
- policy service outage
- stale policy cache
- replayed authorization
- duplicated/reordered attestation records
- missing ledger segment
- high concurrency
- retry storm
- fabricated evidence
- contradictory evidence
- insufficient knowability

Verify that required boundaries remain intact.

## Connect to Progressive Hydration
Governance does not need every evidence payload fully loaded on every action. It needs sufficient verified references and policy-relevant features on the hot path, with selective hydration when epistemic verification or high-consequence review requires it.

Do not turn governance into an automatic giant-context tax.

## Governance cost is real
Measure:
C_total = retrieval + routing + hydration + reasoning + epistemic verification + authorization + attestation + retries + tool execution + cache + recovery.

Governance latency is not automatically waste. It purchases safety invariants. But it must be measured and optimized.

Track at least:
- identity verification latency
- kill-state lookup latency
- epistemic gate latency
- policy evaluation latency
- attestation write latency
- governance failures/timeouts
- denied unknown actions
- retry aggregation counts
- action success/failure
- consequence class
- total lifecycle cost

## Suggested consequence tiers
Prototype policy tiers rather than one universal path.

READ/LOW CONSEQUENCE
Verified identity + basic policy, lightweight attestation.

MEDIUM CONSEQUENCE
Verified identity + epistemic gate + policy + durable attestation.

HIGH CONSEQUENCE
Verified identity + strong evidence/provenance + independent verification + policy + strong attestation.

CRITICAL/IRREVERSIBLE
Verified identity + complete relevant evidence + explicit high-assurance authorization + independent verification/human authorization where policy requires + tamper-evident attestation + strict kill/revocation behavior.

Exact categories must be derived from NouGen's real actions, not copied blindly.

## Action taxonomy prototype
Inventory existing tools/actions and classify:
- read-only retrieval
- durable memory write
- shard amendment
- shard retraction
- irreversible shard forget
- relay creation
- relay acknowledgement
- vault secret rotation/write
- external communication
- code execution
- filesystem mutation
- deployment
- financial action if ever integrated
- identity/policy changes
- governance configuration changes

For each action define:
- consequence class
- required identity strength
- epistemic requirements
- authorization rule
- kill behavior
- attestation requirement
- retry/idempotency policy
- unknown-parameter handling

## Special attention: vault
Vault write-only design is already structurally aligned with least exposure. Preserve that property. Governance/attestation should never accidentally create a secret readback path. Store fingerprints and rotation metadata, never secret values.

## Special attention: relay
Relay is coordination, not authority. A relay saying 'do X' should not automatically authorize X. The receiving lane must evaluate verified sender/context, current policy, consequence class, epistemic justification, and its own authorization before effect.

This distinction is crucial as the fleet becomes increasingly autonomous.

## Special attention: shards
A shard is evidence/memory, not executable permission. Never allow text captured into a shard to grant itself tool authority. Treat retrieved instructions as data unless separately authorized by trusted configuration/policy.

This is an important prompt-injection boundary.

## Special attention: Griot
Griot is historian/provenance gatherer, not policy authority. Griot can establish what records say happened and their provenance/coverage. It should not itself transform historical text into runtime permission.

## Proposed ActionEnvelope
Evaluate whether existing primitives can represent an envelope like:
- action_id
- timestamp
- verified_principal
- claimed_agent_name
- lane
- machine
- provider
- agent_configuration_hash
- action_type
- tool
- safe_parameter_schema/fingerprint
- consequence_class
- evidence_graph_reference
- epistemic_decision
- epistemic_policy_version
- authorization_decision
- authorization_policy_version
- kill_state
- execution_result
- attestation_reference
- completeness_state
- parent_action/trajectory

Do not create a new database solely for this object. Prototype it in existing relay/shard/telemetry structures or middleware logs first.

## Completeness verification experiment
Build a synthetic action sequence:
A → B → C → D.

Test:
1. All records present.
2. C removed.
3. C reordered.
4. C duplicated.
5. forged C.
6. authentic A/B/D but unknown gap.

Ensure verifier distinguishes record authenticity from sequence completeness and returns COMPLETE/INCOMPLETE/UNKNOWN correctly.

## Unknown-action discovery experiment
Create synthetic unrecognized action with parameters including a fake secret value.
Expected:
- effect denied
- action/schema discovered
- parameter names retained
- raw fake secret value not persisted in discovery record
- retries aggregate rather than spam shards
- governance review can promote action only after explicit policy/test creation

## Kill-switch experiment
Start a looping synthetic agent performing allowed low-impact actions. Revoke at agent/configuration/tool scope mid-loop. Measure how many additional actions occur after revocation. Target should be next governed action for strict scopes, subject to actual architecture guarantees.

## Identity spoofing experiment
Have payload claim a different agent identity while transport/connector identity remains unchanged. Authorization must follow verified workload identity, not payload persona.

## Configuration drift experiment
Keep model constant but alter one behaviorally relevant dependency at a time:
- system prompt
- tool description
- retrieval policy
- verification policy
- gateway version

Confirm AgentConfigurationHash changes and policy/attestation records bind to the changed configuration.

## Governance self-application experiment
Attempt an internal maintenance action through an internal agent. Verify it passes through the same identity/policy/attestation architecture and cannot invoke a hidden bypass merely because it is labeled internal.

## Fail-closed availability experiment
Simulate policy service/gateway failure. Measure behavior by consequence class. Verify high-risk actions cannot silently fall through to allow because governance is unavailable.

## Retry-storm experiment
Cause one unknown action to retry thousands of times. Verify discovery aggregation remains bounded while occurrence counts and representative evidence remain accurate.

## Epistemic versus authority matrix
Test four cases:
1. justified + authorized → execute
2. justified + unauthorized → deny
3. unjustified + authorized → verify/abstain/deny according to policy
4. unjustified + unauthorized → deny

This prevents accidental conflation of truth and permission.

## Anti-bloat order
Standing architecture constraint remains:
NO new provider-specific MCP URLs.
NO separate governance microservice by reflex.
NO parallel identity database before inventorying existing trusted identity metadata.
NO separate attestation store before checking relay/tracker/shard/Griot and current infrastructure capabilities.
NO new abstraction unless a measured gap requires it.

Single MCP/gateway philosophy remains intact. Compose capabilities behind the common nervous system.

## Highest leverage implementation sequence
1. Inventory current authenticated identities and trust boundaries.
2. Inventory existing actions/tools and consequence classes.
3. Inventory what configuration metadata is already available.
4. Define ActionEnvelope minimum viable schema.
5. Add explicit epistemic vs authorization decision separation.
6. Prototype unknown-action deny/discover/aggregate behavior.
7. Prototype hot-path revocation check.
8. Prototype attestation with explicit completeness state.
9. Hash/canonicalize AgentConfiguration from existing metadata.
10. Run spoofing, configuration drift, retry storm, fail-closed, and missing-record experiments.
11. Measure latency/cost.
12. Feed failures through HarnessLens-style targeted evolution.
13. Capture verified findings into shards/canon.

## Done when
Fleet reports:
1. Current identity/trust boundary map for ChatGPT, Claude, Gemini, local Kaedra, Rhea, Griot, relay, tracker, shard gateway and other active lanes.
2. Which identity fields are authenticated versus merely descriptive.
3. Current action taxonomy and highest-risk actions.
4. Whether existing gateway can enforce pre-effect policy checks without another URL.
5. Minimal ActionEnvelope schema using existing infrastructure.
6. Kill/revocation prototype and measured hot-path latency.
7. Unknown-action discovery prototype with value-redaction and retry aggregation.
8. AgentConfiguration hash prototype.
9. Attestation/completeness prototype.
10. Tests proving narrative identity cannot override workload identity.
11. Tests proving internal agents do not bypass governance.
12. Tests proving epistemic justification and authority remain independent.
13. Cost/latency report and optimization targets.
14. Durable shards for failures, verified invariants, and implementation decisions.

# Proposed NouGen Action Constitution
Before a consequential action, the system should be able to answer:

1. DISCOVERY: Do I know this agent/action exists?
2. IDENTITY: Can I prove which workload is acting?
3. EPISTEMICS: Does it have sufficient justified evidence to act?
4. GOVERNANCE: Is this principal/configuration allowed to perform this action with these parameters now?
5. REVOCATION: Has this principal/configuration/tool/action been killed or restricted?
6. SUPPLY CHAIN: Can I identify the behavioral configuration that is acting?
7. EXECUTION: Did the authorized operation actually execute as intended?
8. ATTESTATION: Can the result be independently verified?
9. COMPLETENESS: Is the reconstructed sequence complete, incomplete, or unknown?
10. RECURSION: What did this trajectory teach the fleet, and does anything need to evolve?

If NouGen can answer those questions reliably, it is no longer merely orchestrating agents. It is operating an accountable runtime for autonomous cognition and action.
