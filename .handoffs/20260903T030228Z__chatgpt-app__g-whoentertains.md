# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Prepare NouGen chatgpt_wake adapter for future custom MCP event triggers
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T03:02:28.446Z

---
Baseline captured 2026-09-02: ChatGPT Work has supported inbound event-triggered Tasks, but custom MCP apps are not yet documented as direct wake sources. Keep NouGenRelay canonical. Design `chatgpt_wake` as a transport abstraction: Slack/GitHub shadow doorbell now, custom MCP trigger later. Do not bend relay semantics around provider-specific wake mechanics. Done when the adapter boundary is explicit enough that adding an OpenAI custom MCP event source requires only a transport implementation, not relay redesign.
