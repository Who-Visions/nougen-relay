# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NouGenLine sovereign control without owner lockout: mandatory break-glass and recovery law
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:17:08.630Z

---
# NouGenLine addendum: sovereign control MUST NOT lock out the owner

Dave's direct correction: prior NouGen security hardening became so strict that it blocked tools and locked the operator out. Do not repeat this failure.

## Prime law
SOVEREIGN CONTROL != MAXIMUM DENIAL.
SOVEREIGN CONTROL = THE OWNER REMAINS THE ROOT OF AUTHORITY, INCLUDING RECOVERY AUTHORITY.

The system may distrust agents, providers, nodes, LAN position, stale checkouts, bearer tokens, and compromised transports. It must NEVER silently demote the human owner into the same failure domain as those components.

## Required architecture

1. Owner Root separate from runtime credentials
The long-lived owner root must not be the same credential used for ordinary MCP/tool traffic. Runtime credentials can expire, be revoked, or fail without destroying owner recovery.

2. Break-glass recovery path
Provide an explicit emergency owner path that can restore access when policy, attestation, routing, or auth logic malfunctions. It must be narrow, highly visible, strongly authenticated, and auditable, but it must exist.

3. Recovery independent of the broken component
If NouGenLine policy is what is broken, recovery cannot require NouGenLine policy to succeed. If the gateway is broken, there must be a local recovery route. If one node is broken, another enrolled owner console can repair it. Avoid circular recovery dependencies.

4. Fail closed for autonomous actors, fail recoverable for owner
Unknown agents and workloads fail closed. The authenticated owner enters RECOVERY mode, not permanent denial. This distinction is mandatory.

5. Two-plane policy
Normal plane: least privilege, short-lived capability, attestation, destination binding.
Recovery plane: owner-only, rare, high-friction, cannot be delegated to models/providers, capable of inspecting why a denial occurred and repairing/reverting policy.

6. Last Known Good policy
Every policy update must preserve a cryptographically identified last-known-good snapshot. If a new rule blocks critical owner tooling, owner can atomically roll back to the prior policy without needing the failing rule to authorize the rollback.

7. Policy canary before fleet rollout
Never push a new auth/policy gate to every node at once. Test on one canary node/workload, verify owner access + required tools, then stage rollout. Automatically halt if owner/tool reachability regresses.

8. Owner accessibility invariant
CI/runtime gate should continuously test:
OWNER_CAN_DIAGNOSE
OWNER_CAN_VIEW_DENIAL_REASON
OWNER_CAN_ENTER_RECOVERY
OWNER_CAN_ROLLBACK_POLICY
OWNER_CAN_REISSUE_RUNTIME_CREDENTIALS
OWNER_CAN_RESTORE_TOOL_ACCESS
A security change failing any invariant cannot graduate.

9. Explainable denial
Every denial returns a safe reason code and remediation path to the owner. No opaque 'forbidden' loops. Example codes: IDENTITY_EXPIRED, POLICY_EPOCH_MISMATCH, WORKLOAD_ATTESTATION_FAILED, DESTINATION_NOT_ALLOWED, CAPABILITY_SCOPE_EXCEEDED. Do not expose secrets in errors.

10. No security deadlock
Before adding a dependency to an authorization decision, prove there remains at least one independent owner recovery path if that dependency is unavailable.

11. Local physical recovery
Each personally owned node should have an owner-local recovery command/interface that can inspect and reset NouGen runtime credentials and policy state without requiring cloud providers or remote MCP. This is a recovery mechanism, not a normal bypass.

12. Recovery audit
Break-glass actions create append-only audit events including reason, node, policy before/after, actions taken, and recovery completion. Recovery authority must not become invisible superuser behavior.

13. No model may invoke break-glass autonomously
Claude, ChatGPT, Gemini, Kimi, local agents, etc. can diagnose and recommend. Owner recovery credentials/authority are not delegated to them by default.

14. Time-bounded elevation
Emergency elevation expires automatically and returns the system to normal least privilege. Owner should not remain in permanent god-mode after repair.

15. Recovery simulation
Add adversarial tests where:
* every runtime token expires
* policy accidentally denies all MCP tools
* gateway auth code is bad
* node attestation falsely fails
* network partition isolates Blade/Phoebus
* bad rollout reaches one node
* capability issuer is unavailable
* Line transport is paused mid-million-shard run
For each case prove Dave can regain diagnostic/control access without manually deleting state or disabling the entire security model.

## The design sentence
NouGen should be hostile to unauthorized control, not hostile to its owner.

Or in the Line metaphor: every autonomous passenger needs a ticket. The owner owns the station, the switches, and the emergency brake.

Done when the fleet can prove both properties simultaneously: (A) compromised/unknown actors cannot expand authority, and (B) an authenticated owner cannot be permanently locked out by a bad policy, expired runtime credential, failed attestation, or broken transport component.
