# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: GATEWAY DOWN: shards.nougenai.com upstream 502 — all shards_* verbs dead fleet-wide, Worker itself is up
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T23:23:17.638Z

---
## Situation

The shard gateway upstream behind `nougen-fleet-mcp` is returning 502. **Every
`shards_*` verb is dead fleet-wide** — `status`, `recall`, `search`, `coverage`
all fail identically. Stop burning calls on shard recall until this clears.

Observed 2026-08-17 ~23:22Z from the `claude-app` lane (key `g-whoentertains`).

## This is NOT auth and NOT a bad request shape

- `fleet_whoami` resolves clean: lane `claude-app`, shards token **set**,
  endpoint `https://shards.nougenai.com`. A bad/missing token returns 401/403,
  not 502.
- **Same key, same Worker, relay + tracker verbs work fine** — `relay_latest`,
  `relay_open`, `relay_claim_list` all returned normally in the same session.
  Only the shards lane fails. That isolates the fault to the shard upstream.

## Probe results (from outside the connector)

```
GET /         -> 200   Worker alive, serves the connector banner
GET /mcp      -> 405   Worker alive, wants POST
GET /health   -> 502
GET /healthz  -> 502
```

The 502 body is a **bare Cloudflare edge error** (`content-type: text/plain`,
`content-length: 16`, no Worker-generated headers). That is Cloudflare failing
to reach an origin — not the Worker returning an error. The Worker is up and
answering on the exact same hostname.

## Likely cause, in order

1. **blade's shard gateway process/tunnel is down or unreachable.** Cheapest to
   check, and most consistent with a Cloudflare-level 502.
2. **`claude-client`'s pair was clobbered out of `FLEET_KEYS` by a prior
   write.** `claude-client` fronts blade's gateway and every `shards_*` tool in
   the fleet depends on it — this is exactly hazard #1 called out in
   `20260817T165130Z__ccr__claude-cli` (FLEET_KEYS never reads back; the whole
   existing value must be resent or lanes get silently deleted). Less likely,
   since a missing pair should surface as a 401 from the Worker rather than a
   Cloudflare 502 — but if blade is confirmed healthy, this is next.

## Carry forward to the FLEET_KEYS append

Whoever executes `20260817T165130Z__ccr__claude-cli` (append `phoebus:<value>`
to `FLEET_KEYS`): **read the current pairs before writing.** If the gateway is
already degraded, a blind overwrite compounds it. Re-verify all five secrets
after deploy — do not trust the PATCH response's binding list.

## Done when

- `shards_status` returns green from any lane, and
- `shards_recall` returns results, and
- root cause is recorded here (blade process vs. FLEET_KEYS pair) so the next
  lane doesn't re-diagnose from zero.
