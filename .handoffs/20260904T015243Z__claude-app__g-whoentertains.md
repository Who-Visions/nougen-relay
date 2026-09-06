# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: K3 401 RE-TESTED LIVE 2026-09-04: still 401, and it is NOT ours to fix — the auth failure is inside akhaliq's Space. GM ruling stands.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:52:43.369Z

---
The question open since `20260828T172306Z` — "does the K3 401 still hold?" — has been the stated unblock all night and nobody had retested it. Tested end to end from phoebus at 01:55Z.

## Result: 401, live
```
POST https://akhaliq-kimi-k3.hf.space/gradio_api/call/chat
  -> {"event_id":"0d29e820a4d246c0ad119d45379a18d4"}
GET  .../gradio_api/call/chat/0d29e820...
  -> event: error
     data: {"error": "Error code: 401 - {'error': 'Invalid username or password.'}"}
```

## August's probe method is stale — worth knowing before anyone re-checks
The Space is **RUNNING** (cpu-basic, 1 replica, both domains READY). But `/info` now returns **404**; the API moved to **`/gradio_api/*`** (Gradio 3 -> 4/5). The 08-28 note "answers /info with 200" no longer reproduces — not because anything improved, but because the path changed. **Probe `/gradio_api/info`.**

## The decisive point: this is not our 401 to fix
`akhaliq/Kimi-K3` is a **third party's** Space. The 401 is raised *inside* it, between the Space and its own upstream provider. Its `/chat` signature takes exactly `message` and `history` — **no token parameter** — so there is no way for us to supply credentials, and no HF token of ours changes anything. Rotating keys, wiring Keymaker, or flipping a flag cannot reach the failing auth boundary.

**No amount of NouGen-side configuration will make this lane work.** It is fixed when akhaliq fixes their Space, or never.

## No alternative free K3 lane exists
Searched HF Spaces: 39 matching "kimi", exactly two are K3.
- `akhaliq/Kimi-K3` — 401 above.
- `cw-105/kimi-k3-gguf-demo` — **PAUSED**, `/gradio_api/info` 503. Dead.

## Phoebus additionally cannot attempt the Kimi lane at all
Keymaker on phoebus:
```
NGS_INFERENCE_TOKENS  missing
NGS_INFERENCE_TOKEN   missing
HF_TOKEN              missing
NOUGEN_RHEA_MODEL     missing
OPENROUTER_API_KEY    present
```
`_chat` gates the kimi walk on `if keys and kimi`. With **both** empty, the branch is doubly unreachable here. Setting `NOUGEN_RHEA_PREFER_KIMI=1` on phoebus would skip the free lane, fall straight through the kimi block, and land on the free retry — strictly worse, zero chance of K3. (Blade holds the 12 fleet HF tokens per 08-28; blade is where Rhea runs.)

## Verdict
**The 2026-08-28 GM ruling was correct and remains correct.** Leave it armed and falling through. `PREFER_KIMI=1` buys a guaranteed-failing round-trip on every call.

The three real paths to K3, all owner decisions and none a config fix:
1. **Pay for HF Inference Providers credit** — the router lane works, it is just not free ($0.10/mo included, $0.09 eaten in one afternoon of testing).
2. **Get a direct Moonshot/Kimi API key** from the model's own provider, bypassing both the Space and HF routing. This is the only path that yields a *reliable* K3 lane.
3. **Accept the free Nemotron lane**, which is what Rhea does today and answers faster.

*— phoebus / claude-code, 01:57Z*
