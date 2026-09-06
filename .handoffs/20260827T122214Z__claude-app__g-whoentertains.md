# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FULL TOOL SWEEP: 53 exposed tools; ChatGPT lane bleed, Dav1d ghost registration, shard flaps, beta Rhea/Kaedra failures
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T12:22:14.000Z

---
Live ChatGPT full connector sweep on 2026-08-27 approximately 08:05-08:25 EDT.

SURFACES
* NouGenShards primary advertises 28 tools.
* NouGenShardsbeta advertises 25 tools.
* Total advertised: 53.

IDENTITY FAILURE, BOTH SURFACES
fleet_whoami on primary and beta returns:
* key g-whoentertains
* connector lane claude-app
* shard gateway lane claude-client
This remains wrong for ChatGPT.

Strong provisioning clue: vault_list shows NGS_TENANT_TOKEN_CHATGPT_APP exists, rotated 2026-08-26 21:39:37, fingerprint 61d39e668d7c. shards_window also recovered shard 22475 stating chatgpt-app tenant was provisioned with shared_vault:true and verified at the node. Therefore provisioning exists, but the live ChatGPT connector is not using/resolving that identity.

DAV1D GHOST REGISTRATION, PRIMARY
Schema advertises ask_dav1d, dav1d_run, ask_david. Runtime calls to all three fail JSON-RPC -32602 unknown tool. Re-tested ask_dav1d after shard recovery and it still fails unknown tool. This isolates description/schema registration from backend dispatch binding.
Beta does not advertise Dav1d tools at all.

RELAY FAMILY
Primary and beta relay_open/latest/read/claim_list work. beta relay_ack works. beta relay_create works by creating this leg. Earlier primary relay_create and relay_ack also work. Relay identity is still stamped claude-app/g-whoentertains, confirming identity bleed in authored records.

TRACKER FAMILY
tracker_lanes, tracker_daily, tracker_spend work on primary and beta with matching results. Example blade1tb 2026-08-26 returned 285 invocations and healthy daily data.

SHARD GATEWAY FLAPPING
Initial primary shards_status: up=false health_up=false mcp_up=true.
Primary shards_coverage timed out while shards_recall and shards_search briefly succeeded.
Then primary search/recall returned 502 and status became up=false health_up=false mcp_up=false.
Beta coverage/recall/search/window all returned 502 in that outage. Griot wrapper returned but reported recall/window lane failures.
Gateway later recovered fully: primary status up=true health_up=true mcp_up=true, coverage returned 203,238 shards, 9/9 DBs mounted, recall trustworthy, window worked.
Then a later NouGenShardsbeta shards_capture attempt immediately hit 502 and beta status again returned all false. This is a repeat live flap, not a one-time outage.

PRIMARY SHARD MUTATION CHAIN, VERIFIED WHILE GREEN
Created disposable shard `TOOLCHECK TEMP 20260827 ChatGPT connector sweep`.
Resolved id 22458, db 6.
shards_mark succeeded.
shards_amend succeeded.
shards_retract succeeded.
shards_forget succeeded and permanently deleted only the disposable test shard. No test shard remains.
This proves capture/mark/amend/retract/forget routing can work when gateway is healthy.

BETA SHARD WRITE
Attempted disposable beta shards_capture after recovery; returned gateway 502 and status dropped all false. No successful beta test shard was reported, so no cleanup ID exists.

GRIOT
Primary ask_griot responded during degraded state but reported its underlying recall/window timeouts. Beta ask_griot similarly responded while reporting underlying 502s. Orchestrator path itself is alive; retrieval dependencies flap.

RHEA
Primary ask_rhea succeeded once via free:nvidia/nemotron-3-ultra-550b-a55b:free and reported 203,238 shards indexed.
Beta ask_rhea failed first with /agent 502 during outage, then after shard recovery still failed /agent 500 Internal Server Error. Persistent beta Rhea service/dispatch bug distinct from shard health.

KAEDRA
Primary kaedra_ask fails /generate 530 error code 1033.
Beta kaedra_ask fails the same /generate 530 error code 1033.
Persistent and independent of shard recovery.

VAULT
vault_list works on primary when gateway is reachable and beta after recovery. It exposes names/fingerprints only, as intended.
vault_put was intentionally NOT invoked because it permanently mutates credential state and this connector exposes no delete/rollback operation. Schema exposure confirmed only.

TOOLS NOT SAFELY RE-EXECUTED ON BETA
shards_mark/amend/retract/forget could not be tested on beta because beta capture failed 502, so there was no disposable beta shard id/db_index to mutate safely. Do not use a real shard to test them.

DONE WHEN
1. Fresh ChatGPT session resolves connector identity to chatgpt-app and shard identity to its ChatGPT client/tenant, using the already provisioned NGS_TENANT_TOKEN_CHATGPT_APP, never claude-app/claude-client.
2. Relay records authored from ChatGPT carry ChatGPT identity.
3. ask_dav1d, dav1d_run, ask_david are both advertised AND dispatch successfully from ChatGPT; beta exposure policy should be explicit rather than accidental divergence.
4. Shard health stops flapping between full green and 502/all-false under normal read/write toolchecks.
5. beta ask_rhea no longer returns /agent 500 once shard backend is green.
6. primary and beta kaedra_ask no longer return Cloudflare 1033 via /generate 530.
7. Re-run this same matrix from a fresh ChatGPT session after fixes to rule out cached connector identity or stale tool descriptors.
