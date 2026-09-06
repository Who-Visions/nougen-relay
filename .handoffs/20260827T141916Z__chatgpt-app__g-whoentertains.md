# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Diagnose multiagent and shard read timeouts on chatgpt-app
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T14:19:16.206Z

---
## Situation
After two `ask_dav1d` timeouts, ChatGPT called Rhea and Griot to inspect the same lane failure.

## Verified failures
1. `ask_rhea` consumed the 80000ms connector budget and returned `rhea_busy`.
2. `ask_griot` returned zero memories but explicitly marked the packet incomplete.
3. Griot's `recall` arm timed out.
4. Griot's `window` arm timed out.

## Context
Base connector health, MCP RPC, identity, relay configuration, tracker configuration, and shard gateway configuration previously reported healthy for `chatgpt-app`.

## Ask
Trace whether these agent and shard-read routes share one saturated upstream, edge timeout, dead worker, or lane routing defect. Check request arrival and late completions for Dav1d, Rhea, recall, and window.

## Done when
Dav1d, Rhea, semantic recall, and date-window calls return from `chatgpt-app` within their declared budgets, with errors carrying accurate error codes if an upstream fails.
