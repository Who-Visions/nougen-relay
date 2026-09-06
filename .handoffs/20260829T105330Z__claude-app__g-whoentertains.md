# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED: Rhea's 530/1033 was gateway routing, not inference. Fixed in Cloudflare (SPACE_TIMEOUT_MS=120000; connector now routes via failover workers.dev). ask_rhea and shards_status verified up.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T10:53:30.755Z

---
## Resolved

`ask_rhea` works. `shards_status` = `{"up":true,"status":200,"configured":true}`.

**It was never an inference problem.** The HF Space was healthy the entire time
and answered `/agent` correctly, naming a brain. Multiple sessions (mine
included) burned hours hunting missing provider keys because the error read like
a lane outage.

## Root cause — two independent faults

**1. Failover budget tuned for the wrong endpoint.**
`nougen-shard-failover` aborts the Space at `SPACE_TIMEOUT_MS` (default 35000)
then falls through to `blade.nougenai.com`, whose tunnel is down and returns
exactly `530` / `error code: 1033`. That 35s figure came from `/search` (9-11s).
Rhea's `/agent` runs a multi-round agent loop and **measures 70.5s**, so every
call was cut off mid-flight and the dead tunnel's error surfaced as if it were
Rhea's. → set `SPACE_TIMEOUT_MS = 120000`.

**2. The connector pointed at a host in its own zone.**
`nougen-fleet-mcp` had `SHARD_GATEWAY_URL = https://shards.nougenai.com`.
External callers to that host DO get the failover worker (verified:
`x-nougen-origin: space`), but the Worker's own subrequest to a same-zone
hostname reached the tunnel origin instead — so failover never ran for the
connector. → now `https://nougen-shard-failover.whoentertains.workers.dev`,
outside the zone, cannot be bypassed, and keeps blade failover for when blade
returns.

## Why this stayed hidden

**Neither worker was in the repo** — `fleet/` is gitignored. Both had to be
recovered with `wrangler init --from-dash`. That is the substance of legs
`20260829T045608Z` and `20260829T045709Z`; they were not "needs the worker
source", they were "the source does not exist in version control".

Both are now committed under `ops/workers/`, with the full write-up in
`docs/gateway-routing.md` (commits `b9995665`, `be038d56`). Config values are
deliberately not committed — the fleet worker's vars include an allowed-email
list; read them with `wrangler versions view <id> --name <worker>`.

## Diagnosis lessons worth not repeating

- `/health` returning 200 proves the Space is reachable, **not** that a given
  caller's path works. `/agent` and `/health` resolved differently for the same
  host. Reading `/health` as proof of health cost the most time.
- `x-nougen-origin` names which origin answered. Check it first.
- A first `shards_status` after deploy can report `up:false` from an 8s
  `/health` budget against a cold Space. Retry before concluding. Warm: ~0.9s.
- `blade.nougenai.com/agent` returning `530 / error code: 1033` byte-for-byte
  is the fastest way to confirm a tunnel fault vs a lane fault.

## Still open

- Blade's tunnel remains down; failover now correctly rides the Space instead.
- `shards_recall` returns no results via the Space substrate (call path works,
  no error). The Space is not blade's full vault — expected while blade is down,
  worth confirming intent.
- PR #135 still blocked on 3 CodeQL name-heuristic false positives needing an
  owner dismissal. Its free-model-list change should probably be dropped: the
  outage was never about OpenRouter.
