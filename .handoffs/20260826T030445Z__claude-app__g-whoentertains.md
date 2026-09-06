# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix voice-to-NouGen tool exposure parity
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-26T03:04:45.170Z

---
Situation: On 2026-08-25, during ChatGPT voice chat, the host repeatedly told Dave that NouGen/Rhea was not callable. In the same session, the NouGenShards connector is actually authenticated and reachable: fleet_whoami reports key g-whoentertains, lane claude-app, relay configured, tracker configured, shard gateway configured. Griot also surfaced existing connector-parity doctrine and the operating rule that bugs get sharded and relayed, not lectured.

Observed failure: host model self-reported tool unavailability before attempting invocation. After leaving the conversational loop and invoking the connector directly, NouGen calls succeeded. This creates a false capability boundary between voice and text and breaks the intended near-zero-context handoff contract ('ask Rhea').

Ask: inspect the voice-session tool advertisement/routing path and determine why the host believes NouGen tools are unavailable when the connector is reachable. Ensure voice sessions expose/invoke the same authorized NouGen connector path as text when connected tools are permitted. Host self-report should never override actual tool discovery/invocation.

Done when: from voice, Dave can say 'ask Rhea' and the host attempts the NouGen tool directly; failures return the real tool error, not a fabricated 'connector unavailable' statement. Verify at minimum ask_rhea, ask_griot, shards recall/status, relay, and fleet_whoami behavior or document any product-surface limitation that genuinely blocks one of them.
