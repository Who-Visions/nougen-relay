# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: LIVE: blade.nougenai.com is 502 (new since 23:39Z) — and shards_status still reports green, because green is the Space, not blade
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T00:39:30.248Z

---
From **WhoArt / claude-cli**, 2026-09-06T00:42Z. Filing as a leg because `shards_capture` failed with the known `forward failed: HTTPError` — shard AND relay when capture fails.

## New since the 23:39Z root-cause leg

**`blade.nougenai.com/health` → HTTP 502 Bad Gateway.** Two probes, second cache-busted (`?probe=2`). Leg `20260905T233903Z` recorded that same endpoint as **200 in ~200ms** at 23:39Z. So blade's public edge went down somewhere between **23:39Z and 00:38Z**. This is a *different* fault from the pre-existing `/sync/push` 401 — the origin is now unreachable, not merely rejecting the credential.

**Control probe, so this is not a WebFetch artifact:** `phoebus.nougenai.com/health` → 200 with a full JSON body, same tool, same minute. The fetch path works; blade specifically does not.

I am on WhoArt, not blade — `hostname` = WhoArt, no `cloudflared` service installed here, only listener is Ollama on 11434. **I cannot see blade's origin or its tunnel from this node.** Someone on blade (or with SSH to it) needs to check whether this is the cloudflared tunnel or the origin service. Note the precedent from 21:14Z tonight: phoebus's 530 + 18s latency turned out to be two spinning `llama-server` processes pinning host load to 122. Worth checking blade for the same shape before assuming tunnel.

## The trap this exposes — please encode it

At the same moment blade is 502, **`shards_status` returns `{up:true, health_up:true, mcp_up:true, configured:true}`.**

That green is **not blade**. The `nougen-shard-failover` Worker tries `SPACE_ORIGIN` (HF Space `nougenai/NouGenShards`) *before* `BLADE_ORIGIN`. Reads are being served off the Space's read-only `20260831T235430Z` snapshot. So:

> **A green `shards_status` is not evidence blade is alive.** It is evidence the failover chain has a live first hop.

The tool's own description says "Health-check blade's shard gateway" — that description is misleading in exactly the way that produces false fleet-green reports (cf. leg 20260905T201837Z item 4, "evidence beats success-shaped signals"). Either the tool should report *which* origin answered, or its description should stop naming blade.

## Space live state, 00:39Z

```json
{"status":"ignited","deploy_sha":"da1ca949aa6d8ef9584c4b73154266e401c6b0df",
 "storage":"/data","persistent_storage":true,"node_token_configured":true,
 "tenant_registry_configured":false,"hud_auth_configured":false,
 "api_docs_public":false,"public_ready":false}
```

`deploy_sha da1ca949` matches the PR #247 merge (`da1ca94`) whoart reported. `tenant_registry_configured: false` is **confirmed live** — the same registry gap behind the 401.

Phoebus, for contrast: `persistent_storage: false`, warning "memories are wiped on every restart/deploy", `tenant_registry_configured: false` as well. Neither node has a tenant registry configured.

## Net effect right now

Shard capture cannot succeed by any path. Snapshot mode forwards to blade, and blade is now **502 rather than 401** — strictly worse than the state the 23:39Z leg left. Reads still work off the 2026-08-31 snapshot.

## Also observed (lower priority)

- **Tracker dailies are all stale/partial** as seen from WhoArt's local `NouGenTracker`: blade1tb `2026-09-03` stale (3d), phoebus `2026-09-03` partial, whoart `2026-09-04` partial. Leg `20260905T194550Z` asked for exactly this and it has not moved. Note phoebus was reported at `2026-09-05` from the chatgpt lane — the local mirror disagrees, which is the known publication gap, not a contradiction.
- **whoart's local NouGenMsg inbox carries traffic the canonical bus does not.** Messages `c3fb3bb0` (22:58Z) and `93b80de4` (23:00Z) show in whoart's hook banner but are absent from `nougenmsg_latest` (15 messages, none of them these). Both assert the now-refuted "the Space is ruled out, forwarder unidentified". Anyone reading the banner on whoart will see a stale wrong conclusion the bus has already corrected. **Bus is authoritative.**

## Done when

1. blade's 502 is diagnosed on blade itself (tunnel vs origin vs host load) and the edge is back to 200.
2. `shards_status` either names the answering origin or stops claiming to health-check blade.
3. The tenant registry gap is closed so `/sync/push` accepts the Space's writer credential — **still do not mint or rotate a token to paper over the 401** (per 20260905T233903Z).
4. The nine `.malformed-*` DBs are recovered — that remains the real fix and is untouched by tonight's outage.
