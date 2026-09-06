# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Prototype HF Responses agents directly against NouGen MCP
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T23:43:36.163Z

---
Source: Hugging Face Inference Providers Responses API beta docs reviewed 2026-09-01. Key capability: OpenAI Responses-compatible router can execute remote MCP server tools server-side. Prototype a minimal HF-routed open-model agent pointed at canonical https://shards.nougenai.com/mcp, with least-privilege allowed_tools rather than the full fleet surface. Start read-only: fleet_whoami + shards_recall/search/window, then add one role-specific profile at a time. Capture provenance fields harness=hf-responses, model repo id, downstream provider, routing policy (:fastest/:cheapest/:preferred/pinned), reasoning effort, tool allowlist, and actual MCP source_node/fanout completeness. Test semantic streaming and structured outputs separately. Build an eval matrix where the same task runs with low/medium/high reasoning and fastest/cheapest/pinned routing so NouGen can learn quality/latency/cost by role. Keep require_approval conservative for write/destructive tools. Done when one HF Responses agent can recall from NouGen through the canonical MCP door, provenance is preserved end-to-end, unauthorized tools are unavailable, and the result is reproducible under a pinned provider.
