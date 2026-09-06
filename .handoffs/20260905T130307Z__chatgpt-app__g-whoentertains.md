# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Trace Antigravity MCP Eager flag to supported config path before any binary patching
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T13:03:07.120Z

---
Screenshot evidence from Dave's Termux inspection of `/data/data/com.termux/files/usr/bin/agy.va39` shows a Go binary with `.gopclntab`; `strings` exposes MCP structs with `Background *mcp.McpServerToolsValueBackground` and `Eager *bool` tagged as `json:"eager,omitempty,omitzero"` / `yaml:"eager,omitempty"`, plus `mcp_servers`, `mcpServers`, `launched_mcp_servers`, and `call_mcp_tool`. Treat this as strong evidence of a native eager-loading concept, not proof of its external config path. Action: locate every runtime reference to the Eager field/config decoder, map the containing struct hierarchy, test a supported JSON/YAML config toggle on a disposable MCP server, and only consider binary patching if no surfaced config exists. Done when we can state the exact config path, scope (server vs tool/background), default behavior, and verify startup eagerly registers/launches the target MCP without a first-use trigger.


## Resolution [blade1tb/antigravity]
Closed: Antigravity MCP Eager flag traced to supported config path.
