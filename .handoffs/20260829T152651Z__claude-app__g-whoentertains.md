# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CONNECTOR FIX 4/4 (deploy path): there is NO source project for nougen-fleet-mcp anywhere — fixes 1-3 have nowhere safe to land. Locate or reconstruct it BEFORE deploying anything.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:26:51.003Z

---
Four of four. **This one gates the other three, so read it before shipping them.**

## The problem

I prepared exact patches for `kaedra_ask` (`20260829T152600Z`), `listLegs` (`20260829T152614Z`) and `tracker_spend` (this batch). All three are one-function changes with measured before/after numbers. **None of them has a safe place to land.**

`workers_get_worker_code` returns the **deployed bundle** — 2,039 lines of built output, not the source project. And the source is not on this fleet:

```
find "The Observatory" -iname "*fleet-mcp*"        -> nothing
grep -rl "tracker_spend" --include=*.ts --include=*.js  -> nothing outside the dump
wrangler.toml / wrangler.jsonc for this worker      -> nothing
```

The only wrangler projects on phoebus are vendored third-party ones under `Livthemoment/deps/`.

## Why I did not just deploy it

I have the capability: `wrangler whoami` reports OAuth with **`workers_scripts (write)`** and `workers (write)` on account `0d4ac187…`, and there is a deployment from 10:50 today under the same account. So this was a choice, not a blocker.

Hand-editing a decompiled bundle and pushing it over the connector **the entire fleet reads** is not a safe unilateral move:

- the worker reads `env.RELAY_BRANCH`, `env.KAEDRA_GATEWAY_TOKEN`, `env.SHARD_GATEWAY_TOKEN`, `env.KAEDRA_TIMEOUT_MS` and more. A deploy assembled without the original config can drop vars and bindings.
- **this fleet has already been burned by exactly that** — a worker settings write that dropped bindings, which is why `keep_bindings` is doctrine here.
- a broken connector takes out relay, tracker, shards and Kaedra for every lane at once. That is strictly worse than the three bugs it would fix.

## What is actually needed

**Find the source project.** Candidates, in order:

1. a repo under `who-visions` or `WhoVisions` that is not cloned on phoebus — I can only see the four I have
2. a checkout on blade or whoart (I have SSH to both and can search if someone confirms it should be there)
3. a Cloudflare dashboard "Quick Edit" worker with no source at all

**If (3), that is the real finding**: a production worker carrying relay, tracker, shards and Kaedra for the whole fleet, with no recoverable source and no review path. That should be reconstructed into a repo — the bundle is readable and the three patches above are small — and it should happen *before* the next edit, not after.

## Ask

- **Whoever last deployed this worker** (there is a deployment at 2026-08-29T10:50:41Z under `whoentertains@gmail.com`): say where the source lives. That single answer unblocks all three fixes.
- If it lives on blade or whoart, relay the path and I will apply and test all three patches from phoebus over SSH.
- If it does not exist, say so plainly and I will reconstruct a source project from the bundle as a PR rather than a blind deploy.

## Done when

`nougen-fleet-mcp` has a source project under version control, and fixes 1-3 land through it with a diff someone can read.
