# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix live canonical MCP split brain without minting another URL
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T17:58:30.163Z

---
Live ChatGPT reproduction, 2026-08-27 ~13:57 ET.

Existing canonical ingress task remains the correct architecture: https://shards.nougenai.com/mcp must be the single public MCP endpoint for Claude, ChatGPT, Gemini, Perplexity, and future providers.

Current evidence from the SAME ChatGPT session:

1. NouGenShards.fleet_whoami
   - key: g-whoentertains
   - connector lane: claude-app
   - shard gateway: https://shards.nougenai.com
   - shard lane: claude-client

2. NGS_v2.fleet_whoami
   - key: g-whoentertains
   - connector lane: chatgpt-app
   - shard gateway: https://blade.nougenai.com
   - shard lane: chatgpt-app

3. NGS_v2.shards_status
   - up=true
   - health_up=true
   - mcp_up=true
   - configured=true

Diagnosis: split-brain connector configuration. The older/public NouGenShards surface still binds ChatGPT to Claude identity while NGS_v2 binds it correctly, and the two surfaces expose different gateway origins. This is not a reason to create another public endpoint.

Required fix: make https://shards.nougenai.com/mcp the single public ingress, resolve each provider tenant/lane behind it, and ensure ChatGPT presents as chatgpt-app on the canonical surface. blade.nougenai.com may remain an internal origin only.

Do not mint a new provider-specific URI or hostname.

Done when: from ChatGPT, the canonical NouGenShards connector reports connector lane chatgpt-app and shard lane chatgpt-app while still entering through shards.nougenai.com/mcp, and Claude continues to resolve as its own Claude lane through that same public URL.
