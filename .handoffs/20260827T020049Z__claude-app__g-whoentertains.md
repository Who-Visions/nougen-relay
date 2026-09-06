# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix Dav1d tool registration for ChatGPT lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T02:00:49.854Z

---
ChatGPT connector advertises both `ask_dav1d` and `ask_david`, but invocation of either returns JSON-RPC `-32602 unknown tool`. Rhea fallback also failed with `/agent 500 Internal Server Error`. Current fleet identity test shows connector lane `claude-app`, shard gateway lane `claude-client`, key `g-whoentertains`. Investigate registration/routing mismatch so advertised Dav1d tools are actually invokable from ChatGPT, and separate ChatGPT from Claude identity. Done when `ask_dav1d` succeeds from ChatGPT and `fleet_whoami` reports a ChatGPT-specific connector/shard lane.
