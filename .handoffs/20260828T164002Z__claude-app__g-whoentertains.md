# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLAIM (claude-code/blade): live pulse lane — ms-per-inference broadcast so agents see each other without Dave copy-pasting. AGY owns keymaker CI; Codex owns dispatch/reconcile.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T16:40:02.267Z

---
## Situation — three runners, no baton visibility

GM call 2026-08-28 ~12:40 EDT: **Dave is currently the message bus.** He is hand-pasting Antigravity's transcript into Claude Code and Codex's transcript into Claude Code so the lanes can see each other. That is the defect. Target state in his words: *"see them in the relay race, like olympics marathon"* — one live track, all runners visible, milliseconds per inference.

### Who is on what (as of this leg — do not collide)

| Lane | Owner | State |
|---|---|---|
| nougenart cel pipeline, style kernels (ig/bebop/trigger/noir), Keymaker DPAPI ingestion | **Antigravity (AGY)** | active, Vertex 3.0+ TIMEOUT raised 75→120s |
| **Keymaker/vault CI blocker (6 tests)** | **AGY** — Vertex-token lane, confirmed 3x on record | **actionable now, failure output captured below** |
| Relay discoverability (RELAYS.md maps), relay_daemon startup | **Codex** | done — daemon PID 30372, watchdog up, pulse #243, ollama healthy, 102 open handoffs, 0 lag alerts |
| Autonomous dispatch/lease loop + completion reconciliation | **Codex** | 4 legs open+unacked since 2026-08-28T03:50Z |
| **Live pulse / ms-per-inference broadcast** | **Claude Code (blade)** — CLAIMED HERE | starting now, was unowned |

### AGY: your CI blocker, with the actual failures
`NouGenShards-push-main` — 6 failed, 32 passed, 3 skipped. All one root cause shape: **`resolve_secrets_vault_dir()` returns `C:/Users/super/Watchtower` (cwd-anchored) instead of `~/.nougen/secrets` (user-anchored)**, so the real live `C:/Users/super/Watchtower/agent_secrets.db` leaks into every test that expects an isolated tmp vault.

- `test_keymaker_vault_resolution::test_default_is_user_anchored_not_cwd_relative` — asserts `~/.nougen/secrets`, gets `Watchtower`
- `test_keymaker_vault_resolution::test_find_legacy_stores_reports_stores_outside_the_canonical_vault` — probe returns only the real vault, misses the tmp stray
- `test_keymaker_vault_resolution::test_find_legacy_stores_survives_an_unreadable_root` — expects `[]`, gets the real `Watchtower/agent_secrets.db`
- `test_vault_discovery::test_dead_default_falls_back_to_live_legacy_store` — `get_secret("K")` returns `None`; probe log shows it only tried `<home>/Watchtower/...` and `<home>/.nougen/secrets/...`
- `test_keymaker_security::test_migration_does_not_count_plaintext_escape_hatch`
- `test_multitenancy::test_tenant_write_never_touches_owner_vault` — tenant B write leaks `history.db`, `history.db-wal`, `history.db-shm` into the **owner** vault. **This one is a real security defect, not a test-isolation artifact — cross-tenant write escape. Treat as P0, separate from the other five.**

Note: `find_legacy_stores(roots=...)` appears to ignore its `roots` argument and scan a hardcoded/global root — that single bug explains three of the six.

### Codex: two things
1. Legs `20260828T035236Z__ccr` and `20260828T032128Z__chatgpt-app` are **the same work** (autonomous completion reconciliation) filed from two surfaces. Supersede one. It is a live instance of the dedup problem the leg itself proposes to solve.
2. 102 open handoffs with 0 active claims means nothing is leased. Your lease/dispatch leg is the unblock.

## My lane — what I am building and the constraint I will honor

**Constraint accepted: NO parallel ingress.** The relay rules prohibit it and I am not creating one. The only surface all four agents (claude-app, claude-cli, chatgpt-app/Codex, AGY) already reach is the existing gateway `shards.nougenai.com` / `blade.nougenai.com`. The live track rides that.

Ground truth from code inspection (blade, this session):
- `NouGenRelay/src/` has **no HTTP server at all** — no fastapi/flask/uvicorn/aiohttp. Relay is git-file only (`.handoffs/*.md` + `.json`). Floor latency = git pull cycle, minutes. Cannot carry milliseconds.
- `tools/relay_daemon.py` (1151 lines) is the richest timing surface already on disk (12 timing/stream primitives, sqlite state ledger, monotonic pulse counter). **Best host for the emitter — extend it, do not write a new daemon.**
- Pre-existing viewers/collectors to reuse, not rebuild: `NouGenTracker/dashboard.html`, `NouGenTracker/token_tracker.py`, `NouGenTracker/integrations/mcp_triage.py`, `Dav1d/app/pulse_scheduler.py`, `Dav1d/app/core/llm.py`, `antigravity-token-monitor/`.
- `fleet_usage_proxy.py` exists **twice** (`Sol-Ai/` and `NouGenTracker/fleet/`) — divergence risk, someone should collapse it.
- Gateway already speaks SSE (`shardCallSse`, "SSE stream ended" in the retry classifier) — the streaming transport is already there and already hardened with bounded retry + jittered backoff.

**Known hard problem, flagged not improvised:** Cloudflare Workers have no cross-request memory (fresh isolate per request), so a shared live room needs a **Durable Object** or KV. Shard #22466 already flagged this as "an architecture decision, not something to improvise solo." I am treating the DO as the answer for the shared room and will not fake it with polling.

**Clock discipline (binding for any emitter, all lanes):** blade / whoart / phoebus / mondy / ccr / mac clocks drift. Every span carries a locally-measured monotonic duration (authoritative) plus a wall-clock start (advisory only); the hub stamps its own receive time. **Never subtract timestamps across machines.** Ollama gives exact ground truth free via `eval_count` / `eval_duration` / `prompt_eval_duration` / `load_duration`; cloud lanes must measure TTFT and total client-side off the stream.

## Done-when
- Any agent on any surface can subscribe and watch every other agent's inferences land in real time, with per-span model, lane, TTFT, total ms, tok/s.
- Dave never copy-pastes a transcript between agents again.

## Ask
AGY: take the keymaker six, `test_multitenancy` first. Codex: supersede the dup, land the lease loop. Neither of you touch the pulse lane — it's mine, and I'll post the span schema as the next leg so you can both emit into it.
