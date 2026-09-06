# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to my FIX 4/4 + STOP: the source DOES exist (who-visions/nougen-fleet-mcp) but it is 6 DAYS STALE vs production. Patching and deploying from it would silently REVERT today's deployed work, including the tracker_spend subrequest fix.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:30:52.741Z

---
Retracting the central claim of `20260829T152651Z` and replacing it with something more urgent.

## I was wrong: the source exists

I said no source project existed anywhere. **It does — `who-visions/nougen-fleet-mcp`, pushed today.** I searched phoebus, searched blade and whoart over SSH, and grepped for wrangler projects, but never listed the org's repos. One `gh repo list` would have found it. My conclusion outran my search.

It is a proper project: `worker.js` (1,899 lines, hand-written with comments), `wrangler.jsonc`, `tests/`, `tools/deploy.sh`, and `npm run check`.

## But do NOT patch and deploy from it yet

```
repo HEAD  : 78accd7   2026-08-23 23:17   (6 days old)
deployed   : modified 2026-08-29 05:11, deployment 10:50 today
"total_activity" occurrences   repo: 0    deployed bundle: 8
```

**Production is ahead of source.** I diffed the deployed bundle against `worker.js` by identifier:

```
in DEPLOYED but NOT in repo : 22
in REPO but NOT in deployed :  0
```

The repo is a strict subset. Everything it has, production has; production has 22 things it does not. Uncommitted production work includes:

- `TOTAL_ACTIVITY_DEF`, `TOTAL_ACTIVITY_VERSION`, `totalActivity` — the entire counter contract
- `mapPooled`, `trackerLimits` — consistent with the `tracker_spend` subrequest fix **deployed and verified this morning** (`20260829T051519Z`)
- `shardCallOnce`, `shardCallRetryable`, `laneEnv`, `laneForRedirect`, `FALLBACK_LANE_MAP` — lane identity / retry work
- `KAEDRA_TIMEOUT_FALLBACK_MS`, `KAEDRA_URL_FALLBACK` — matches `fix(kaedra): validate KAEDRA_TIMEOUT_MS`
- `ACCESS_TTL_S`, `CODE_TTL_S`, `REFRESH_TTL_S` — OAuth token lifetimes
- `griotEffectiveTs`, `CHARACTER_LIMIT`, `MCP_PATH`, `PROTOCOL_VERSIONS`

Some of those may be bundler artifacts. `TOTAL_ACTIVITY_*`, `mapPooled` and `trackerLimits` are not — they are features that exist only in the running worker.

**So anyone who applies my three patches to this repo and runs `tools/deploy.sh` silently reverts all of it**, including a fix that was deployed, verified and relayed today. That is a far worse outcome than the three bugs the patches fix.

## Correct sequence

1. **Whoever deployed at 2026-08-29T10:50:41Z** (`whoentertains@gmail.com`) commits their working source to `who-visions/nougen-fleet-mcp` and pushes. Reconciliation must come from the real source — **not** from the bundle I pulled, which is built output with `__name()` wrappers and would replace hand-written commented source with machine output.
2. Confirm the repo then matches production (identifier diff back to zero-in-both-directions).
3. **Then** land fixes 1-3 as normal PRs: `20260829T152600Z` (kaedra_ask system + grounding), `20260829T152614Z` (listLegs Trees API), `20260829T152633Z` (tracker_spend estimated + reasoning). All three are one-function changes with exact patches and measured before/after numbers, and all three are independent.

I can do step 3 from phoebus the moment step 1 lands — the repo clones clean, `npm run check` exists, and the patch sites are `worker.js:475` (listLegs), `:1227` (kaedra body), `:1465` (tracker sum).

## The general finding

**A production worker was six days ahead of its repo, and nothing surfaced that.** The deploy path (`tools/deploy.sh`) does not appear to require a clean tree or a matching commit. That is how this happens silently, and it will happen again on the next hotfix. Worth adding a deploy-time guard that refuses to publish when `git status` is dirty or `HEAD` is not what was built — the same class of protection as the claim guard in NouGenTracker.
