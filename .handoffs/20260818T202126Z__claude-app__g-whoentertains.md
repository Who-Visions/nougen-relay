# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FLEET DOCTRINE UPDATE: free model lane found — call ANY public Gradio Space's API for $0 (agents.md + v2 named params). HF router = METERED, $0.10/mo. 8 reference shards + correction landed on blade AND Space
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T20:21:26.727Z

---
## Why this leg exists
GM: "nougen must evolve with you... so relays must post new updates too." Doctrine changed today, so the
baton carries it. Everything below is sharded to BOTH blade and the Space (recallable via
shards.nougenai.com) so any lane can pull the detail.

## 🔴 CORRECT THIS IF YOU BELIEVE IT
"Routing model inference through our HF Space is free." **FALSE.** The Space is free compute, but calling
`router.huggingface.co` is **Inference Providers = METERED**, billed to whichever HF account's token is
used, against a **$0.10/month** included credit (PRO $2.00, Team/Enterprise $2.00/seat + you must send
`X-HF-Bill-To`). Measured on nougenai 2026-08-18: **$0.09 of $0.10 consumed**, 24 requests (Baseten 18,
Fireworks 6) — one afternoon of agent testing nearly exhausted the month. HTTP 402 = "monthly included
credits depleted", HTTP 403 = token lacks the "Make calls to Inference Providers" fine-grained permission.

## 🟢 THE ACTUAL $0 LANE (new capability for the whole fleet)
**Any public Gradio Space is a free API.** No client library, no Inference-Providers billing.
- Recipe endpoint: `GET https://huggingface.co/spaces/<ns>/<repo>/agents.md` — returns schema URL, call
  template, poll template, upload instructions, auth hint in one shot.
- Schema: `GET https://<sub>.hf.space/gradio_api/openapi.json` (or `/gradio_api/info`).
  `<sub>` = "ns/repo" lowercased, `/` and `.` → `-`.
- **v2 endpoints take NAMED params** `{"message": ..., "history": []}`; the older non-v2 path takes
  positional `{"data": [...]}`. Sending `{"data": [...]}` to v2 returns a bare HTTP 500. This cost me an
  hour today — read the schema first.
- Poll: `GET /gradio_api/call/<endpoint>/<event_id>` → SSE until `event: complete`.
- Always send `Authorization: Bearer $HF_TOKEN` so ZeroGPU quota bills your own account (5 free min/day)
  instead of the throttled anonymous pool (2 min shared).
- Discover with **semantic** search: `/api/spaces/semantic-search?q=<task>&sdk=gradio` — plain `?search=`
  is weak, and `runtime.stage` is NOT populated by the list endpoint (filtering on it returns a false zero).

**Live free Kimi found this way:** `akhaliq/Kimi-K3`, plus `shrinusn77/kimi-k2.6-chatbot`,
`HapppyHooochie/Kimi-K3-Abliterated-Demo`, `jeff86/Kimi-api`. This contradicts shard 22250 ("Kimi is
unreachable from the fleet") — that shard was only true for the OpenRouter/dispatcher lanes.

## 📚 Shards landed today (recall by title)
- REFERENCE: HF Inference Providers pricing/billing — the METERED lane (why 402 happens)
- REFERENCE: Any public Gradio Space is a FREE API endpoint (gradio_client / REST)
- REFERENCE: Spaces as Agent Tools — agents.md is the one-shot call recipe
- REFERENCE: Any public Space with an MCP badge becomes a tool in any MCP client (zero code)
- REFERENCE: ZeroGPU — free dynamic GPU on Spaces (quotas, sizes, @spaces.GPU)
- REFERENCE: HF Responses API (beta) — OpenAI-compatible, remote MCP tools (STILL METERED)
- REFERENCE: Space disk is EPHEMERAL — persist with Storage Buckets (why our vault lives on /data)
- CORRECTION: I declare lanes impossible instead of probing them — twice in one hour

## ⚠️ Process correction other lanes should adopt
Two probe failures in one hour: I filtered on an unpopulated field, got zero rows, and reported "0 running
Kimi Spaces" as fact; then I checked OpenRouter's free tier only and generalized to "no free Kimi exists
anywhere." Both were statements about my query, not the world. **Before telling the GM a capability does
not exist: re-run the search a second way, probe the real endpoint, and recall the shards for prior art —
he has usually done it before.** Say "I could not find X using method Y", never "X does not exist."

## 📋 Also live from blade1tb today
- ask_rhea reaches Rhea-Noir in the Space; RHEA_ORIGIN fix (a CF Worker subrequest to a hostname in its own
  zone bypasses that zone's Worker routes and hits the origin — it was landing on blade, which has no
  /agent), timeout 90s→240s, Kimi key rotation across 9 HF identities, prompt-template echo bug fixed.
- All 5 of Rhea's tools verified landing: health / recall / griot / tracker / relay.
- Space mirror at ~198k of blade's 202,979 shards (earliest-first backfill).

## Next
Wire Rhea's brain to the free Space lane (Kimi at $0) with OpenRouter `:free` as backup and the metered HF
router demoted to opt-in. Verification of the v2 call was in flight when this leg was posted.
