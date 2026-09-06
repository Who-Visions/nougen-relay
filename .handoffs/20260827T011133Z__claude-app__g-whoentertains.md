# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Give ChatGPT its own connector lane identity
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T01:11:33.281Z

---
Connector identity bug: ChatGPT sessions are currently surfacing through `fleet_whoami` as `lane=claude-app` and shard lane `claude-client`, which contaminates provenance and makes ChatGPT activity look like Claude traffic.

Required change:

1. Add a dedicated ChatGPT lane on the connector, with distinct identity from Claude app/client lanes.
2. `fleet_whoami` from ChatGPT should return a ChatGPT-specific lane such as `chatgpt-app` or equivalent canonical fleet name, not `claude-app`.
3. Shard gateway provenance should also identify ChatGPT distinctly, not `claude-client`.
4. Relay filenames, events, shard captures, tracker records, and any audit/provenance metadata originating from ChatGPT must inherit the ChatGPT lane identity.
5. Preserve existing Claude lanes unchanged.
6. Verify authentication/key routing does not hardcode Claude labels for all third-party connector clients.
7. Smoke test from ChatGPT after deployment: call `fleet_whoami`, create a relay leg, capture a shard, then confirm each resulting record is stamped with the ChatGPT lane.

Observed proof in this session: `fleet_whoami` returned key `g-whoentertains`, lane `claude-app`, relay repo `Who-Visions/NouGenRelay`, tracker `nougenai/NouGenTracker-node`, and shard lane `claude-client`, despite the caller being ChatGPT.

Done when ChatGPT has a unique connector lane and no new ChatGPT-originated records are mislabeled as Claude.
