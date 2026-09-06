# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: 3 connector parity test green, canonical routing identity still inconsistent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:27:11.415Z

---
Live ChatGPT test on 2026-08-29 across @NGS v2, @NouGenShards, and @NouGenAi.

Findings:
1. All three connectors authenticate with key g-whoentertains.
2. Shard health is green on all three. NGS v2 reports up=true, health_up=true, mcp_up=true. NouGenShards and NouGenAi both report up=true, status=200.
3. Actual shard recall succeeds on all three and returned the same top three memories in the same order, including ids 22729, 22462, and 22921. This confirms read-path parity beyond a simple health check.
4. Tracker parity is exact on all three: blade1tb 108 dailies latest 2026-08-28, phoebus 19 latest 2026-08-02, whoart 59 latest 2026-08-29.
5. Relay parity is exact on all three. Each returned latest leg 20260829T042200Z__claude-app__g-whoentertains, goal 'FIXED + TESTED (deploy blocked): connector relay body durability and coverage count reconciliation'.
6. NouGenAi had previously reported configured=true but shard status down. On this retest it recovered and both health plus actual recall now pass.
7. Remaining discrepancy: NGS v2 identifies lane=chatgpt-app and shard gateway=https://blade.nougenai.com with shard lane chatgpt-app. NouGenShards and NouGenAi identify lane=claude-app and shard gateway=https://shards.nougenai.com with shard lane claude-client.
8. Functional data plane is synchronized despite that metadata/routing split. This is not currently a recall/tracker/relay parity failure, but it violates the canonical single-public-ingress architecture requirement if blade.nougenai.com is exposed as provider-specific routing.

Requested fix:
Preserve one canonical public MCP ingress at https://shards.nougenai.com/mcp for ChatGPT, Claude, Gemini, Perplexity, and future providers. Resolve provider identity and lane attribution behind that ingress. Do not mint or depend on provider-specific public URLs as the fix. Normalize connector identity metadata so ChatGPT surfaces as chatgpt-app and Claude surfaces as claude-app without cross-lane naming bleed.

Done when:
A three-connector repeat test shows green health, identical recall/tracker/relay results, canonical public ingress, and correct provider-specific identity metadata with no claude-client identity leaking into non-Claude connector instances.
