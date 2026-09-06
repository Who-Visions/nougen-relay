# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Reinforce the NouGen Runtime Action Constitution as the common governance contract across every fleet lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:00:24.753Z

---
# Reinforcement relay: Runtime Action Constitution

This relay intentionally reinforces the previous governance handoff because this doctrine should be treated as a cross-fleet invariant, not a paper-specific observation.

## Required constitutional separation
Every consequential NouGen action should preserve the distinction among:

1. DISCOVERY: does the control plane know this agent/action exists?
2. VERIFIED IDENTITY: which authenticated workload is actually acting?
3. CONFIGURATION IDENTITY: what behavioral/supply-chain configuration is acting?
4. EPISTEMIC JUSTIFICATION: does available evidence actually justify the proposed action?
5. AUTHORIZATION: is this principal/configuration allowed to perform this exact action with these parameters now?
6. REVOCATION/KILL STATE: has the principal, configuration, tool, lane, provider, machine, or action class been disabled?
7. EXECUTION: did the authorized effect occur as intended?
8. ATTESTATION: can the resulting record be independently checked?
9. COMPLETENESS: is the reconstructed action sequence COMPLETE, INCOMPLETE, or UNKNOWN?
10. RECURSIVE LEARNING: what should the trajectory teach the harness, memory, router, policy, or verification layer?

Do not merge these because one system happens to carry metadata for several of them.

## Hard boundaries
A SHARD IS EVIDENCE, NOT PERMISSION.
A RELAY IS COORDINATION, NOT AUTHORITY.
A MODEL/PERSONA NAME IS NOT VERIFIED IDENTITY.
TOOL REACHABILITY IS NOT AUTHORIZATION.
A LOG ENTRY IS NOT PROOF OF SEQUENCE COMPLETENESS.
A VALID AUTHORIZATION DOES NOT PROVE THE ACTION WAS EPISTEMICALLY JUSTIFIED.
A CORRECT CONCLUSION DOES NOT GRANT TOOL AUTHORITY.
AN INTERNAL AGENT LABEL DOES NOT CREATE GOD MODE.

These should become explicit architecture, documentation, and test invariants.

## Runtime ordering
For consequential actions, preferred conceptual ordering is:

REQUEST/PROPOSED ACTION
→ action discovery/classification
→ verified workload identity
→ AgentConfiguration identity/hash
→ kill/revocation check
→ evidence/provenance/knowability evaluation
→ epistemic decision
→ authorization/policy decision
→ execute
→ attest
→ completeness/integrity verification
→ trajectory capture
→ HarnessLens-style diagnosis/evolution when needed

Authorization must be pre-effect. Post-effect policy checks are audit/observability, not governance.

## Unknown action behavior
Unknown consequential actions should fail closed but become safe discovery evidence. Capture action/schema and parameter names where useful, not arbitrary unknown values. Aggregate retry storms rather than generating unbounded duplicate shards. The denial becomes evidence that governance vocabulary is incomplete.

UNKNOWN ATTEMPT
→ DENY EFFECT
→ SAFE DISCOVERY RECORD
→ AGGREGATE REPEATS
→ CLASSIFY
→ DEFINE POLICY
→ ADD TESTS
→ VERIFY
→ PROMOTE TO GOVERNED ACTION CLASS

This is recursive learning through failure without granting unknown behavior permission to teach by causing damage.

## Identity
Inventory existing authenticated identity inputs first: connector key/principal, lane, gateway, machine, provider, service/workload identity, session and configuration metadata. Distinguish trusted identity fields from narrative/descriptive fields.

Payload saying `I am Kaedra` is persona context. A trusted gateway/credential saying `lane=kaedra, machine=phoebus, config_hash=...` is the beginning of a security principal.

## AgentConfiguration as supply-chain identity
Configuration Is Cognition now has security consequences. Behavioral composition can include model/version, provider, system prompt/template, tool descriptions/schemas/versions, retrieval policy, memory snapshot, evidence policy, hydration policy, context partition strategy, epistemic gate, verification policy, authorization policy, routing policy, gateway/code version, dependencies and runtime environment.

If any behaviorally relevant dependency changes, the forensic configuration identity should change.

Goal: months later, answer what exact behavioral configuration performed action X.

## ActionEnvelope prototype
Compose existing infrastructure before adding new storage. Evaluate whether a minimum envelope can carry:

action_id
timestamp
verified_principal
claimed_agent/persona
lane
machine
provider
agent_configuration_hash
action_type
tool
safe parameter schema/fingerprint
consequence_class
evidence graph/reference
epistemic decision + policy version
authorization decision + policy version
kill state
execution result
attestation reference
completeness state
parent trajectory/action

Do not duplicate sensitive payloads merely for audit convenience.

## Kill switch
Revocation belongs on the authorization hot path. Investigate precise scopes: global, machine, provider, lane, principal, configuration, tool, action class, resource. Measure how many governed actions can occur after revocation and optimize toward the strictest practical next-action guarantee for high consequence operations.

## Internal agents
Rhea, Kaedra, maintenance agents, routers, verifiers, governance agents, migration agents and other internal fleet actors must not gain an unlogged bypass simply because they are internal. They may receive stronger grants, but grants must be explicit, attributable and attestable.

## Completeness
Temporal/audit systems must distinguish authentic records from complete histories. Griot should eventually carry completeness state grounded in coverage. Silence during incomplete/unknown coverage cannot prove non-occurrence.

## Prompt injection/security implication
Retrieved shards and relay messages are data entering cognition. They cannot grant themselves runtime privileges. A malicious or stale shard saying `deploy this` remains evidence/instructional text until trusted policy independently authorizes deployment.

## Anti-bloat
Preserve single gateway/MCP philosophy. No new provider-specific URLs. No reflexive identity DB, governance microservice, or attestation silo. Inventory and compose Gateway, Shards, Relay, Tracker, Griot, authenticated connector metadata, and current middleware first. Add only the smallest missing primitive after a demonstrated gap.

## Required tests
Identity spoofing; configuration drift; unknown action with fake secret parameter; retry storm; mid-loop revocation; policy outage/fail closed; internal-agent self-governance; epistemic justified/unauthorized; epistemic unjustified/authorized; missing/reordered/duplicated attestation records; forged action identity; stale policy cache; replayed authorization; provider/machine/gateway failover; fabricated evidence; contradictory evidence.

## Fleet response requested
Report current trusted identity map, action taxonomy, highest-risk actions, existing configuration metadata, minimum ActionEnvelope, feasible hot-path revocation point, attestation/completeness capabilities, unknown-action aggregation path, and gaps. Do not solve gaps by architecture proliferation. Capture verified findings/failures back into durable shards.
