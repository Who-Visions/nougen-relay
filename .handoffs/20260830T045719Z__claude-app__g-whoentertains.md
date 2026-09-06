# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: P1 HANG FIXED (verified): BLADE_TIMEOUT_MS=8000 deployed, recall returns in seconds instead of hanging — and it exposes the real remaining fault: blade unreachable from edge, serving empty Space replica
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:57:19.183Z

---
**GM approved and I ran it.** `wrangler secret put BLADE_TIMEOUT_MS --name nougen-shard-failover` = `8000`. Binding confirmed live, new active version `8d8fc2e6-bed1-4065-9bd5-715bb8dbca95`. Reverts with `wrangler secret delete BLADE_TIMEOUT_MS --name nougen-shard-failover`.

## Verified result — the hang is gone
| probe | before | after |
|---|---|---|
| `shards_search("NouGen",1)` via MCP | hang → client timeout | **returns in seconds** |
| failover `POST /mcp/` | hang | **8.25s** |
| `shards.nougenai.com/mcp` POST | never reached query path | 401 in 0.17s |

The 8.25s matches the 8000ms budget exactly. Previously the first leg had 35s and the Space 120s (~155s worst case) under a 45s outer budget, so the outer layer always abandoned first and no error ever surfaced. Capping the first leg lets the call complete inside the outer budget.

## This CONFIRMS blade is the stalling origin
The failover burns the **entire** 8s budget on blade every call, then the Space answers. Note the discrimination: `POST https://blade.nougenai.com/mcp/` from blade itself returns **401 in 0.28s**, but the same request from the Cloudflare edge stalls past 8s. That is an edge→origin path fault, i.e. the tunnel — consistent with the missing `CLOUDFLARED_NGS_TUNNEL_TOKEN` leg `20260829T111954Z`, not with blade's process being down.

## The fix EXPOSED the next fault (this is the real remaining P1)
`shards_search` now returns **`(no matches)`** for both `NouGen` and `gateway`. Earlier tonight this same connector returned 5 real hits for `perplexity`, so the vault demonstrably holds data. We are now falling through to the **Space replica, which answers but has an empty or broken index** — precisely the malformed-replica condition in `20260829T120003Z`, previously invisible because the hang masked it.

**So the read path is up but serving from a bad replica.** Recall is responsive and WRONG rather than absent — arguably more dangerous, because `(no matches)` reads like a genuine empty result. Anyone acting on recall results right now should treat them as unreliable until blade is reachable from the edge again.

## Next, in priority order
1. **Restore blade's tunnel** so the authoritative store (DB5, healthy on blade) serves `/mcp` again — that fixes correctness, not just latency.
2. **Repair or resync the Space replica** so the fallback is actually a fallback rather than an empty answer.
3. **Lower `SPACE_TIMEOUT_MS`** from 120000 to under ~25000 (needs a `src/worker.js` edit + redeploy; cannot be done via `secret put` — already a plain var).
4. Consider making an empty-index replica **fail** rather than return `(no matches)`, so a bad replica can never impersonate a legitimate empty result.

## Corrections still standing from `20260830T044504Z`
`SHARD_GATEWAY_STYLE` was already `http` (my SSE root cause was wrong and is retracted). blade and the Space both answer direct probes fast — the stale 530/500 claims in `20260829T120003Z`/`120004Z` should not be worked without re-probing.
