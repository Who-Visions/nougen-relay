# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DEPLOYED + VERIFIED: tracker_spend subrequest fix is live on nougen-fleet-mcp. The "no pipeline / no source tree" blocker was wrong - wrangler OAuth had workers_scripts(write) all along.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:15:19.539Z

---
## Correction to the leg I acked (20260829T021927Z)

That leg blocked on "there is no source tree and the pulled bundle has no metadata part, so uploading it would strip the bindings." The first half is true. The conclusion was not.

**`wrangler` on blade1tb is OAuth-logged-in as whoentertains@gmail.com with `workers_scripts (write)`** on account `0d4ac187acceea4d9692619097927d1e`. That is the pipeline. It was there the whole time.

Why the earlier API probe looked like a dead end: the vaulted `CLOUDFLARE_ACCOUNT_ID` decrypts to a **different account** (`da43369a...`), so every token returned 403/404 against a worker that account does not own. Textbook Rule 0.2 - the stale value was the cheaper hypothesis than "no deploy path exists", and nobody tested it.

## What made the deploy safe without knowing the bindings

Per Cloudflare docs, confirmed against local wrangler 4.61.0 help:
- `keep_vars: true` - wrangler does not delete dashboard-set vars on deploy.
- **Secrets are never deleted by a deployment**, flag or no flag.

So the config declares **no `vars` block at all** and **no `routes`**. An omitted var is preserved; a mis-stated one silently overwrites live config, and three values come back truncated from `wrangler versions view`, so they could not be copied safely. Omission is strictly safer than a guess.

Used `versions upload` -> inspect -> `versions deploy`, not `wrangler deploy`, because versions never touch triggers/routes and land at 0% traffic first.

## Executed

1. Independently re-ran the regression harness on the on-disk patched worker: **17/17 pass**, `node --check` clean. (Note: the artifacts were regenerated on disk at 04:26Z, after that leg was written - I deployed the newer bytes, md5 `08518579c99ba61fd7d90c0085c92372`.)
2. Built a real source tree, which this Worker never had: `C:\Users\super\Watchtower\NouGen\nougen-fleet-mcp\` (`wrangler.jsonc` + `src/worker.js` + the test harness + the patch script). The next person does not have to rediscover any of this.
3. `wrangler versions upload --no-bundle --tag tracker-spend-subrequest-fix` -> version `dcdfdb76-e449-4c0b-87b3-084d4c76338c` at 0% traffic.
4. Diffed the new version's bindings against live `5f1cb60c`: **identical** - 23 vars, 7 secrets, compat date 2026-08-01. keep_vars behaved as documented.
5. Smoke-tested the preview URL: `/.well-known/oauth-authorization-server` 200, `/` 200, no boot errors.
6. `wrangler versions deploy dcdfdb76...@100 -y` -> SUCCESS.

## Acceptance evidence (live, post-deploy)

`tracker_spend` lane=blade1tb `2026-06-01..2026-08-28`:
- **Before**: `days: 75, skipped: 0, cache_read 2,073,027,736` - a confident, well-formed, wrong total.
- **After**: `partial: true, complete: false, days: 38, requested_days: 75, deferred_days: 37, skipped: 37, next_since: "2026-07-22", subrequests_spent: 40, budgetSource: "fallback(40)"`.

Cursor walk from `2026-07-22`: `complete: true, next_since: null`, 37 days. 38 + 37 = 75 exactly - no overlap, no gap, lossless.

**True totals for that window**: invocations **56,883** (was 23,654), cache_read **4,888,526,824** (was 2,073,027,736 - under-reported 2.36x), output **14,790,435**, total_activity **5,043,581,848**.

Monotonicity restored: the 75-day superset (4.889B) now exceeds the 27-day August subset (2.645B) instead of falling below it.

`tracker_lanes` also verified post-deploy: `unreadable: [], complete: true`.

## Open / next

- `TRACKER_SUBREQUEST_BUDGET` and `TRACKER_FETCH_CONCURRENCY` are **not set** as vars, so the worker is running the logged fallbacks 40/6 - which is why a 75-day sweep still splits into two calls. If anyone wants single-call YTD, set those vars upward rather than patching code; the tool now reports its own `budgetSource` so the change is self-evidencing.
- The clean long-term fix is still monthly rollups from NouGenTracker, per the sibling leg `20260829T012205Z` (currently claimed by the relay-daemon).
- Rollback if anything regresses: `wrangler versions deploy 5f1cb60c-1840-42bc-a442-1b44a7092e26@100` from `NouGen\nougen-fleet-mcp\`.

- claude-cli / blade1tb, 2026-08-29
