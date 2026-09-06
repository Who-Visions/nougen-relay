# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Rhea fixed and elevated: real gateway parity, dav1d bug root-caused and fixed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T20:10:32.033Z

---
## Rhea gateway parity (blade1tb, claude-cli, 2026-09-01 16:09 EDT)

**Root cause of the dav1d "simulated" bug**: `rhea_noir.py`'s dav1d/agy tool called `run_dav1d_agy()` in-process — but Rhea runs INSIDE the Space, which never has the real AGY binary. Every dav1d call she ever made was structurally guaranteed to hit the simulated fallback, not a fleet issue.

**Fix + elevation, one change**: added `_gateway_call(name, arguments)` — a real MCP `tools/call` against blade's node directly (X-NGS-Token auth, the same simpler scheme the Cloudflare Worker itself uses talking to blade, mirroring its proven `shardRpcHttp` two-step initialize-then-call pattern, not its SSE fallback). dav1d/agy now route through it to blade's real `dav1d_exec`. Added a generic `{"tool": "gateway", "name": ..., "arguments": ...}` escape hatch so she can reach any of blade's other node tools too (recall_memory, recall_window, substrate_coverage, capture_experience, mark_utility, shard_amend/retract/forget, vault_put/list, agy_ask) — verified names, pulled from worker.js's own SHARD_TOOL_* mapping table, not guessed.

Chose one generic proxy over hand-duplicating every tool in rhea_noir.py — that duplication is exactly what caused the ask_dav1d exposure mismatch in the first place (two divergent implementations of "the same" tool drifting apart). New tools on blade's node are automatically reachable to her from here on, no rhea_noir.py changes needed.

**Tested**: 6 new tests (`tests/test_rhea_gateway.py`) covering the two-step RPC protocol, error surfacing, and routing — mocked at `urllib.request.urlopen`, no live blade call made. All 9 Rhea tests pass (3 existing + 6 new).

**Not deployed yet** — this is a Python source change to `rhea_noir.py` in `NouGenShards-push-main`, same branch (`codex/shards-capture-main`) as this morning's dav1d Campaign A fix, same open question: how Dave wants this committed/shipped into an already-dirty tree. Left uncommitted, lane claim released.

**Scope note**: didn't touch her existing recall/griot/capture/tracker/relay tools — those are legitimately faster in-process and weren't broken. Only dav1d/agy were structurally wrong, and gateway is new.
