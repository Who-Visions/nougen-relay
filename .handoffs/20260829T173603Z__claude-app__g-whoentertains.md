# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CANONICAL: shards.nougenai.com/mcp is the front door — every lane addresses it, nothing else. Repair drift, do not adopt it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T17:36:03.598Z

---
GM directive, 2026-08-29. Filed by whoart/claude-app. This supersedes any guidance pointing a lane at an origin.

## The rule

**`https://shards.nougenai.com/mcp` IS THE FRONT DOOR. It is the only shard address a lane may hold.**

The HF Space, `blade.nougenai.com`, and `nougen-shard-failover.whoentertains.workers.dev` are **ORIGINS THAT RESOLVE BEHIND IT**. They are never addressed directly by a client.

If `fleet_whoami` reports a `shards.gateway_url` that is anything else, that is **DRIFT — repair it, do not adopt it.** Do not "fix" a lane by writing down whatever it currently points at.

## Why this is not style

A lane pointed at an origin has no failover and dies with that origin. Today, measured:

- A thunderstorm took blade offline. `blade1tb.local` stopped resolving, `blade.nougenai.com` returned 530.
- `shards.nougenai.com` was UP THE WHOLE TIME — 200 in 0.3s, deploy_sha 7af14e11, storage /data, persistent_storage true.
- My connector had been repointed to `blade.nougenai.com` earlier today. So my shard memory went dark — `{up:false, health_up:false, mcp_up:false}` — while the front door was answering in under a second.

The outage was not the weather. The outage was the binding.

## Three values were live at once

    https://shards.nougenai.com                                  <- the front door (correct)
    https://blade.nougenai.com                                   <- what production actually had
    https://nougenai-nougenshards.hf.space                       <- what wrangler.jsonc had committed
    https://nougen-shard-failover.whoentertains.workers.dev      <- what docs/gateway-routing.md prescribed

Four sources, four answers, nobody wrong on their own terms. That is the actual defect: there was no canonical address, so every repair picked a different one. This is the THIRD drift of this variable — the prior commit touching it is titled "restore SHARD_GATEWAY_URL to the HF Space hostname production actually ran".

## The prerequisite, and the ordering is a trap

`shards.nougenai.com` must be bound to `nougen-shard-failover` as a **CUSTOM DOMAIN, not a route.**

Cloudflare, verbatim: *"On the same zone, the only way for a Worker to communicate with another Worker running on a route, or on a workers.dev subdomain, is via service bindings. On the same zone, if a Worker is attempting to communicate with a target Worker running on a Custom Domain rather than a route, the limitation is removed."*

So today `shards.nougenai.com` is bound as a ROUTE. `nougen-fleet-mcp` sits in the same zone; its own subrequest bypasses the failover worker and lands on the tunnel origin. That is why external clients got failover and the connector did not.

**SETTING THE VARIABLE BEFORE FIXING THE ROUTING TYPE REINTRODUCES THE BYPASS.** Fix the routing type first, then set the variable. Otherwise you trade a dead-host binding for a dead-path binding.

Alternative that also works: a service binding from `nougen-fleet-mcp` to `nougen-shard-failover` — zero-cost, no network hop, front door untouched. Custom Domain is preferred because it makes every lane take one identical path.

## docs/gateway-routing.md was wrong and is corrected

It prescribed moving `SHARD_GATEWAY_URL` to the failover worker's `workers.dev` hostname, "outside the zone and therefore cannot be bypassed". Two faults: it abandons the front door rather than repairing it, and Cloudflare's own limits say `workers.dev` subdomains carry the SAME same-zone restriction — it only appeared to work by being outside the zone, which is an accident, not a mechanism.

## Landed

- `Who-Visions/NouGenShards` @ 49cd32ee — docs/gateway-routing.md corrected, canonical section added at the top.
- `Who-Visions/nougen-fleet-mcp` @ 5919676 (main) — `SHARD_GATEWAY_URL = https://shards.nougenai.com`, with the Custom-Domain prerequisite carried inline as a comment so the value and its trap travel together.

## Still needed — GM, dashboard, not doable from a lane

1. Bind `shards.nougenai.com` to `nougen-shard-failover` as a Custom Domain (currently a route).
2. Then set the live `nougen-fleet-mcp` variable `SHARD_GATEWAY_URL = https://shards.nougenai.com`. Use Settings -> Variables, which updates the var without redeploying code and without disturbing the other bindings. Do NOT deploy from a repo to achieve this — deploy derives plain_text from config and has silently dropped live vars before.

## Note for every lane

`CLAUDE.md` IS GITIGNORED in NouGenShards. Doctrine edits to it are per-machine and do NOT propagate. I updated whoart's copy; every other box still has the old one. If a rule needs to reach the fleet it goes in a relay leg, a shard, or a tracked file — not CLAUDE.md. That is worth someone's attention independently of this incident.
