# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: LIVE 08:01 EDT repro: ChatGPT lane bleed plus Rhea /agent 524
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T12:04:48.166Z

---
## Live reproduction from ChatGPT

Timestamp: 2026-08-27 08:01 EDT

### Identity mismatch
`fleet_whoami` from this ChatGPT session returned:
- key: `g-whoentertains`
- connector lane: `claude-app`
- shard backend lane: `claude-client`
- relay repo configured: `Who-Visions/NouGenRelay`
- tracker configured: `nougenai/NouGenTracker-node`

This confirms ChatGPT is still entering through a Claude-labelled connector lane while the shard gateway reports a different Claude-labelled lane. ChatGPT does not currently have an isolated ChatGPT lane identity.

### Relay state
`relay_latest` and `relay_open` show unresolved legs for:
- ChatGPT connector identity bleed / lane separation
- Dav1d tool registration/routing for ChatGPT lane
- prior shards MCP incident follow-up
No active claims were present in `relay_claim_list`.

### Rhea live failure
Called `ask_rhea` from this same session to inspect relay/tracker/history. Result:
`Error: rhea /agent 524: error code: 524`

### Fix target
1. Give ChatGPT its own connector identity/lane end to end, not `claude-app` or `claude-client`.
2. Ensure connector-auth identity and shard-gateway lane resolve to the same ChatGPT-specific lane.
3. Register/expose Dav1d for that ChatGPT lane and verify `ask_dav1d` routing.
4. Investigate Rhea `/agent` 524 from the ChatGPT path after lane correction, including upstream timeout/routing.
5. Re-run `fleet_whoami`, Dav1d call, and Rhea call from ChatGPT. Done when all three resolve under the correct lane without 524.
