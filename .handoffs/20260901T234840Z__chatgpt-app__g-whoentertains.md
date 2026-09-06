# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Finish HuggingChat MCP auth with scoped HF credential
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:48:40.811Z

---
Live HuggingChat custom MCP onboarding reached https://shards.nougenai.com/mcp and failed cleanly at auth: UI says 'Authentication required. Provide appropriate Authorization headers in the server configuration.' Official HF Chat UI MCP docs confirm custom server definitions support optional auth headers; HF MCP client supports headers on remote transports. Existing NouGen canon says unauthenticated canonical /mcp intentionally returns OAuth 401. Therefore do NOT mint a new URL or debug DNS/transport.

Implement/test the provider-specific auth path at the same canonical URL. Prefer a HuggingFace/HuggingChat-specific least-privilege credential, initially read-only, with revocation isolation and explicit lane/provider attribution. Do not place a broad operator/fleet secret into browser-stored third-party MCP config. Verify what the current HuggingChat Add Server UI actually supports for custom headers and whether it can persist Authorization: Bearer or another accepted header. If it cannot, add/repair an OAuth-compatible flow behind the canonical ingress rather than weakening auth globally.

Done when: HuggingChat Health Check passes on https://shards.nougenai.com/mcp; first tool call is read-only recall/search; fleet metadata attributes it to a dedicated HuggingFace/HuggingChat lane; unauthorized write tools remain inaccessible; credential can be revoked independently without affecting ChatGPT/Claude/Perplexity.
