# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix stale relay and shard visibility on ChatGPT connector lane
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T23:16:58.535Z

---
## Incident
ChatGPT connector lane authenticated successfully as `g-whoentertains` with Relay, Tracker, and Shards configured and reachable, but visibility is stale.

## Evidence observed 2026-08-31
- `fleet_whoami` succeeds.
- Relay backend points to `Who-Visions/NouGenRelay`.
- Shard gateway points to `https://shards.nougenai.com`.
- `relay_latest` still returns an Aug 29 leg: `20260829T120007Z__ccr__claude-cli`.
- `relay_open` returns Aug 29 open legs and no newer activity.
- Fresh shard recall for latest Aug 31 system status returned no results.
- User confirms this is a visibility lag, not expected fleet inactivity.

## Diagnose
Trace the ChatGPT connector read path end to end and identify where freshness is lost: relay registry sync, cache invalidation, gateway indexing, lane routing, stale worker deployment, repo head mismatch, or connector-side pagination/cursor state. Compare this lane's visible relay head and shard index timestamp against a known-fresh lane.

## Fix requirements
1. Make relay_latest reflect the true newest leg across the fleet.
2. Make relay_open expose current open legs, not an Aug 29 snapshot.
3. Make shard recall see newly captured Aug 30 to Aug 31 material.
4. Add a freshness signal to connector responses, ideally source head SHA or event timestamp plus index timestamp, so stale reads are detectable instead of silent.
5. Add a regression probe that writes or observes a known relay/shard event and verifies every provider lane can see it within the expected propagation window.
6. If caching exists, define explicit TTL and invalidation behavior for relay and shard read paths.

## Done when
From this ChatGPT connector lane, `relay_latest` returns the actual newest fleet leg, fresh Aug 31 shards are recallable, and a cross-lane freshness probe passes with observable timestamps/head identity.
