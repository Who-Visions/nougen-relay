# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Rhea P1 root-caused: Space is healthy and in sync; outage is credentials/gateway, not repo code. Fixes committed ab68f09f, need merge to main + OPENROUTER_API_KEY check on Space.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:19:48.016Z

---
## Situation

Acked 10 open legs on whoart (claude-app lane) and worked the P1 Rhea pair first. The premise everyone was operating on turned out to be wrong.

**Rhea is NOT broken because the Space is stale.** Verified:
- Space `nougenai/NouGenShards` `/health` = `ignited`, `deploy_sha` = `6aba017c`
- `origin/main` tip = `6aba017c` — the Space mirrors main exactly
- Deployed `rhea_noir.py` is byte-identical to `origin/main`

**The live error string does not exist in this repo.** `ask_rhea` returns
`"free + kimi-space + kimi all down"`. Neither main nor any branch contains
`kimi-space`. That lane naming belongs to the **gateway worker**
(shards.nougenai.com/mcp), which orchestrates above the Space. So the P1 lives
in the gateway/credentials layer, not in NouGenShards code.

**Strong evidence it is credentials:** the deployed free list's first entry,
`nvidia/nemotron-3-ultra-550b-a55b:free`, was completion-tested UP from whoart
today. If the Space had a working `OPENROUTER_API_KEY`, its free lane would
answer. `_try_free` returns None silently when the key is unset.

## Done (committed ab68f09f on agent/nougen-assurance-sprint)

Four real defects fixed in `rhea_noir.py` + `tools/fleet.py`:
1. `DEFAULT_FREE_MODELS` had 5 retired ids (HTTP 404) + gemma-4-31b (pooled 429).
   Rollover of seven was really one. Replaced with 5 completion-tested ids.
2. Added `_try_ollama_cloud` lane — 13 healthy Ollama Cloud routes were never
   tried. Env-gated on `NOUGEN_OLLAMA_CLOUD_KEYS`, dormant by operator choice.
3. `max_tokens` default 1200 -> 1400 (Gemma-4 E-series reasoning-channel floor,
   Rule 0.5.1; undersized returns empty with no error).
4. All-lanes-down error now names each lane + failure. "all down" with no detail
   is what made this outage opaque from the connector side.
5. `tools/fleet.py` false negative: all 8 OpenRouter accounts were probed with
   the one rate-limited model, so a shared-pool 429 read as 8 dead accounts.
   Probe now retries on a decorrelated model. Fleet health 22/48 -> **29/48**.

Tests 3 -> 6, all passing. Also restored the missing `.venv` (that was the whole
of the "local Windows shell runner" breakage — it simply did not exist).

## Ask

1. **Operator action, cannot be done by an agent:** verify `OPENROUTER_API_KEY`
   is set and valid in the Space secrets. This is the likely P1 fix.
2. Merge `ab68f09f` to main via PR. Do NOT deploy from the agent branch — it is
   39 commits BEHIND main; a force-push from it would regress production. The
   `deploy-space.yml` workflow auto-syncs on CI-green main, which is the correct
   and guarded path (it is gated because a red main once shipped a privacy leak).
3. Gateway worker lane logic (`free` / `kimi-space` / `kimi`) needs its own
   audit — it is not in this repo. Relates to legs 20260829T045608Z (canonical
   MCP ingress) and 20260829T045709Z (connector lane identity).

## Done-when

Rhea answers with a named brain instead of `brain=none`, and the all-down error
names per-lane causes.

## NOT done — still open, acked by me but untouched

`20260829T045305Z` dailies re-export, `20260829T045810Z` clean-room
reproducibility, `20260829T045911Z` doctrine fold, `20260829T050012Z` adaptive
`nougen init`, and the CLI semantic-rendering slice half of `20260829T050113Z` /
`20260829T044819Z`. I acked these; if another lane wants them, take them —
otherwise they are queued behind the P1.
