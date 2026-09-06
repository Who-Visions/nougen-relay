# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Blade MCP fixed: node flap + missing Dav1d roster entry behind ask_dav1d
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T01:12:53.795Z

---
## Situation
"fix mcp on blade" session (Claude Cli, blade1tb, 2026-08-26 evening).

## Done
- NGS node (127.0.0.1:4444) died AGAIN silently mid-session (PID 7180 gone, same signature as 08/25 death - died during /search). Watchdog from pi-remix leg restarted it (new PID), gateway 502'd only during the flap window. Node restarted clean, shards.nougenai.com/mcp green (health + mcp both up).
- ROOT CAUSE of ask_dav1d: NOT a transport failure. app.py's ask_dav1d/ask_david tools call agents.run_agent("Dav1d", ...) but the roster in src/nougen_shards/agents.py NEVER HAD a Dav1d entry -> every call returned "[roster] No agent named 'Dav1d'".
- FIX (push-main): added Dav1d AgentSpec (Execution / CLI triage persona, model env-first via NOUGEN_AGENT_MODEL_DAV1D fb dav1d:e2b) + alias david->dav1d. Verified in venv: run_agent('Dav1d', ...) -> "Alive. My model name is Gemma 4." Node restarted to serve it.
- Local ollama healthy on 11434 AND 11436 (both answer /api/tags, dav1d:e2b present); startup-probe "tags timeout" was cold-boot transient. ollama MCP launcher (ollama_mcp_launch.py) runs clean.

## Open
- End-to-end /mcp verification of ask_dav1d blocked on token: node runs with NGS_NODE_TOKEN fp 9c67af03a9da but keymaker %NGS_NODE_TOKEN% pattern only surfaces NGS_NODE_TOKEN_SPACE fp 15c96012efbf -> where does start_grid.py load fp 9c67af03a9da from? Investigating.
- Node still dies silently under /search (2nd occurrence). Watchdog masks it; forensics still owed.
- Restarted node reports persistent_storage:false storage:default - confirm that is expected for the local lane.

## Done-when
ask_dav1d answers over shards.nougenai.com/mcp from a remote client.
