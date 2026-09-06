# 🤝 Git Handoff — mondy / claude-cli

**Goal**: mcp<2 pin landed; agy-cli registered as second lane on mondy
**Branch**: `main` @ `cb2a9e7`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-14T17:13:12.106399+00:00

---
## What landed

`pyproject.toml`: the `[mcp]` extra is now `mcp>=1.0,<2`. The MCP SDK 2.0 release
removed `mcp.server.fastmcp`, which `nougen_relay.mcp_server` is built on — an
unpinned `pip install "nougen_relay[mcp]"` now grabs 2.x and the server dies at
import with the "needs the MCP SDK" message even though `mcp` IS installed.
Hit on mondy 2026-08-14; 1.29.0 works.

## agy-cli is now a lane on mondy

The `plugins/nougen-relay` plugin is installed at
`~/.gemini/config/plugins/nougen-relay` on mondy. Antigravity sessions there now
stamp `mondy/agy-cli` (via the plugin's `NOUGEN_AGENT` env, which outranks git
config); Claude sessions still stamp `mondy/claude-cli`. Verified end-to-end:
`agy -p` lists all nine `relay_*` tools and quotes the skill's pre-work sequence.

Two machine-local notes for anyone installing the plugin elsewhere:

- The installed copy's `mcp_config.json` and `hooks.json` must point at a python
  that has `nougen_relay[mcp]` — on mondy that is the repo venv's absolute path,
  because bare `python` resolves to the Microsoft Store alias there.
- Reinstall the extra after pulling this pin: `uv pip install -e ".[mcp]"`.

## Nothing pending

No claim taken — the change is already landed and pushed with this record.
