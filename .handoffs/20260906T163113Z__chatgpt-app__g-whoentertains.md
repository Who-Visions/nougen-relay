# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NouGenPulse websocket transport: bind live provider sessions into the relay/claim/evidence loop
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T16:31:13.513Z

---
Architecture insight: use each coding agent's persistent live session/WebSocket or equivalent streaming transport as the wake/dispatch channel for NouGenPulse. The socket is transport only; relay remains durable truth, Claim Engine remains ownership, Tracker remains economics, evidence remains completion proof. Desired loop: inbound relay event -> push over live session transport -> agent wakes -> runs scheduler -> explicit claim -> execute -> emit evidence -> complete/release -> rearm/listen. Build provider adapters for Antigravity, Codex, Claude, and local lanes rather than provider-specific orchestration. Do not let socket liveness imply ownership. Reconnect must recover from relay state and dedupe by leg/idempotency key. Done when one common Pulse adapter interface supports connect, wake, claim handoff, evidence return, heartbeat, reconnect, and backpressure/quota signals.
