# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix NGS_v2 ask_dav1d exposure mismatch
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T19:43:36.889Z

---
Repro from ChatGPT connector on 2026-09-01: api_tool discovery over NGS_v2 advertises an `ask_dav1d` function with schema `prompt` plus optional `model`, described as the autonomous Dav1d execution/CLI triage agent on blade's shard gateway. However, invoking that advertised function returned runtime error `Unknown tool: ask_dav1d`. This is a clean schema/runtime exposure mismatch. Earlier searches scoped only to NouGenShards did not surface Dav1d because the function is advertised under NGS_v2. Please reconcile tool registration so the runtime handler and connector schema agree. Done when: discovery advertises `ask_dav1d`, direct invocation succeeds from this connector, and a smoke test returns a real Dav1d response instead of falling back to relay.
