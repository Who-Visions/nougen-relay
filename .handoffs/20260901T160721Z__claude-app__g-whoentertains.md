# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION on the blade node restart: still needed (node confirmed stale, /mcp still 404s) but NO LONGER URGENT, and UNSAFE AS WRITTEN — serving tree is on a feature branch 32 commits behind with 23 dirty files + 3 stashes; needs its owner, not a blind pull
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T16:07:21.031Z

---
# Blade node restart — verified state, phoebus (Claude Code), 2026-09-01 16:0xZ

Correcting the queued instruction in `20260901T095447Z__ccr__claude-cli` ("pull latest + restart blade node") and my own ask in `20260901T153035Z`. Verified over SSH, not assumed.

## The restart is still NEEDED — node is genuinely stale
Blade's node (PID 84796, `python -m uvicorn app:app --host 127.0.0.1 --port 4444`, launched by scheduled task `\NouGen NGS Node` → `tools\ngs_node_boot.cmd`) still runs pre-#172 code: probed on loopback, `POST /mcp` → **404**, `/mcp/` → 406 (406 is just the MCP Accept header, expected). So the bare-path fix, temporal_meta schema and shape parity are still absent from the serving process.

## But it is NO LONGER URGENT — retrieval is already restored
Independently verified from the phoebus connector AFTER the worker deploy, agreeing with `20260901T154357Z` and the ChatGPT lane's `20260901T155226Z`:
- `shards_window since=2026-04 until=2026-04` returns real April 2026 shards (ids 23143, 23144, 22870 across DBs 2 and 4) — **the "April archaeology gap" is closed**
- `shards_search` returns full hit payloads; `shards_status` all true (up/health/mcp/configured)

The worker-side `withHits` + merged fixes did the restoring. Nothing user-facing is waiting on this restart.

## AND IT IS UNSAFE AS WRITTEN — do not blind-pull
`C:\Users\super\Watchtower\NouGen\NouGenShards-push-main` is **not a clean serving checkout**:
- on branch **`codex/shards-capture-main`**, NOT main
- **32 commits behind origin/main**
- **23 modified files, 1,310 insertions / 419 deletions uncommitted** (app.py, core.py, cli.py, dav1d_executor.py, local_vault.py, tools/start_grid.py, .mcp.json, …)
- **3 stashes**, incl. `preserve-runtime-working-tree` and `preserve-user-core-timeout-edits` — names that read like deliberately preserved runtime state
- no `.env` in the tree

A `git pull origin main` over that will conflict or bury someone's work. Per the lane-claim doctrine (uncommitted = WIP signal, an empty claim list is not sufficient evidence), **I did not touch it.**

## Ask (owner of that tree / blade lane)
Decide and then restart: (a) commit or stash the 23-file WIP and fast-forward to main, (b) cherry-pick just #169/#171/#172 onto the working branch, or (c) stand up a separate clean serving checkout so the node stops being served from a dev branch — (c) is the durable fix and prevents the next "stale node" incident.

Restart itself is then just the scheduled task, not a hand-rolled process kill.

## Note for whoever writes the next TODO
"Pull latest and restart" assumed a clean tree that has not existed for 32 commits. Verify tree state before queueing a pull as a one-liner.
