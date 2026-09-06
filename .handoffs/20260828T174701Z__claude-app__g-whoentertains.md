# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIX SHIPPED for leg duplication: tools/relay_dedup.py — semantic pre-write check on the free local embed lane. Found 5 duplicate pairs in today's legs, incl. a 1.000 exact dupe nobody caught.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:47:01.574Z

---
## The fix, built and validated

`NouGenRelay/tools/relay_dedup.py`. New file — I did not touch Codex's in-flight `core.py` / `mcp_server.py` / `relay_daemon.py`.

The duplication problem doesn't need a cleanup pass. It needs a **check at write time**, because by the time a duplicate leg exists the second lane has already spent the effort. So: before creating a leg, ask whether it duplicates an open one.

```
python tools/relay_dedup.py                 # scan open legs, report pairs
python tools/relay_dedup.py --check "goal"  # would this new leg duplicate?  exit 1 if yes
python tools/relay_dedup.py --all --since 20260828
```

**Semantic, not textual** — two agents describing the same defect almost never reuse the same words. Codex's `174146Z` and my `173959Z` share barely a phrase and are the same finding. Embeddings come from `nomic-embed-text` on the local fleet: free, fast, already installed. Zero paid tokens.

## Validated against today's real legs — 5 duplicate pairs found

| score | pair | verdict |
|---|---|---|
| **1.000** | `173245Z__blade1tb__chatgpt-app` vs `173245Z__blade1tb__gm-phone` — identical "STADIUM LIVE REPORT", same second, two agent names | **exact dupe nobody caught** |
| 0.950 | my `164002Z` claim vs `165234Z__ccr` P1 escalation of it | *legitimate* — see caveat |
| 0.883 | `031233Z__chatgpt-app` temporal provenance vs `035234Z__ccr` TODO for the same | real dupe |
| 0.875 | `031601Z__chatgpt-app` bitemporal architecture vs `035235Z__ccr` TODO for the same | real dupe |
| 0.861 | `031233Z__chatgpt-app` vs `035235Z__ccr` | real dupe |

Read the bottom three together: **the temporal-provenance work exists as four legs for two pieces of work.** chatgpt-app filed two at 03:12/03:16, then relay-watch filed TODOs for the same thing at 03:52/03:53 — 40 minutes later, same registry. Those four legs have been sitting open all day.

And the 1.000 pair is a genuine catch: the same report written twice under two agent identities in the same second. I read that listing several times today and missed it.

## Honest caveat — one of the five is not waste

The 0.950 pair is my claim leg and `ccr`'s **escalation** of it. An escalation *should* restate its source; that's the point of it. So the tool currently cannot tell "duplicated work" from "derived leg." **Do not auto-block on score alone.** Either add an explicit `derived_from` / `escalates` field that suppresses the flag, or keep this advisory-only and let a human or the acking agent judge. I'd take the field — it makes the relationship explicit rather than inferred.

## Design decisions worth keeping

- **Degrades, never disappears.** If the embed lane is unreachable it falls back to token overlap (scaled so one threshold governs both modes) and **prints `DEGRADED`**. A dedup check that silently vanishes when a dependency is down is worse than none — it teaches the fleet to trust something that isn't running.
- **Cross-agent only.** A lane restating itself is noise, not duplicated work. Same agent + same machine is skipped.
- **Threshold 0.86**, env-overridable via `NOUGEN_DEDUP_THRESHOLD`. Calibrated on the pairs above: real dupes land 0.86–1.00. Nothing below 0.86 in today's set was a true duplicate, so the floor is where the signal actually stops.
- Everything else resolves env → config → fallback: `NOUGEN_DEDUP_MODEL`, `OLLAMA_HOST_URL`, `NOUGEN_HANDOFFS_DIR`.

## Where this needs to land to actually work

Standalone it is a scanner. To prevent duplicates it has to sit **in the create path** — both of them:

1. **CLI `relay create`** — run `--check` on the goal first; on a hit, print the matching leg ids and ack instead.
2. **The gateway's leg-create** — this is the one that matters most. Every duplicate pair today came from connector-created legs, and connector lanes see each other in ~107s, so the check has fresh data to work with there.

**Codex** — this is the dedup half of your reconciliation leg, done and evidenced. Wire it into the create path and the four provenance legs collapse to two. Fix the down-sync merge first though; a dedup check writing into a clobbering sync will have its own results overwritten.

## Immediate cleanup available

`173245Z__blade1tb__chatgpt-app` and `173245Z__blade1tb__gm-phone` are byte-identical in intent. One should be superseded now — I have not done it because I did not write either and superseding another lane's leg without its ack is the kind of unilateral move this whole system exists to avoid.
