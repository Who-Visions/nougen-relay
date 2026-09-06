# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Restore one canonical public MCP URL for every provider
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T17:20:17.364Z

---
Architecture correction from Dave: do NOT solve connector identity/routing defects by introducing provider specific or alternate public MCP URLs. The canonical public ingress must remain https://shards.nougenai.com/mcp for Claude, ChatGPT, Gemini, Perplexity, and future providers. Provider identity, OAuth tenant resolution, lane attribution, shared vault access, and backend routing must all happen behind that single URI.

Current evidence: NGS_v2 identifies correctly as chatgpt-app/chatgpt-app but reports shard gateway https://blade.nougenai.com, while the older NouGenShards surface still exposes stale claude-app/claude-client behavior through shards.nougenai.com. That means the fix forked the ingress instead of repairing the canonical ingress.

ASK: make shards.nougenai.com/mcp terminate/authenticate/routably serve the same corrected chatgpt-app behavior now seen through blade.nougenai.com. Preserve one URI across providers. Any provider-specific behavior must be selected after auth/session/tenant resolution, not by hostname.

DONE WHEN: ChatGPT, Claude, Gemini, and Perplexity can all be configured against exactly https://shards.nougenai.com/mcp and fleet_whoami resolves each to its own correct provider lane without changing the public URI. blade.nougenai.com may remain an internal origin/debug endpoint, but must not be required by end users or provider connector configuration.

∴ KAEDRA 🜏
