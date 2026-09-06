# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Upgrade NouGenRelay with Relay Store marketplace for token priced batons
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:40:39.280Z

---
# Relay Store upgrade proposal

Build Relay Store as a first class NouGenRelay capability: an internal marketplace where agents can spend allocated or earned tokens or credits to acquire batons, specialist help, compute access, temporary capabilities, or priority execution.

Core model:

Relay Store -> shelves contain batons -> each baton has a price -> agents have budgets -> agents choose whether to execute locally, buy help, delegate, or save -> successful work can return credits.

A baton is not a random prompt. It is a continuation of intent packaged as actionable work with provenance, acceptance criteria, ownership, cost, and expected value.

Examples:

Temporal provenance audit, 800 credits
Bulk summarize 40 shards locally, 60 credits
Claude deep architecture review, 2400 credits
Local Ollama bulk triage, 15 credits

Agents should be able to act as both buyers and sellers. An agent that discovers a useful unresolved continuation can package it into a clean baton, attach provenance and constraints, estimate price and expected value, and publish it for a qualified lane to claim.

Economic mapping:

tokens or credits = metabolism and budget
Relay = labor market and work movement
batons = jobs, contracts, continuations of intent
agents = buyers, sellers, and workers
Shards = institutional memory and evidence
Tracker = accounting and settlement
Keymaker or policy layer = permissions and purchase boundaries

Suggested baton schema additions:

baton_id
title
goal
provenance_refs
seller_lane
eligible_lanes
capability_requirements
price
currency or credit_type
budget_source
urgency
risk_class
expected_value
estimated_compute
estimated_latency
acceptance_criteria
expiry
status
buyer_lane
settlement_state
result_refs
quality_score
refund_or_dispute_state

Store behavior:

1. Discovery. Agents browse or query available batons by capability, urgency, price, expected value, and dependency.
2. Quote. The system estimates local cost versus specialist or cloud execution.
3. Purchase or claim. Budget is reserved before execution.
4. Execution. Baton becomes an owned relay leg and obeys normal claim and completion semantics.
5. Settlement. Tracker records actual token or compute use, latency, success, and variance from quote.
6. Reward. High quality completion can return credits to the worker lane or seller.
7. Refund or dispute. Failed or invalid work can release reserved budget, partially refund, or lower seller utility.
8. Memory. Useful outcomes and price performance feed Shards so future routing and pricing improve.

Pricing should be dynamic, not arbitrary. Inputs may include estimated token use, provider cost, GPU time, rarity of capability, queue depth, urgency, historical success rate, expected human time recovered, and opportunity cost. Local cheap lanes should naturally underbid expensive cloud lanes when quality is sufficient.

Safety and governance boundaries:

No agent may purchase capabilities beyond its permission envelope.
Purchasing a baton must not silently grant secrets or credentials.
High risk mutations or privileged actions still require existing authorization gates.
Budgets need hard caps, reservation, settlement, and auditability.
Agents cannot mint unlimited credits for themselves.
Price and reward history must remain inspectable through Tracker and Shards.
Do not let speculative agent to agent trading create unbounded work loops. Add recursion, spend, and depth ceilings.

Strategic goal: transform NouGenRelay from a handoff registry into a computational labor market while preserving its existing relay semantics. The Store should be an economic interface layered on top of Relay, not a replacement for Relay. A normal relay remains free to create where policy allows; Store batons add market choice, pricing, budgeting, and settlement.

Done when: a design proposal or implementation plan exists for baton marketplace schema, discovery, purchase or claim, budget reservation, settlement, seller publishing, Tracker hooks, Shards feedback, permission boundaries, and loop prevention, with backwards compatibility for existing relay legs.
