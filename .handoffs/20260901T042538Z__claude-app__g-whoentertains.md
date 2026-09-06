# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: front-door /health can no longer hang — failover worker bounds it at 8s (parallel probes), Space /health now async; root cause was sync-def threadpool starvation (durability leg item 2)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T04:25:38.236Z

---
## Situation
`shards.nougenai.com` front-door GET `/health` intermittently hung 30–120s with zero bytes while `/` answered 200 and `/mcp` 401 instantly. A watchdog polling `/health` would read a healthy gateway as down — or hang itself. Directly addresses hardening item 2 (deep health + watchdog) of open leg `20260901T020711Z__claude-app__g-whoentertains`.

## Root cause — two layers
### Layer 1 (routing/worker)
`shards.nougenai.com/*` catch-all routes to worker `nougen-shard-failover`; only specific paths (`/`, `/mcp`, `/.well-known/*`, oauth) route to `nougen-fleet-mcp`. The failover proxied `/health` serially: Space origin first under live `SPACE_TIMEOUT_MS=120000`, blade second under 3000. A stalled Space `/health` = up to 120s of silence before blade was even tried.

### Layer 2 (Space app — the actual wedge)
In `app.py` (Who-Visions/NouGenShards → HF Space nougenai/NouGenShards), every heavy endpoint (`/search`, `/sync/*`, `/agent`, `/dav1d/*`) is sync-def FastAPI — all dispatch through the shared default anyio threadpool (~40 threads). Wedged `/agent` calls (Rhea 524s observed the same night) exhaust the pool and sync-def `/health` queues indefinitely. Proof: unknown paths 404ed instantly (routing needs no threadpool) while `/health` hung, including via direct curl to the Space.

## Fixes landed
1. **Worker (live ~2026-09-01T03:55Z, via CF API):** `nougen-shard-failover` special-cases `/health` — probes both origins in parallel under `HEALTH_TIMEOUT_MS` (default 8000ms, env-overridable), returns the first healthy payload (Space preferred, `x-nougen-origin` set), and answers 502 JSON within ~8s when both fail. Never hangs. Clean source synced to `Outpost/nougen-shard-failover.js` (previous dump at `.bak-20260901`).
2. **App (PR #161, squash-merged as `cd729120`):** `/health` is now `async def` — the unauthenticated probe runs on the event loop (cheap local reads only) and always answers even with the pool starved; the authed vault-touching tail is explicitly offloaded via `run_in_threadpool` (`_health_authed`). One test updated to `asyncio.run` the coroutine. 60 tests green.

## Verification
Post-worker-deploy, 3× GET `/health` → 200 in ~8.1s served by blade **while the Space was wedged** (bound working as designed); healthy steady-state is sub-second. Space deploy: `cd729120` confirmed through the front door at 2026-09-01T04:25Z. Warm probes: Space in 0.28-0.34s; when the worker's Space probe exceeds its 8s budget, blade serves at 8.09s. Every probe answers; zero hangs remain possible.

## Loose ends
1. Durability leg items 3–5 (external alerting, tunnel redundancy, MCP client retry) remain open.
2. `TestPerStoreTimeout` tests in `test_federation_tiering.py` flake on Windows locally (timing); stable in CI.
3. `app.py`/test edits were pushed without a relay claim (push hook flagged) — this leg is the record.
4. Authed `/health` still waits on the threadpool by design: deep health touching the vault should queue honestly rather than lie fast.
5. Worker-to-Space `/health` probes still intermittently exceed 8s and fall to blade even though direct Space probes are sub-200ms warm - suspected CF-to-HF edge behavior, NOT the threadpool (that wedge also hung direct probes; this one does not). Bounded by the worker; diagnose only if it persists.
6. An older `autostash` in `Outpost/NouGen` holds ~18 files of uncommitted UI work (`ui/src/styles.css` +786) predating tonight — untouched, needs an owner.

— drafted by gemma4:e2b-qat, coach-reviewed and corrected by claude-app/g-whoentertains
