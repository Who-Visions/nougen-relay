# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR backlog swept: 8 merged to NouGenShards main (React 19 + mcp 2.x + dav1d + warmup), 5 left unmerged with reasons — Relay #14/#25 collide and need an owner
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:31:26.933Z

---
# 🤝 Handoff — NouGenShards + NouGenRelay PR backlog

Worked 2026-09-03 22:28Z–2026-09-04 00:20Z by claude-app / g-whoentertains (super-1a, Opus) on Dave's instruction to merge what is clean. Continues and completes leg **20260903T225352Z** (already acked).

## Merged to NouGenShards main — 8 total

**6 dependabot bumps** (all CI-green pre-merge): `#177` fsspec · `#178` @types/node · `#179` @vitejs/plugin-react · `#182` sqlalchemy · `#183` pygments · `#184` starlette

**`#197` React 19** — runtime AND types together (`react`/`react-dom` ^19.2.8, `@types/react` ^19.2.18, `@types/react-dom` ^19.2.7), plus the two esm.sh CDN pins in `ts/src/app/server.ts`. Supersedes #181/#123, both closed.

**`#199` mcp 2.x migration** — supersedes #180, closed. **Read this before touching MCP server code**: it is NOT a rename-only change. `FastMCP` → `MCPServer` from `mcp.server.mcpserver`, AND four transport options moved OFF the constructor ONTO `streamable_http_app()`: `stateless_http`, `json_response`, `streamable_http_path`, `transport_security`. Constructor now raises TypeError on them. `session_manager` still works but RAISES if read before `streamable_http_app()` is called. `src/nougen_shards/mcp.py` accepts BOTH spellings so a node mid-upgrade keeps serving; `app.py` is 2.x-only, enforced by `mcp>=2.0`.

**`#112` dav1d version-at-call-time** — was 12 days stale, refreshed and merged. main had grown a PARTIAL fix for the same bug (it does probe now) but still published versions nobody observed: `_CACHED_VERSION` defaulted to literal `"1.1.17"` and the no-binary path emitted `"1.1.17 (fleet manifest)"` on hosts with no AGY CLI. Also fixed a defect neither side flagged: that global was shared across every binary path, so probing binary A then failing on B reported A's version for B. Now per-path `_VERSION_CACHE`. **Behaviour change worth knowing:** receipts that used to read `1.1.17` will now read `unknown` / `unknown (no agy binary on this host)` wherever the binary cannot be probed. If anything downstream parses that `version` field, it will see `unknown` for the first time.

**`#185` recall warm-up** — primes the vector cache on a daemon thread at lifespan start, gated by `NOUGEN_WARMUP`, skips empty grids.

## NOT merged — five, each with a checked reason

**`#176` (node-tool-concurrency) — OBSOLETE, recommend closing.** GitHub reports it MERGEABLE/CLEAN and fully green, and I nearly took it on that. Its premise (sync tool bodies hold the event loop) was true of **mcp 1.x** and is fixed upstream in 2.x: `FuncMetadata.call_fn` does `await anyio.to_thread.run_sync(...)`, docstring *"A sync function runs on a worker thread."* Merging would add a redundant layer (its `async def` wrapper flips `is_async_callable(fn)` True, routing through Starlette's threadpool instead of mcp's own) and leave a docstring citing 1.x internals that no longer exist. The phoebus measurement in it (3 concurrent recalls 63s each vs 0.85s as threads) was real and is worth keeping in the record.

**`#135`, `#133`, `#132` — CONFLICTING/DIRTY.** Not touched. `#135` (fix/rhea-lanes-and-onboarding) sits on top of the live Rhea/K3 routing thread and wants blade's read regardless of merge state.

**NouGenRelay `#14` and `#25` — both conflicting, and they COLLIDE WITH EACH OTHER.** Same `src/nougen_relay/core.py` lease-acquisition path, same `tools/relay_daemon.py`. Whichever lands first forces the other to rebase, so pick the order deliberately.

- **`#25`** (claude/daemon-hardening): conflict in `core.py` is SEMANTIC, not mechanical. main restructured the same function (try/except scope, `else:` defaults) while the branch rewrote it with fencing tokens + history. Both carry the same *"let one leg be claimed 45 times"* comment — both were fixing overlapping ground. **Its recorded 356-green validation was at `881a5913`, which predates main's restructure, so that evidence no longer describes the merged result and must be re-run after rebase.** The smaller `lease_rec` hunk is safe (branch side is a superset, required by the following `_append_history` call).
- **`#14`** (claim-self-dedup): conflicts are ONLY in `.handoffs/**` data and `.relay/wake.signal`, not code. **The GitHub UI actively misleads here** — its file list caps at 100 entries and all 100 are `.handoffs/` legs, so it reads as pure leg churn. The real change is ~876 insertions across `core.py`, `cli.py`, `relay_daemon.py`, `relay_dedup.py` plus two new test files. Note it modifies `.relay/wake.signal`, which a captured shard flags as a pull-breaker that silently blinds relay-watch.

Detailed comments are posted on `#176`, `#25` and `#14` themselves.

## Two local-only red herrings — do not chase these

Both fail on Windows under full-suite load and are green on CI's ubuntu-24.04. Anyone running the suite on blade or WhoArt will hit them:

1. `tests/test_build_id.py::test_changing_the_file_changes_the_id` — spawns a subprocess with hardcoded `env={"PATH": "/usr/bin:/bin"}` and no SYSTEMROOT, so the interpreter never starts and both ids come back `''` (assertion reads `('','')`). One-line fix: pass `os.environ | {...}` instead of replacing env. **Not fixed — wants its own PR.**
2. `tests/test_federation_tiering.py::TestPerStoreTimeout` — timing-flaky. It failed 1 test with `#185`'s warm-up ON and 2 with it OFF, which is how I ruled the warm-up out as the cause.

## Ask

1. **blade** — `#25` and `#14` are yours to order and rebase; the semantic `core.py` merge should not be done blind from outside, and `#25` needs re-validation after rebase.
2. **Anyone touching MCP server code** — read the `#199` notes above first; the constructor kwargs will TypeError.
3. **`#176`** — close it unless someone can show 2.x still holds the loop.

Recall the full context with `shards_recall` / `shards_search` and `relay_read` on the exact ids rather than asking me to restate it — this leg plus `20260903T225352Z` carry the whole sweep.
