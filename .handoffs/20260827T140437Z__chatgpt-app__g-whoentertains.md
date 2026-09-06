# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix ask_dav1d timeout while MCP and shard health remain green
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T14:04:37.819Z

---
Situation: On 2026-08-27, chatgpt-app invoked ngs_v2 ask_dav1d with a trivial prompt. It ran ~70s then returned `Error: The operation was aborted due to timeout` with structured `INVALID_ARGUMENT`. shards_status reports health 200 and MCP RPC OK; fleet_whoami is configured. Vault says Dav1d resolves env-first from NOUGEN_AGENT_MODEL_DAV1D, fallback dav1d:e2b, on Blade Ollama. Kaedra/phoebus is separately inaccessible because KAEDRA_GATEWAY_TOKEN is not configured here; Mac/phoebus being down should not explain Dav1d unless routing drifted.

Ask: On Blade, probe the resolved Dav1d model and Ollama base URL from the live node process, verify the model exists and generate directly, inspect ngs_node.log around the timeout, then fix the dynamic route/timeout or model availability. Restart only the scoped node/service if needed.

Done when: ask_dav1d returns a short answer end-to-end through the token-gated MCP connector, with runtime evidence and the resolved host/model recorded.
