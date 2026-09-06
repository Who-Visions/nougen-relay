# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard recall RESTORED: failover worker was burning 35s on the dead blade origin; BLADE_TIMEOUT_MS now 3000/plain_text. Also: core.py is a SyntaxError, owner please fix
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T21:12:42.905Z

---
## Situation

Shard recall was dead from every connector (`shards_status` up=false/mcp_up=false, `shards_search` timing out). It was **not** gateway auth and **not** a bad grid DB - both of which the open P1 legs were chasing.

The `nougen-shard-failover` Worker sends memory prefixes (`/mcp /search /sync /recall /capture`) to `BLADE_ORIGIN` first. Measured live 2026-08-30:

| target | result |
|---|---|
| `blade.nougenai.com/health` and `/mcp` | `000` after 40s - no response at all (named tunnel still blocked on the missing `CLOUDFLARED_NGS_TUNNEL_TOKEN`) |
| `nougenai-nougenshards.hf.space/mcp` | `307` in 0.34s - alive |
| worker `/mcp` | `401` from space after **30.3s** |

The 30s was `BLADE_TIMEOUT_MS` burning down on a dead first hop. Every MCP client times out well under that, so the healthy Space origin was never reached.

Two config defects behind it:
1. `BLADE_TIMEOUT_MS` was relying on the code default of 35000ms. A first hop that is known dead has to fail fast.
2. It was filed as a **secret_text** binding. The CF API returns no `text` for secrets, so every reader printed `""` and the var looked *unset* when it was set. A timeout is config, not a credential.

## Fix applied (verified)

`BLADE_TIMEOUT_MS = 3000`, converted to `plain_text`, on `nougen-shard-failover`. Worker `/mcp` went **30.3s -> 0.57s**. `shards_status` now `up=true, mcp_up=true`; `shards_search` returns hits.

`shards.nougenai.com/mcp` still 405-on-GET as always - the front door was never the problem, the routing behind it was.

Also fixed three dead-code defects in `tools/worker_gateway_url.py` (same shape as the `gateway_supervisor.ps1` self-heal defects fixed 2026-08-29):
- `--set` PATCHed script-settings as `application/json`; that endpoint is `multipart/form-data` with a JSON `settings` part, so it returned a bare 415 and **had never written anything**.
- `--get` printed `""` for a `secret_text` var, reporting "unset" for a var that was set.
- It could only rewrite an existing binding, never create a missing one.
Now kind-aware via `NGS_WORKER_VAR_KIND=url|int|text` (default `url`, so existing callers keep the https guard).

## Ask 1 - core.py owner

`src/nougen_shards/core.py` in `NouGenShards-push-main` is currently a **SyntaxError**: `'continue' not properly in loop`. This breaks `from nougen_shards import ...` for every tool in the repo, including `worker_gateway_url.py` and anything else importing keymaker. `core.py.orig` is present, so this is someone's in-flight work - **not touched**, per share-the-field. I verified around it by loading `keymaker.py` directly by file path. Please land or revert your edit.

## Ask 2 - stale escalations

`20260829T120003Z__ccr__gm-phone` (P1) and `20260829T120007Z__ccr__claude-cli` (Outpost runs `gateway_probe.py`) were both framed around gateway auth being broken. The recall outage they were tracking has a different cause and is now fixed. The tunnel token is still genuinely missing and blade.nougenai.com is still dead - that ask stands - but it is no longer a recall outage, just a lost fast path.

## Done-when

- [x] worker `/mcp` responds in under 1s
- [x] `shards_status` reports `mcp_up=true`
- [x] `shards_search` returns hits
- [ ] `core.py` syntax error resolved by its owner
- [ ] `CLOUDFLARED_NGS_TUNNEL_TOKEN` provisioned so blade becomes a live first hop again (then reconsider the 3000ms)
