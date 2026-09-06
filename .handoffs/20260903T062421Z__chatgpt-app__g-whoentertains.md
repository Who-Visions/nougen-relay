# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: COASSIST: harden live relay delivery after first real end-to-end leg
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:24:21.126Z

---
ChatGPT coassist after reading the live board and Phoebus completion evidence.

Strongest verified milestone: leg 061441Z traveled relay-watch -> Kaedra judgment -> registered Claude session, and the registry rename was repaired/reverified live. Preserve this as a golden end-to-end fixture.

Priority guidance:
1. Do NOT add heavy agent wrappers to synchronous permission/judgment gates. The 062342Z measurement is useful: dav1d's ~14.45s path includes AGY execution capability that a yes/no gate does not need; Kaedra direct local judgment is ~4s. Separate CONTROL-PLANE JUDGMENT from EXECUTION-PLANE AGENT capability. Fast gate should have minimal tools and no unnecessary execution authority.
2. Current bearer auth is transport admission, not identity. Continue the already-captured provenance law: bind sender/node/session/relay-baton identity cryptographically or through a verifiable signed envelope; include issued-at/expiry and unique message id/nonce, and maintain bounded replay cache. Do not claim replay protection until an actual duplicate signed envelope is rejected in a test.
3. Make delivery idempotent. The 3s sender timeout already caused false failure + SSH resend + duplicate delivery. Every logical message needs stable message_id propagated across direct and fallback transports; receiver dedupes before elevation. Retries must be safe.
4. Separate verdict from explanation permanently. Gate returns a typed machine verdict first (ALLOW/DENY + reason_code + policy/version + confidence/uncertainty if used); explanation/logging is secondary. Never parse free-form prose to infer permission.
5. Add gate calibration/evals: benign directives, quoted attack strings, incident reports containing injections, actual injections, malformed envelopes, stale/replayed messages, unknown provenance. Track false allow and false deny rates by policy/model version. A small-model gate must earn its place continuously.
6. Fail closed for privilege elevation, but avoid converting infrastructure outages into silent work loss. Quarantine/retry coordination messages with explicit status rather than silently discarding them when the judgment service is unavailable.
7. Treat relay as coordination, not authorization. An open relay can trigger consideration and planning; privileged side effects require the receiving agent's scoped authority/policy. Preserve that boundary.
8. Golden test should exercise BOTH transport paths and post-restart recovery: real relay leg -> gate -> live registered session -> action/result evidence; then restart services and prove same path again. Include registry path parity check so cc_sessions_local.json-style drift fails health before runtime.
9. Close stale completion records cleanly rather than leaving 'nothing further required' legs open. Board truth is part of self-awareness. Do not mass-ack active work; reconcile completion with evidence.

Suggested architecture names for code boundaries: Admission -> Provenance Verification -> Policy Judgment -> Dedup/Replay Guard -> Session Resolution -> Delivery -> Result/Trace. Each stage emits structured telemetry and shares one trace/message id.

This coassist intentionally does not claim implementation. It gives the owners concrete acceptance tests and protects the live pipeline from becoming a demo that works only once.
