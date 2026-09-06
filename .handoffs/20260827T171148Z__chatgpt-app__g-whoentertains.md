# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Agy: set Codex fleet-registry MCP startup timeout to 120 seconds
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T17:11:48.024Z

---
On Blade, Codex v0.150.1 reports `nougenai-fleet-registry` startup timed out after the default 30s. Live config at `C:\Users\super\.codex\config.toml` lines 121-123 is:

```toml
[mcp_servers.nougenai-fleet-registry]
command = 'C:\Users\super\AppData\Local\Programs\Python\Python311\python.exe'
args = ['C:\Users\super\Watchtower\local_search_mcp.py']
```

Add only:
```toml
startup_timeout_sec = 120
```
inside that table, after `args`. Preserve all nested tool approval blocks. 120 is the existing local precedent already used by `[mcp_servers.node_repl]`, not a new arbitrary constant. Validate TOML via `codex mcp get nougenai-fleet-registry --json`, then restart Codex and confirm MCP startup completes. Parent Codex `apply_patch` is blocked by Windows sandbox error `SetTokenInformation(TokenDefaultDacl) failed: 1344`; `codex mcp add` has no timeout persistence flag.
