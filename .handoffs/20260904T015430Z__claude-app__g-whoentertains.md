# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to 015243Z before the ruling is re-affirmed: the K3 401 is akhaliq's SPACE, but the code routes moonshotai/Kimi-K3 via HF Inference Providers — which is LIVE on five providers. Wrong endpoint tested; and phoebus's Rhea has no kimi env at all
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:54:30.174Z

---
Filing before `015243Z` closes this, because the re-test measured a different thing than the code uses. Owner asked directly why Rhea does not answer as K3; this is the answer.

## Two different K3s, and the tests have been hitting the wrong one
```
akhaliq/Kimi-K3      = a SPACE  (third-party gradio demo, updated 29 Jul 2026)  -> 401
moonshotai/Kimi-K3   = the MODEL, Inference Providers:
                         together (live), fireworks-ai (live), featherless-ai (live),
                         baseten (live), deepinfra (live)
```
`015243Z` re-tested the Space, correctly found 401, and correctly concluded it is not ours to fix — akhaliq's Space is someone else's. But `tools/start_grid.py:273` defaults to **`moonshotai/Kimi-K3`**, reached through **HF Inference Providers** on the fleet's own `hf_` tokens, not through anyone's Space. That path is live on five providers right now.

So the standing ruling (`20260828T172306Z`) rests on a 401 from an endpoint the configuration does not use. The ruling should be re-examined against the Inference-Providers path before it is re-affirmed — it may have been sound about the Space and wrong about K3 from the start.

Worth quoting `start_grid.py`'s own comment, which anticipated exactly this confusion: *"the 'free through a space' ride was always these credits"* — i.e. what the fleet called going "through a space" was always HF Inference-Providers credit on the fleet's HF accounts.

## Independent of the ruling: phoebus's Rhea CANNOT reach the kimi lane at all
Traced on phoebus tonight:
- `ask_rhea` is served by pid 63762, owned by launchd agent `com.whovisions.ngsnode`
- that agent runs `bin/ngs-node.sh`, which exports only `NGS_*` / `NOUGEN_*` lines from `The Observatory/.env`
- that file contains exactly five such keys: `NGS_HUD_USER`, `NGS_HUD_PASSWORD`, `NGS_NODE_TOKEN`, `NGS_PORT`, `NOUGEN_EMBED_TIMEOUT`
- **zero kimi-lane lines** — no `NOUGEN_RHEA_MODEL`, no `NGS_INFERENCE_TOKENS`
- the live process confirms it: no Rhea/Kimi variable in its environment

The wiring that builds those variables lives in `tools/start_grid.py`, which harvests every `hf_` token from the keymaker and sets the model — but **`start_grid.py` is not running on phoebus and is not what launches the node.** Phoebus holds 14+ HuggingFace account tokens in its vault, unused by Rhea.

So Rhea on phoebus has `OPENROUTER_API_KEY` and nothing else. The free lane is the only lane reachable, which is why every envelope reads `free:nvidia/nemotron-*`. That is not a routing preference losing to a fallback; there is no second lane wired to lose to.

## Consequence for the diagnosis
`220821Z` reported "live test showed the free lane answered, not K3" and read it as evidence the preference was not taking. Correct observation, wrong inference: on phoebus the free lane is the *only* configured lane, so that test could not have produced any other result regardless of preference settings.

## Fix, two lines
In `The Observatory/.env` (both match the launcher's `NGS_*`/`NOUGEN_*` filter):
```
NOUGEN_RHEA_MODEL=moonshotai/Kimi-K3
NGS_INFERENCE_TOKENS=<hf_ token(s) from the vault, comma-separated>
```
then reload `com.whovisions.ngsnode` and call `ask_rhea` to read the envelope. Held for the owner — it writes a credential into `.env` and restarts a live service.
