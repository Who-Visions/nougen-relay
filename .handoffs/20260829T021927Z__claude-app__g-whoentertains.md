# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED + TESTED (needs deploy): tracker_spend silent under-reporting — root cause was swallowed subrequests, not the 92-cap. Corrects my earlier mechanism claim.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T02:19:27.721Z

---
## Correction first
My earlier leg `20260829T015226Z` said the 92-file cap dropped the *newest* dailies. **That was wrong.** The code reads `dates.slice(-budget)` on an ascending sort — it keeps the newest and drops the oldest. The under-reporting is real and reproduced, but the mechanism is different and worse. Superseding diagnosis below; the numbers in that leg still stand.

## Actual root cause (read from the deployed bundle, confirmed by live probe)
`nougen-fleet-mcp` / `tracker_spend`, pre-patch:
```js
const dailies = await Promise.all(take.map((d) => trackerDaily(env, lane, d).catch(() => null)));
for (const daily of dailies) { if (!daily) continue; ...sum... }
```
One unbounded subrequest per daily. Past Cloudflare's per-invocation subrequest ceiling every further `fetch` throws, `.catch(() => null)` swallows it, the daily vanishes from the sums — while `days` still reported `take.length` and `skipped` stayed **0**. The tool returns a confident, well-formed, materially low total with no warning of any kind.

Live proof, lane=blade1tb, both `skipped: 0`:
```
2026-08-01..08-28   27 days   cache_read 2,644,796,858
2026-06-01..08-28   75 days   cache_read 2,073,027,736   <-- contains the window above
```
A superset window reporting less than its own subset, with the cap counter reading zero, rules out the documented 92-file limit.

## Fix (applied, tested, NOT deployed)
Artifacts on blade1tb at `C:\Users\super\Watchtower\NouGen\`:
- `patch_fleet_mcp_20260828.py` — idempotent, anchor-checked patch script (fails closed on a missed/ambiguous anchor). 10 sites.
- `nougen-fleet-mcp.patched-20260828.js` — patched multipart body.
- `nougen-fleet-mcp.worker-20260828.js` — extracted worker.js, `node --check` clean.
- `test_fleet_mcp_spend.mjs` — regression harness.
- `nougen-worker-backups/nougen-fleet-mcp.pre-20260828.js` — pre-change backup, per convention.

**tracker_spend**: bounded subrequest budget resolved env-first (`TRACKER_SUBREQUEST_BUDGET`, `TRACKER_FETCH_CONCURRENCY`, logged fallbacks 40/6 — Rule 0.2 #6); pooled fetches replacing the unbounded `Promise.all`; only dailies that actually returned are counted (`days` vs `requested_days` vs `missing_days`); partial windows are marked `partial:true` / `complete:false` with a **`next_since` cursor** so a caller walks forward over non-overlapping windows and sums to an exact total; canonical `total_activity` = input + output + cache_read + cache_creation, versioned `total_activity/v1`, reasoning deliberately excluded; legacy `skipped` retained and now non-zero whenever coverage is short.

**Also hardened** (same class — one bad item killed or corrupted a whole tool): `tracker_lanes` (per-lane catch, reports unreadable lanes instead of throwing), `relay_claim_list` (unguarded `JSON.parse` inside `Promise.all` — one malformed claim file 500'd the tool), `relay_open` (per-leg catch). Swept the rest of the bundle: no other swallow-catches; the `shards_*` tools already fail loud.

## Test evidence
`node test_fleet_mcp_spend.mjs <worker.js>` stubs a 100-daily lane and a hard subrequest ceiling.
- Patched worker: **17/17 pass.**
- Unpatched worker (control): **12 fail** — decisive line `no counter includes an unfetched daily :: 500 vs 920`, i.e. it reported `days: 92, skipped: 0` while summing only 50 dailies. That is the production symptom reproduced offline.
Includes the monotonicity invariant the leg asked for (regression item #3) plus a cursor-walk test proving lossless reconstruction of the full total.

## Blocking on deploy — needs the pipeline owner
There is **no source tree for `nougen-fleet-mcp` on blade1tb**; the deployed script is the source, with prior versions in `nougen-worker-backups/`. The code I pulled via the Cloudflare API is the `worker.js` multipart part **only — it carries no metadata/bindings part**, so uploading it alone would strip the worker's bindings. I did not deploy: production is human-in-the-loop, and I will not guess a binding set.

Whoever owns the deploy: apply `nougen-fleet-mcp.worker-20260828.js` through the normal pipeline with the existing bindings intact, then re-run the two probes above — `2026-06-01..08-28` must either exceed the August window or come back `partial:true` with a cursor. Point me at the pipeline and I'll take it the rest of the way.

## Still open
The sibling provider/model aggregation leg `20260829T012205Z` is unacked. Its YTD ask now has a working path — walk `next_since` — but the clean fix is monthly rollups published by NouGenTracker (`C:\Users\super\Watchtower\NouGen\NouGenTracker`, Python, local and editable), which would collapse a YTD sweep from ~106 subrequests to ~10.

— claude-cli / blade1tb, 2026-08-28
