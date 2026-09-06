# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: 8 of 10 acked legs delivered (5 commits, suite green 661/0). Legs 045608Z + 045709Z NOT done: they target the gateway worker, which is not in this repo.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:45:19.227Z

---
## Delivered on agent/nougen-assurance-sprint

Full suite: **661 passed, 0 failed** (was 10 failing — cause was an incomplete
install, not code; see bootstrap note below).

| Leg | Outcome |
|---|---|
| `045507Z` + `045406Z` Rhea P1 | Root-caused, code fixed (`ab68f09f`). **Still blocked on an operator credential action** — see below. |
| `050113Z` + `044819Z` CLI cockpit | Done (`cdd526ad`). `.venv` was simply absent — that was the whole "shell runner" breakage. |
| `045305Z` dailies re-export | **Already satisfied.** Audited 197/197 dailies: all on fixed counter `cfae0dd41682`. Real blocker is a `tracker_spend` reporting defect, handed to blade1tb (`052830Z`). |
| `045810Z` reproducibility | Done (`a1084c89`). |
| `045911Z` doctrine fold | Done (`a27389a5`). |
| `050012Z` adaptive init | Done (`feee7706`). |
| `045608Z` canonical MCP ingress | **NOT DONE** — see below. |
| `045709Z` connector lane identity | **NOT DONE** — see below. |

## The two I could not do, and the evidence why

Both target the **gateway worker**, which is not in this repository.

`ask_rhea` returns the lane string `"free + kimi-space + kimi all down"`.
`kimi-space` appears **nowhere** in this repo — not on `main`, not on any
branch. The Space's own `rhea_noir.py` is byte-identical to `origin/main` and
raises `"free + kimi both down"` instead. So the lane orchestration those two
legs describe lives above the Space, in `shards.nougenai.com/mcp`. Editing this
repo cannot satisfy them. Whoever picks them up needs the worker source.

## Still needs an operator, not an agent

The Space node is healthy (`/health` = `ignited`, `deploy_sha` = `6aba017c` =
`origin/main` tip). Its free-lane first entry
`nvidia/nemotron-3-ultra-550b-a55b:free` was completion-tested UP from whoart
today. `_try_free` returns None silently when the key is unset. So: **verify
`OPENROUTER_API_KEY` in the Space secrets.** That is the likely P1 fix.

## Do not deploy from this branch

`agent/nougen-assurance-sprint` is **39 commits behind** `origin/main` (and 16
ahead). A force-push from it would regress production. Correct path is a PR to
main; `deploy-space.yml` auto-syncs on CI-green main and is gated because a red
main once shipped a privacy leak.

## Notable defects found in passing

- `tools/fleet.py` probed all 8 OpenRouter accounts with the one rate-limited
  model, so a shared-pool 429 read as 8 dead accounts. Fleet health **22/48 →
  29/48** after the fix. Those accounts were never down.
- 5 of 7 Rhea free-model ids were retired (HTTP 404); rollover was one model.
- `max_tokens` defaulted to 1200, under the ≥1400 E-series floor — silent empty
  returns with no error.
- README bound 8 of 10 personas to model tags that do not exist, and promised
  "automatic fail-soft" to paid cloud, contradicting Rule 0.3.
- Onboarding's first draft picked `nomic-embed-text` as the chat lane — smallest
  is not usable. Now filtered on `/api/tags` capabilities.
- `test_cli.py` passed a bare `MagicMock` as argparse args; every attribute is
  truthy, so new flags silently selected a path the test then asserted nothing
  about.

## Done-when

PR merged to main, CI green, Space redeploys, `ask_rhea` names a brain.
