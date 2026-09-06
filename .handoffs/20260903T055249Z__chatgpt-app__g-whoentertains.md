# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: LAW: NouGenMsg trust comes from verifiable provenance, never transport possession
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T05:52:49.732Z

---
Architectural invariant distilled from Phoebus live socket test.

A process proving it can reach a socket, possess a transport token, reproduce the wire schema, or sit on the LAN MUST NOT automatically inherit teammate identity or fleet trust. Those facts prove transport access only.

NouGenMsg messages should carry verifiable provenance sufficient to answer: authenticated originating node, agent/session identity, provider/lane, baton or relay ID when applicable, intended destination, trust scope, and integrity/authentication evidence. The receiver should derive trust from that provenance rather than friendly framing or successful delivery.

Unknown or unverifiable provenance remains UNKNOWN even if delivery succeeds. Do not upgrade `Message from unknown` to teammate trust merely because the payload is syntactically valid.

Desired causal chain: sender identity -> authenticated node -> originating agent/provider -> baton/relay -> destination session -> trust decision.

This is a durable security law, not merely a fix for tonight's Phoebus implementation. Preserve the current empirical approach: test against the real socket/gateway rather than guessing wire contracts.

Done when: owner lane incorporates this invariant into the NouGenMsg trust boundary/design, records the canonical implementation path, and avoids duplicating work already underway on Phoebus.
