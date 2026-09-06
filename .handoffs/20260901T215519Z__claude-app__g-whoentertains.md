# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ask_griot bottlenecks: 8 fixes patched + measured (node + Worker), 2 elevated steps left for Dave: node restart, deploy.py
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T21:55:19.450Z

---
## ask_griot bottleneck pass (blade1tb, claude-cli, 2026-09-01 18:20 EDT)

Mission from Dave: "fix every bottleneck with ask_griot". War-game: `wargames/ask-griot-bottlenecks.md` (outcome table inside). Shard captured with all numbers. Lane claim on app.py / core.py released. Nothing committed; tree still carries other lanes' Rhea + dav1d WIP, untouched.

**Baseline (live node)**: recall_memory 4.6-6.8s, recall_window 3.7-7.1s returning 0 rows for a multi-word question, /health 3.8s during a recall. In-process: era page with no keyword 33.6s (no timestamp index), embed 0.3s per arm, first recall in a fresh process 23.5s (over the 20s federation deadline, local grid silently skipped).

**Node fixes (NouGenShards-push-main, uncommitted)**
1. `core.init_db`: `idx_shards_timestamp` on shards(timestamp DESC). Already built on all 9 live DBs. Era page 33.6s -> 0.06s.
2. `app.py`: recall_memory / recall_window are async + run_in_threadpool. /health no longer stalls behind a recall; warm cost identical to sync (2.2s both).
3. `app.py _window_search`: 9-DB scan on a thread pool (NOUGEN_WINDOW_WORKERS) and FTS MATCH falls back phrase -> AND -> OR. Starved question: 0 rows/7s -> 8 rows/1.4s. Helpers nested inside the function because test_trusted_window execs that FunctionDef alone.
4. `core._embed_query_cached`: LRU (NOUGEN_EMBED_CACHE, default 256), misses not cached. Second arm's embed 0.3s -> 0.
5. `NOUGEN_MCP_DOMAIN_KEY`: "*" = whole-brain single pass, ~1s faster, but parity probe 44% top-5 overlap vs the implicit CWD-fused ranking, so it is opt-in, default unchanged.
6. Lifespan warm-up thread (`NOUGEN_WARMUP=0` disables): first recall after restart 2.6s instead of 20s with the local lane missing.

**Worker fixes (nougen-fleet-mcp/src/worker.js, patched, mocked smoke ALL PASS, NOT deployed)**
7. `shardCallOnce` skips the per-call `initialize` (node is stateless_http); `SHARD_GATEWAY_STATELESS=0` restores it; a "not initialized" reply triggers one handshake + retry.
8. ask_griot window arm has its own `GRIOT_ARM_TIMEOUT_MS` (default 20000) via Promise.race; a late window lands in failures[] while the recall answer is returned.
(`ask_dav1d` from earlier today is in the same file, also awaiting deploy.)

**Two steps need an elevated shell / deploy rights, so Dave:**
- Restart the node (runs elevated; `node_lane.ps1 -Action stop` reports success but PID 84796 survives, Stop-Process = Access is denied from this session): elevated PowerShell in NouGenShards-push-main: `.\tools\node_lane.ps1 -Action stop; .\tools\node_lane.ps1 -Action start`
- Deploy the Worker from nougen-fleet-mcp: `..\NouGenShards-push-main\.venv\Scripts\python.exe deploy.py`
- Then re-time: `.venv\Scripts\python.exe -u <backup dir>\griot_time.py` (copies of every patch script, the smoke test, the timer, pre/post files live in `NouGen\nougen-worker-backups\griot-20260901\`).

**Tests**: 5 node test files, same 3 failures before and after my edits: two deny-by-default tests get 401 not 503 (keymaker supplies the token on blade; auth code untouched by the diff), and test_trusted_window NameErrors on `_normalize_iso_bound`, which another lane's uncommitted WIP added to app.py. Not mine, not fixed, flagging for its owner.

**Ledger**: vault lane (45 stores, ~1.9s regardless of pool size) is now the federated floor; FTS sidecars or a per-lane soft budget are GM calls. Bare `/mcp` on the node 404s while `/mcp/` works (Worker uses `/mcp/`).

**Rollback**: `worker.pre-griot-20260901.js` beside worker.js; node hunks reverse via the patch scripts in the backup dir (never `git checkout -- app.py`, other lanes' WIP lives there).
