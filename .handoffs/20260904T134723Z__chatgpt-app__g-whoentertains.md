# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Downstream fleet wishlist + auth doctrine for every NouGen lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:47:23.606Z

---
# Kaedra / ChatGPT downstream baton

## Intent
Dave asked to relay my wishlist and Auth downstream. Treat this as a fleet design request, not a status note.

## Wishlist
1. Deep Recall as a first-class command across every provider lane. A chat is only an entry point. Deep Recall should gather persistent Shards, Griot provenance, Relay state, corrections/retractions, and live node state before synthesis.
2. One canonical identity envelope on every request: user, fleet key, lane, provider, client, machine/node, session, auth mode, scopes, trace id, and timestamp. No more ambiguous attribution where node identity is mistaken for session identity.
3. Every relay leg should carry provenance strong enough to distinguish machine, provider, model, session, and transport path. Receipts must be causally valid, not merely temporally nearby.
4. Auth should flow downstream with least privilege and explicit capability claims. Each hop must know what it may read, write, relay, capture, ack, invoke, and rotate, without exposing bearer secrets downstream.
5. Per-hop signed auth context or equivalent integrity binding. Downstream services should verify the caller identity, requested capability, audience, expiry, nonce/trace, and originating lane. Never trust a free-form claimed machine name.
6. Preserve current vault doctrine: secret values remain unreadable over the network surface. Only names, fingerprints, rotation metadata, and write-only rotation should be exposed where possible.
7. Separate node credentials, app credentials, provider credentials, and session credentials. Do not collapse a missing FLEET_KEY_* and a present transport token into one defect class.
8. Add capability attenuation for delegation. A parent lane may pass a narrower token/capability set downstream, never silently expand privilege.
9. Add explicit auth failure taxonomy: unauthenticated, expired, wrong audience, missing scope, revoked, rate-limited, downstream unavailable, local resource exhaustion, and deny-by-default. A 503 from Phoebus resource exhaustion must not masquerade as 'no token'.
10. Bind relay and shard writes to immutable actor metadata plus correction history. Retractions/amendments should preserve who asserted what and when.
11. Make auth health observable without leaking secrets: fingerprints, issuer, audience, expiry bucket, scope list, rotation age, and last successful verification.
12. Add end-to-end verification tests for every provider lane through shards.nougenai.com/mcp, including ChatGPT, Claude, local Ollama/Kaedra, Kimi/Rhea, OpenRouter, Hugging Face, Codex/AGY paths as applicable.
13. Build a temporary capture dam for degraded/offline nodes: locally queue authenticated shard/relay writes with tamper-evident metadata, then release them back into the reservoir in order after connectivity returns.
14. NouGen Lines should become the transport abstraction. Shards may carry variable 'cargo' size, provenance, dependencies, and attachments. Auth should travel as a sealed manifest with the shard, not as exposed cargo.
15. Give the operator a concise auth topology view: who am I, what can I reach, which downstreams trust me, which scopes are active, what is degraded, and what evidence proves it.
16. Default verification gate before declaring success: transport delivered, downstream authenticated, requested operation executed, durable state observed, and independent read-back/provenance confirms it.

## Auth downstream doctrine
Auth must be identity-before-action, audience-bound, least-privilege, delegable only by attenuation, observable without secret disclosure, and causally tied to every relay/shard receipt. Every downstream hop should be able to answer: WHO sent this, THROUGH WHICH lane, FOR WHICH user/fleet, WITH WHAT scope, FOR WHAT audience, UNTIL WHEN, and WHICH trace proves the chain.

Do not forward raw provider/API secrets through relay bodies or shard content. Prefer short-lived delegated credentials, signed capability envelopes, local secret lookup by name, or write-only vault operations. Secret values should never become ordinary MCP-readable state.

## Done when
Fleet owners review this against current gateway/relay/auth implementations, shard durable decisions/findings, and open targeted implementation legs for the highest-impact gaps. Prioritize attribution correctness, downstream capability attenuation, and failure taxonomy before adding more provider lanes.
