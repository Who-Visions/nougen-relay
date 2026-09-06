# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE GREEN END-TO-END: 502 fixed, llama spin killed, capture verified, Space Sync 413 root-caused (DLL-as-content row) and fixed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T03:28:06.497Z

---
From **WhoArt / outpost-1d (claude-cli)**, 2026-09-06 03:30Z, on Dave's order. Closes out my leg `20260906T003930Z` (already acked by another lane) and the Space Sync item.

## Done tonight, all verified live

1. **blade.nougenai.com 502 → 200.** Blade rebooted 20:23:01 EDT; logon task `NouGen Shard Gateway` died `0xC000013A` (console teardown) before re-pointing the worker at the origin. The origin (uvicorn :4444) was healthy the whole time. Re-ran `gateway_supervisor.ps1 -Once` over SSH with a real console → edge 200 immediately. **Hardened**: that task + `NouGen-ApolloMeshService` now have `PT90S` logon delay + 3 auto-restarts/2min, so the next reboot doesn't reproduce this. (Recurrence of the 2026-08-29 boot-chain class, shard 29776@db2.)
2. **Killed 3 spinning llama-servers** (worst: 4,984s CPU, 9.4GB WS). CPU 100→77, +14.7GB RAM freed. Side effect: **the referee lane came back** (`gemma4:31b-cloud @ 127.0.0.1:11434`) — it was down because Ollama was starved.
3. **Capture path live end-to-end**: shards 22635@db8 and 22410@db3 written and recalled, fanout blade/phoebus/whoart all ok. Note **blade reports `tenant_registry_configured: true`** — the "registry gap on blade" framing in leg 20260905T233903Z was wrong.
4. **Blade CLI unblocked**: `~/.claude/settings.json` hook pointed at `NouGenShards-push-main/tools/claude_inbox_hook.py` which doesn't exist in that checkout; repointed to `NouGenShards-repo/tools/` (identical sha `97c0b8b0`), backup kept, `claude -p` → pong. Blade has THREE NouGenShards checkouts; path drift between them caused this.
5. **Space Sync unwedged — real root cause of the 413**: db4 rowid **22938** is a Watchtower ingest of `flutter_windows.dll` — binary stored as **44.6M chars** of content → JSON-escaped 143MB body → **Cloudflare's 100MB edge cap**, eternal 413 that `shrink_batch` can never fix at batch=1. Hidden because SQLite `length()` stops at the first embedded NUL (row "measured" 3,890b). Deployed `MAX_SYNC_CONTENT_CHARS=2M` cap in `to_payload` (oversized rows stay intact, local-only, like sensitivity skips; checkpoint advances), restored batch 150. Verified: db4 22937→23113+, db9 23135→23313+, pushed=150/batch, zero new 413s. Backup: `space_sync_daemon.py.bak-20260906T0330Z`.

## Still open for whoever takes it
- **The Space's corrupt 9-DB grid** (`.malformed-20260905T2331*Z`, ~1.6GB) still needs `.recover` — unchanged from 20260905T233903Z. Snapshot mode stays until then.
- `shards_status` should name which origin answered (it reported green all through blade's outage because the Space answers first).
- Upstream Watchtower ingest should stop sharding raw binaries — the cap is a guard, not the cure.
- Design gap: strategy `shrink_batch` is permanent; nothing grows batch back on success without a referee verdict.
