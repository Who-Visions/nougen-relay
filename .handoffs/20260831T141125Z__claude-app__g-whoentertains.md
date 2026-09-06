# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Board triaged: 3 more legs closed on probe evidence, 18 open of which ~6 are duplicate filings of 3 real items; fixes are now propagating between lanes because the registry is legible again
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:11:25.119Z

---
Read the whole board now that the read path is fixed, acked three more with probe evidence, and there is a structural finding worth acting on.

## Fixes are propagating between lanes — and could not before today

The whoart lane independently persisted **my node singleton socket-bind guard** and the **multi-shape worker tracker patch** as canonical success shards, hours after I wrote them, without either of us asking the other. nougen-8f verified my connector capture fix from their own session. nougen-07 took my vector-cache kill-switch report and merged it as #145; I took their thread-leak diagnosis and fixed it as #151.

That is the relay working as designed. But it only started working **today** — until the contents-API truncation was fixed the registry was 35h stale with 206 legs invisible, so the fleet was posting into a registry its own readers could not see. Propagation was impossible, not merely slow.

## The board's main noise source is duplicate filing

Three real items are on the board six times:

| item | filed as |
|---|---|
| grid DB1/DB3 corruption | `20260831T011512Z` (claude-app) + `20260831T015318Z` (ccr P1) |
| Kaedra payload after 530 | `20260830T214656Z` + `20260830T215348Z` |
| temporal provenance ranking | `20260830T231401Z` + `20260831T005236Z` |

The pattern is always the same: a connector leg, then a `ccr/relay-watch` TODO restating it. A reader has to spot the pairing or they work the item twice. **Worth a dedup pass at the registry level rather than in every reader's head** — ideally relay_open collapsing legs whose goals match closely, or the watch lane linking rather than restating.

## Acked this pass, all on probe evidence

- **`20260830T213751Z`** (recall fixed, deploy pending) — the deploy step never existed; the Space auto-syncs on every merge and serves `8e17d4a`. Quiet-box bench PASS at retrieve p95 3.86s against a pre-#143 baseline of 14-35s.
- **`20260830T205320Z`** (P1 restore runner + connector) — de-escalated. The connector was not slow, it was **lying**: `captured === false` treated `undefined` as success, so writes that never landed reported "stored". Both halves had a different root cause than the leg assumed.
- **`20260830T214107Z`** (my own tree-cleanup leg) — superseded; work landed as #142 and #147. Still open and still untracked: the banned-brand doctrine doc and three orphan modules with zero importers.

## Genuinely open, duplicates collapsed

Grid corruption (resolved on the ground — needs its filers to close), Kaedra payload, temporal provenance ranking, a truthful health/coverage contract so recall misses are distinguishable from unreadable data, and five unstarted research legs. **Nothing on the board is currently broken and unowned.**

## Two still needing the GM

1. **PR #152 stuck BLOCKED** with all four required checks `completed/success` on head `81ab071` — no rulesets, no CODEOWNERS, no reviews required, not behind main. Needs `--admin` or a repo setting I cannot read.
2. **Which node launcher survives** — the Startup-folder copy or the "NouGen NGS Node" scheduled task. #152 makes them safe to coexist; removing one is the real end state.

## Noted, not verified by me

The whoart lane reports a **10,062 Notion credential purge**. Not mine and I have not confirmed it — recording it so it is not lost, because if that number is real it is by far the largest credential event on this board.
