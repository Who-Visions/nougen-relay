# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: shards_status false-green killed (deployed+verified) and all 3 nodes publishing dailies. Space reseed is the last item — blocked on a nougenai HF token
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T03:37:42.403Z

---
From whoart/claude-app, 2026-09-06T03:5xZ, under Dave's explicit "fix everything" authorization. Two of three done and verified live; the third is blocked on a credential and its **plan has changed** — read item 3 before acting on the old one.

## 1. ✅ shards_status false green — FIXED, DEPLOYED, VERIFIED

`shards_status` now reports which origin answered:

```json
{"up":true,"status":200,"configured":true,
 "origin":"space","read_only_snapshot":true,"blade_confirmed":false}
```

The Worker was already stamping `x-nougen-origin` on every response (`nougen-shard-failover.js` lines 43/58/62) — `worker.js:shards_status` was throwing the header away. Now it surfaces `origin`, `read_only_snapshot`, `blade_confirmed`, and says so in the text. The tool description no longer claims to "health-check blade's shard gateway"; it states that green means recall works, not that blade is up.

Deployed to `nougen-fleet-mcp` via `fleet/worker/deploy_worker.py` (etag `9390ecc9dbfe`). **Note `fleet/` is gitignored in NouGen, so there is no commit — the deployed etag is the only record.** Whoever owns that decision may want a tracked copy.

**Read this off the new output:** `blade_confirmed: false` right now. blade.nougenai.com is 200, but the failover Worker never reaches it because the Space answers first. Green has meant "Space" this whole time.

## 2. ✅ Tracker dailies — ALL THREE NODES PUBLISHED THROUGH 2026-09-05

```
blade1tb: dailies/blade1tb/2026-09-05.json
phoebus : dailies/phoebus/2026-09-05.json
whoart  : dailies/whoart/2026-09-05.json
```

whoart `908f7fb`/`8240b87`, blade `af6c26a` (exported and pushed over SSH from blade itself — machines only write their own directory). Root cause was never failed generation: **whoart was 5 commits ahead, unpushed.**

⚠️ **Near-miss worth encoding.** `git diff --name-only origin/main..HEAD` listed 37 files, 36 of them *phoebus* dailies. Pushing on that reading would have clobbered origin's newer phoebus re-exports (`c085ae5`, `e20bd0f`, `434cba4`). `git show --stat` proved the local commit touched **one** file. A symmetric range-diff describes **divergence, not authorship**. Rebased; phoebus's work survived. Also: never run bare `token_tracker.py --export` — it rewrites *every* day it has data for. Use `--start/--end`. Shard `22508@db6`.

## 3. ⚠️ Space grid — THE PLAN SHOULD CHANGE. Do not recover the 1.6GB.

I read the bucket `nougenai/ngs-vault` directly. Two things contradict the standing plan:

**(a) The corruption is ongoing, not historical.** Beyond the nine `.malformed-20260905T2331xxZ` files, the bucket now holds **two more db1 quarantines created after the 23:39Z leg was filed and acked**:
`nougen_shards_1.db.malformed-20260906T015752Z` (332 MB) and `...-20260906T020351Z` (348 MB). The Space re-corrupts db1 about every boot. Recovering the nine files repairs a snapshot of a process still running. Root cause is architectural: **SQLite + WAL + an FTS5 vtable on a FUSE-mounted bucket** — FUSE does not provide the locking SQLite needs. Live `-shm` files were present at 03:18Z.

**(b) Nothing unique is trapped in there.** Counted, not assumed:

| substrate | rows |
|---|---|
| **blade local grid** | **243,803** ← superset, healthy, writable |
| Space snapshot `20260831T235430Z` | 235,064 |
| whoart local grid | 202,880 |

Snapshot DBs 2,4,5,6,7,8,9 are byte-identical in size to the live `.vault` copies; only db1/db3 diverge. And captures have forwarded *away* from the Space since 2026-09-01T00:01Z, so it accepted no new shards in the window — db1's growth is index churn, not rows.

**So: RESEED from blade, don't recover.** Rebuild the Space grid from blade's 243,803 rows, and stop running SQLite on the FUSE mount (copy to container-local disk at boot, serve from there, snapshot back to /data). **Keep `NOUGEN_SNAPSHOT_DIR=/data` until that lands** — it is still the shield (shard 22721@db4). Full evidence in shard `22636@db8`.

**BLOCKER — this is why I stopped here.** Reseeding needs a **nougenai-scoped HF write credential**. Neither whoart's nor blade's keymaker vault has one: whoart holds 16 HF tokens (WhoVisions, WhoVisionsDave, AiwithDav3, ContactWho, eatsruger, EdieBrikell, thesexyslumberparty) and none authenticate as `nougenai`. The **phoebus/claude-app** lane demonstrably has it — it changed Space Variables on 2026-09-05. That lane, or Dave, should take this.

## Also cleared / corrected

- **blade's 502 and the `/sync/push` 401 are both gone.** blade now reports `tenant_registry_configured: true` (was `false` in the 23:39Z and 00:39Z legs) and **capture works end-to-end** — shard `22778@db9` written and recalled, fanout `{blade: ok, phoebus: ok, whoart: ok}`. The 00:39Z conclusion "capture cannot succeed by any path" **no longer holds**; stop routing around it. Done-when item 3 of that leg is satisfied **without any token being minted or rotated**.
- **whoart's grid is clean** — 9 DBs, 202,880 rows, zero malformed. A 0-byte stray `nougen_shards_06.db` (09-05 17:22, no tables) was quarantined as `.empty-quarantined-20260906`; it broke glob-based grid enumerators and is a likely source of phantom "broken DB" reports.
- **Not a defect:** blade's `pricing_cache.json` JSON parse errors during a tracker export are a concurrent mid-write read. The file validates clean. Recorded so nobody re-chases it.

## Done when
1. ~~shards_status names its origin~~ ✅
2. ~~all three nodes publish dailies~~ ✅
3. Space grid reseeded from blade **and** SQLite moved off the FUSE mount — needs a nougenai HF write token.
