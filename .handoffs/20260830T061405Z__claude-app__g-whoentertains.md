# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ACTUAL ROOT CAUSE: the NGS shard node on :4444 is HUNG (accepts TCP, never answers HTTP). Tunnels/workers were faithfully reporting a dead origin. Connector pile-up was NOT the cause
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T06:14:05.782Z

---
**Supersedes my tunnel framing in** `20260830T051459Z` / `20260830T053312Z` / `20260830T054454Z`.

## The actual fault
`http://127.0.0.1:4444/health` — the real NGS shard node, straight to loopback, no Cloudflare involved:
```
try1 http=000 t=20.003s
try2 http=000 t=20.010s
try3 http=000 t=20.027s   (empty body)
```
**The node accepts TCP connections but never answers HTTP.** It is HUNG, not down — `netstat` shows `0.0.0.0:4444 LISTENING` (PID 37860) with live `ESTABLISHED` connections from cloudflared. Every layer above it — connectors, the failover worker, `nougen-fleet-mcp`, every MCP client — was faithfully reporting a dead origin. There was never a gateway bug.

## Two of my own claims retracted
1. **"The node is healthy, 5ms local"** (`20260830T054454Z`) — WRONG. I probed `127.0.0.1:8765`, which is **Apollo's Sol-Ai mesh port**, not the shard node. `NGS_PORT=4444` is set and 4444 is where the node actually serves. Right method, wrong port; the 5ms result described a different service entirely.
2. **"Stacked connectors caused the outage"** — WRONG, and GM supplied the disproof: Cloudflare explicitly supports running multiple `cloudflared` **replicas** for HA (each tunnel keeps 4 long-lived connections; replicas are a documented feature, not a fault). Replicas against a healthy origin are fine. They all hung because the **origin** hangs. The pile-up was a genuine resource leak worth fixing, but it was a symptom of restart-thrash against a hung node — not the cause of the outage.

The fail-closed guard patch in `tools/start_grid.py` still stands on its own merit (unbounded connector growth is a real defect), but it does not fix this.

## Current state
- Connectors now: only the Windows service `Cloudflared` (PID 23828, `tunnel run --token`, AUTO_START) + the unrelated `tools/bin` quick tunnel → `127.0.0.1:4444`.
- `blade.nougenai.com/health` now returns a fast, consistent **530** (~0.15s) instead of hanging — Cloudflare has no healthy connector/origin. Honest failure beats a hang.
- GM attempted `Restart-Service Cloudflared` from an elevated shell; it stalled on `Waiting for service to stop...` — consistent with a connector wedged against a non-responsive origin.
- `.scratch/ngs_node.log` is **empty** (no tail output), so the node is not even logging — reinforcing a hard hang rather than an error loop.

## The fix — restart the NODE, not the tunnel
```
taskkill /PID 37860 /F
```
then relaunch it (scheduled task `NouGen NGS Node` → `tools/ngs_node_boot.cmd`, or `tools/start_grid.py`). Everything upstream should recover on its own once 4444 answers, because the tunnel path is otherwise intact.

**Do NOT** kill `23828` (the service — it is the intended sole connector and auto-restarts) or `52932`/current `tools/bin` quick tunnel PID.

**Done-when**: `curl http://127.0.0.1:4444/health` returns 200 fast; then `blade.nougenai.com/health` stops 530-ing; then `shards_search` returns real hits instead of `(no matches)`.

## Method lesson (third correction this session, same shape)
Every wrong turn tonight came from trusting an inherited value instead of probing the live one: a code default for `SHARD_GATEWAY_STYLE`, a stale 530/500 claim, and a wrong port for "the node". Probe the exact thing you are about to make a claim about — including which port the service you are naming actually listens on.
