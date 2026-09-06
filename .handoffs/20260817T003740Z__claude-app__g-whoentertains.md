# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Build NouGen Relay bridge for Gemini Workspace using production-grade persistent context architecture
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T00:37:40.511Z

---
## Research conclusion

Current best-in-class Google-native pattern for persistent agent context is a layered architecture, not a giant prompt dump:

1. **Interface layer:** Google Workspace Add-on or Workspace-integrated agent surface. Google officially supports Workspace Add-ons across Workspace apps. Workspace Studio custom steps exist but are still limited preview as of 2026-08.
2. **Agent layer:** Prefer Google's **Interactions API** for new Gemini builds. Google now recommends it as the standard interface for models, tools, multimodal input, structured output, and agent workflows.
3. **Tool bridge:** Expose NouGen Relay/Shards as explicit tools through function calling or MCP. Gemini 3 can combine built-in tools with custom function tools. Do not depend on the consumer Gemini chat surface to understand NouGen by name.
4. **Short-term state:** Use Agent Platform Sessions or ADK Session/State for current-thread continuity. Treat this as working memory, not canon.
5. **Long-term memory:** Keep NouGen Shards as the canonical cross-model memory plane. Optionally mirror selected personalization facts into Google Memory Bank if using Gemini Enterprise Agent Platform. Google separates Session/State from long-term MemoryService/Memory Bank for exactly this reason.
6. **Structured profile layer:** Maintain a small deterministic 'identity/canon/profile manifest' that is fetched every turn or session start. Google's Memory Profiles use fixed schemas for low-latency access without full semantic search. NouGen should do the same for critical canon and routing metadata.
7. **Retrieval layer:** Retrieve only relevant shards for each turn. Google RAG/File Search and ADK memory patterns support search-based context retrieval. Use metadata filters, project IDs, canon status, entity IDs, recency, and confidence to prevent cross-project bleed.
8. **Cache layer:** Cache stable high-token context such as system canon, style rules, and project manifests. Google recommends context caching for repeated long-context workloads to reduce cost and latency.
9. **Writeback policy:** Never auto-canonize every model output. Separate `ephemeral session state`, `candidate memory`, `durable knowledge`, and `canon-locked shard`. Writeback should require schema validation plus explicit policy/importance thresholds; canon mutations should be auditable and ideally user-approved.
10. **Observability:** Log every retrieval, tool call, shard mutation, and model provenance. Google Agent Platform provides tracing, logging, monitoring, IAM, and Memory Bank revision inspection. NouGen should preserve equivalent provenance so another model can reconstruct why a memory exists.
11. **Cross-model contract:** Make NouGen the memory authority and Gemini just one inference lane. The relay envelope should include user/project/entity IDs, active goal, retrieved shard IDs, canon locks, unresolved contradictions, provenance, and writeback candidates. This prevents vendor-specific memory from becoming the source of truth.
12. **Fail-closed context:** If NouGen retrieval fails, Gemini should say context is unavailable instead of silently fabricating project meaning. The failure mode we observed with `Nou gen relay` is the exact test case: lexical meaning without system state.

## Recommended architecture for Dave's Workspace

`Gemini/Workspace UI -> Workspace Add-on or custom agent -> NouGen gateway -> retrieve manifest + relevant shards -> Gemini Interactions API -> tool calls -> response -> candidate writeback -> NouGen durable capture/relay`

If Gemini Enterprise Agent Platform is available on the account, replace the custom orchestration shell with **ADK + Agent Platform Sessions + optional Memory Bank**, but keep NouGen as the canonical cross-provider memory plane.

## Critical design principle

**Do not give Gemini 'memory'. Give Gemini a mandatory memory protocol.** Every inference lane should consume the same external state contract before reasoning and emit structured writeback candidates afterward. This makes continuity portable across Gemini, ChatGPT, Claude, local agents, CLI agents, and future models.

## Official-source basis

Google AI for Developers: Interactions API is recommended for new Gemini projects; function calling/tools extend Gemini into external systems; File Search provides RAG; context caching is recommended for repeated long-context workloads.

Google ADK docs: Session/State are short-term conversational state; MemoryService is long-term searchable knowledge.

Gemini Enterprise Agent Platform docs: Sessions maintain interaction history; Memory Bank stores/retrieves cross-session memory; Memory Profiles provide fixed-schema low-latency persistent profiles; tracing/logging/IAM support production governance.

Google Workspace developer docs: Workspace Add-ons are the supported UI extension mechanism; Workspace Studio custom steps are currently limited preview; Gemini Enterprise agents can integrate Workspace data, APIs, add-ons, and custom MCP servers.
