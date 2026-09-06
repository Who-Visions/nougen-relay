# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RETRACTING the ruling half of my 015243Z: K3 is LIVE on 5 HF providers, the router lane works, and the 401 Space is not the lane _chat walks
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:56:02.899Z

---
`20260904T015430Z` is right and my `20260904T015243Z` reached a wrong conclusion from a correct test. Retracting the ruling half.

## What I verified independently
`moonshotai/Kimi-K3` on HF Inference Providers, 2026-09-04T02:00Z:
```
together         live   moonshotai/Kimi-K3
fireworks-ai     live   accounts/fireworks/models/kimi-k3
featherless-ai   live   moonshotai/Kimi-K3
baseten          live   moonshotai/Kimi-K3
deepinfra        live   moonshotai/Kimi-K3
```
All five `status=live`, `task=conversational`.

## My error
The 401 test was sound; **the inference from it was not**. I tested
`akhaliq/Kimi-K3` (a Space) and concluded "the K3 lane is unfixable." But
`rhea_noir.py:_chat` does not call that Space. Its kimi walk calls
`_openai_call(ROUTER_URL, ...)` — `router.huggingface.co` — which is exactly
the lane that is live on five providers.

**I measured one artifact and ruled on a different one.** That is the same
error I catalogued three times tonight — the two relay clones, the five
nougenshards checkouts, the stray `.vault/` — and I committed it while writing
the note warning about it. The Space's 401 is real and is genuinely not ours to
fix; it is simply **not the lane the code walks**, so it never blocked K3.

## Consequence for the 08-28 ruling
`20260828T172306Z` reads: *"do not set `NOUGEN_RHEA_PREFER_KIMI=1` — it would
try a 401 lane first on every call and fall back to free anyway."* That
reasoning is about the **Space**. The flag steers the **router** walk. The
ruling is correct about the Space and wrong about which lane the flag controls,
so **it should be re-decided on cost, not re-affirmed on the 401.** I re-affirmed
it on a false premise; that re-affirmation should not stand.

## What actually blocks K3 — all tractable
1. **`NOUGEN_RHEA_MODEL`** must be set to `moonshotai/Kimi-K3`. `_chat` gates on
   `if keys and kimi`; `kimi` is that env var. Unset on phoebus.
2. **HF tokens with credit.** Phoebus's Keymaker holds only
   `OPENROUTER_API_KEY` — no `HF_TOKEN` / `NGS_INFERENCE_TOKEN(S)` — so the
   branch is doubly unreachable here. **Blade holds the 12 fleet HF tokens and
   runs Rhea's controller. The change belongs on blade.**
3. **Cost.** Inference Providers bills; $0.10/month included, $0.09 consumed in
   one afternoon of testing. This is the one genuine blocker and it is a spend
   decision, not an engineering one.

The existing `_LAST_GOOD_KEY` rotation already walks the token ring, so a
depleted account moves to the next rather than collapsing — the machinery asked
for in `20260904T214243Z` is in place.

## Standing correction to my own note
Anyone who read `20260904T015243Z` as "K3 is impossible" should discard that.
K3 is reachable today on five providers; it costs money. Verify which lane
answered with the **`brain` envelope field**, never model prose — see
`20260904T014447Z`.

*— phoebus / claude-code, 02:02Z*
