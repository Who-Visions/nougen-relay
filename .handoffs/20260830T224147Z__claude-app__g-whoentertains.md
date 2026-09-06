# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: All four PRs merged (#141 #142 #143 #144); recall fix LIVE on shards.nougenai.com at deploy_sha 493ab18. Defect flagged in #143's vector-cache kill switch. Correcting my own earlier process-leak claim.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T22:41:47.709Z

---
End-to-end landing pass, run while the recall lane and AGY were both quota-blocked. Everything below is merged and verified live.

## Merged to main

| PR | What | State |
|---|---|---|
| #141 | worker-var setter: `--set` had never written anything (JSON instead of multipart on the CF script-settings PATCH = bare 415); `--get` reported "unset" for `secret_text` bindings | MERGED |
| #142 | public-surface: five **tracked** lane-claim leases were shipping machine names, pids and session ids in a public repo | MERGED |
| #143 | recall perf, 19 commits (recall lane's) | MERGED |
| #144 | nougen-ctx skill + mcp (its own lane) | already merged |

Main head `493ab18`, CI green. **The Space auto-syncs on every merge** - `shards.nougenai.com` now serves `deploy_sha 493ab18`, `storage /data`, `persistent_storage true`. There is no manual Space rebuild step; a real merge does it. That retires the standing "push a no-op commit to force a rebuild" ask for this Space.

## How #143's conflict resolved

`core.py` only, 7 hunks. **Main contributed nothing core.py did not already have** - the perf branch had already absorbed main's 2026-08-29 corrupt-DB work. Verified by inventory, not assumption: both sides carried the same 6 `DB_DEGRADED` handlers and all 8 `unreadable during ...` guard sites. Every hunk resolved to the perf branch's structure because main's side was the pre-parallel shape of the same logic. Main's two invariant tests pass on the merged file (5 passed).

**I briefed the worker on a wrong premise and it caught me.** I said main introduced `missed_dbs.append(i)` and the perf branch had `missed = True`. Inverted - the merge *base* had the list; the perf branch introduced the boolean. The correct resolution was the opposite of what my premise implied. Worth internalising: give a delegation a resolution *principle*, not an unverified factual claim about which side introduced what.

## Defect in #143, flagged not fixed

`core.py` ~1542: `cache = _vector_cache_entry(i, conn) if _vector_cache_enabled() else None`, then `if cache and ...`. With `NOUGEN_VECTOR_CACHE=0` the vector lane returns `[]` **silently**. The docstring says the switch disables the *cache*, but main's SQL fallback is gone, so it disables semantic recall entirely - keyword-only results that read as "no semantic matches" rather than "lane off". Default path unaffected, so a foot-gun rather than a live regression. Restoring the fallback reintroduces the 10.7GB scan they deliberately removed; the honest fix is a loud one-time warning plus a corrected comment. Reported directly to the author's session; their call.

## Correcting my own earlier leg (20260830T220905Z)

I reported the ~50 MCP processes as a leak with "nothing reaps them on disconnect". **Wrong.** Measured: **zero orphans** - every one has a live parent. 24 distinct live clients (agy 12, claude 11, language_server 6, codex 4). It is contention on an 8-core box, not a leak, and the reaper I proposed would have found nothing to reap. Same cause explains Codex's 30s MCP startup timeouts and its failing hooks - I ran every failing hook directly with realistic payloads and they all exit 0. They are being starved of their deadline, not broken. Fixed the Codex side: `startup_timeout_sec = 120` on the seven declared servers that were timing out in `~/.codex/config.toml`, backup written, TOML re-parsed clean.

## Also settled

The connector "split brain" signature from shard 2172 (`mcp_up=true, health_up=false`) is a **deploy window**. Reproduced cause-and-effect: merged, the Space sync fired, `shards_status` went split-brain, all three health endpoints curled 200 by hand, next call green. Before opening an incident on that signature, check `gh run list --branch main` for a recent Space sync.

## Open, not mine

- PRs #128-#136 are other lanes' work with their own review needs. Untouched.
- The local node on 4444 reports `persistent_storage: false` - "memories are wiped on every restart/deploy" - while the Space reports `true` with `/data`. Same app, different storage posture. Local node memory did not survive the restart I did earlier.
- `docs/nougen_sovereign_intelligence_doctrine.md` still uses the banned brand term four times plus hardware/ops leaks. Untracked, so nothing has shipped, but it must not be swept in.

## Done-when

- [x] #141, #142, #143 merged, main green
- [x] Space serving the merged recall fix (493ab18)
- [x] node on 4444 healthy (200 in 12ms)
- [x] Codex MCP startup timeouts fixed
- [ ] `tools/recall_bench.py` re-run on a quiet box to get an honest p95 (the lane's 11.4s outlier was measured while 24 MCP clients and three test suites shared 8 cores)
- [ ] vector-cache kill-switch made loud
