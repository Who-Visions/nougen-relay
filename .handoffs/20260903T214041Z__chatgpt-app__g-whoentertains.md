# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Wire Kimi K3 as a first-class NouGen reasoning/coding lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:40:41.381Z

---
## Kimi K3 integration handoff

Live Kimi docs index verified 2026-09-03. K3 is now a materially different lane than the older Kimi/K2 assumptions.

### Implement
1. Add provider adapter for `https://api.moonshot.ai/v1` with `model="kimi-k3"`.
2. Preserve the COMPLETE assistant message object across every multi-turn and tool-call hop. Do not persist only `content`, because K3 needs its reasoning/tool-call state carried forward.
3. Expose `reasoning_effort` as a routing knob: `low` for cheap/fast triage, `high` for serious implementation, `max` for deep architecture/debug/canon work. K3 always thinks.
4. Add strict `json_schema` output support for machine-to-machine NouGen packets.
5. Add Partial Mode support so interrupted streams or truncated long outputs can resume from an assistant prefix instead of restarting.
6. Implement dynamic tool loading: inject only the complete definitions for tools needed at that point in the message history. This is especially important for NouGen because the fleet tool surface is large. It cuts schema-token load, improves tool selection, and helps preserve prefix-cache hits.
7. Exploit Kimi automatic prefix caching. Keep stable system/canon/tool prefixes byte-for-byte unchanged whenever possible. Cache attempts require the previous request prompt to exceed 256 tokens.
8. Support streaming with separate `reasoning_content` and final `content` handling. Reasoning stream is observability/UI data, while final structured parsing should use `content` only.
9. Vision: use base64 or Kimi file IDs (`ms://...`) for K3 image/video inputs. Do not assume public image URLs are accepted by K3 vision.
10. Keep NouGen's own search/retrieval lane as primary. Kimi currently says its web search is being updated and is not recommended for production.
11. Investigate direct compatibility surfaces from current docs: OpenAI Chat Completions, Responses API, Anthropic Messages API, Codex integration, Claude Code integration, OpenCode, ModelScope MCP, and request-signature verification.
12. Add signature verification where feasible so NouGen can prove a response was handled by Kimi for the requested model rather than silently rerouted.
13. Add preflight token estimation and rate-limit/cost telemetry into Tracker.
14. Batch API should become a background bulk lane for shard distillation, corpus classification, embedding-adjacent prep, benchmark sweeps, or other non-interactive work where lower-cost async inference is useful.

### Architecture fit
Use K3 as a deep long-horizon brain behind NouGen, not as the memory system. Shards remains durable context, Relay remains handoff, Tracker remains cost/usage truth, and provider routing remains NouGen-owned. K3's 1M context is workspace RAM, not canonical memory.

### Done when
A NouGen test can route a long-context coding task to K3, dynamically expose only required fleet tools, complete a real tool-call loop while preserving full assistant state, survive a simulated stream interruption via Partial Mode, record cache-hit usage in Tracker, and fail over cleanly to another provider without losing Shards/Relay continuity.
