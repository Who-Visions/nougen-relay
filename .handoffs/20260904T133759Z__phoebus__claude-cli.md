# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: ROOT CAUSE FOUND: phoebus node exhausts file descriptors (391 open vs launchd's 256 limit, 151 consumed on a fresh boot) and serves 503 deny-by-default — indistinguishable from 'no token'. This is the phoebus-absent-from-fanouts signature, and it contaminates every latency number taken today
**Branch**: `main` @ `a9089399`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T13:37:59.419696+00:00

---
While measuring the recall deadline I broke the node with eight search requests, and the failure explains far more than the deadline did.

## The node was serving 503 to every recall

```
POST /search  ->  503  {"detail":"Tenant registry is invalid."}
```

Node log:

```
ERROR tenant registry rejected: cannot load tenant registry
      /Users/kushboygroup/.nougen/tenants.json : [Errno 24] Too many open files
```

**File-descriptor exhaustion.** Not a crash — same PID, still "healthy" on `/health`, still `launchctl`-managed. It simply could not `open()` `tenants.json` any more, so tenant auth failed closed and every data endpoint returned **503 deny-by-default**.

## The numbers

```
launchctl limit maxfiles      256          <- what a launchd child actually gets
node's open FDs at failure    391          <- already far past it
plist NumberOfFiles           not set      <- inherits the 256
FDs on a FRESH boot           151 / 256    <- 59% consumed before serving anything
```

Held by SQLite connections, accumulating per DB:

```
22x nougen_shards_5.db   20x _9.db   20x _7.db   19x _8.db   + matching -wal
```

**Roughly 105 descriptors of headroom on a fresh node.** Eight federated searches consumed it.

## Why this matters more than the deadline

A 503 from FD exhaustion is **indistinguishable from a node with no token configured** — same status, same shape. A peer fanning out records phoebus as unauthenticated or down. That is the exact signature behind `20260904T042257Z` ("phoebus is absent from every fanout") and the intermittency nobody could pin all night: the node degrades under precisely the load that a fanout applies, then looks fine again after a restart.

It also contaminates today's latency work, mine included. `local=timeout:20.2s` on a cold node and `local=ok:8.3s` warm are real, but any probe run near the FD ceiling is measuring descriptor starvation, not search. I am not claiming the 20s cold figure is wrong — I am saying it was measured on an instrument that fails silently under the same load, so it needs re-taking on a node with headroom.

**My restarts today made this worse and hid it.** Each `kickstart` reset the FD count, which is why the node kept looking recovered. I restarted three times before noticing.

## What I did and did not do

**Did:** restarted the node — service is restored, fresh PID, 151/256. That is the documented path and it is phoebus's own service.

**Did NOT:** raise `SoftResourceLimits/NumberOfFiles` in `com.whovisions.ngsnode.plist`. That is a launchd config change on the fleet's permanent node and it is the operator's call, not mine to slip in. **It is also the single highest-value one-line change available on this box right now** — the node is one traffic burst from 503ing again.

**Did NOT:** fix the leak. Connections are being opened per request/thread against all nine grid DBs and not closed. That is the root cause and it deserves a proper PR against `core.get_connection` / `history.get_history_connection` rather than a limit bump that only moves the ceiling.

## Recommended order

1. Raise the plist FD limit (immediate, reversible, stops live 503s).
2. Fix the connection leak (real fix).
3. Re-measure the recall deadline afterwards. **Every latency number from this node today, mine included, was taken on an instrument that fails silently under load.** That includes the "local is the only lane that times out" finding in #211 — the conclusion may well hold, but it has not been measured on a healthy node.

Also worth noting for whoever picks up the deadline: `cloud`, `external` and `vaults` all return in **0.0s** — they are no-op lanes with no configs. The only lane doing work is `local`, so the four-lane fanout is currently three no-ops and one real query.

*— phoebus / claude-cli*
