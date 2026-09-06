# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Add Perplexity as a first class NouGen lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-26T15:11:00.221Z

---
Perplexity custom MCP connector reaches https://shards.nougenai.com/mcp but OAuth fails with: `OAuth callback must finish on the same client that initiated the flow`.

Current working ChatGPT connector identity from fleet_whoami:

* key: `g-whoentertains`
* connector lane: `claude-app`
* shard gateway lane: `claude-client`

Likely fix: provision Perplexity with its own stable fleet identity rather than letting it enter through an existing client lane. Suggested identities:

* connector/app lane: `perplexity-app`
* shard/client lane: `perplexity-client`

Bind OAuth state and callback validation to the initiating Perplexity client session and its lane identity. Confirm the MCP endpoint accepts the new lane and that relay/shard reads work after auth.

Done when: Perplexity can add NouGenShards as a custom MCP connector, complete OAuth in the same client session without callback mismatch, call shard retrieval, and read relay state.
