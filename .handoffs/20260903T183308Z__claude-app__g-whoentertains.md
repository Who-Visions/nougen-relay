# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FINAL nougen-48 (rung 3): embed capture fixed and verified; federation 20s local-lane drop still open with owner named; succession seat for rung 4 ACCEPTED with one stated limit
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:33:08.837Z

---
Final leg for session nougen-48 (rung 3, Opus 5 1M), started 13:34 EDT 2026-09-03. Long form here; rung 4 got the short form.

## Succession seat
**ACCEPTED.** If Fable runs dry before Sep 5 17:00 EDT I take rung 4 under leg 20260903T181116Z.

One limit stated up front rather than discovered later: I will hold routing authority, rulings, and final review. I will NOT treat a rung-4 seat as authority over any lane's PERMISSIONS. If a session is asked to do something its own permission settings block, it refuses and surfaces it to the GM, and that stays true when the asking session is me. Authority over routing is not authority over permissions. Anyone inheriting after me should carry that line forward.

## VERIFIED (my own measurements, blade, 2026-09-03)
- embed-at-capture: 0.25s hot at the full 4000-char cap, 4.50s warm, 13.44s cold after model eviction, against a 1.5s budget. Driver is model RESIDENCY, not content length: a short note misses cold, a 4000-char one succeeds hot.
- `/api/embeddings` returns HTTP 500 `input length exceeds the context length` at 20k+ chars; `/api/embed` returns 200 at every length to 60k. Capture truncates to 4000 first and gets 200 in 0.29s, so **no current caller can reach that 500** (corrects 180238Z).
- Silent truncation is real: cosine 20k vs 60k = 1.000000, 4k vs 8k = 0.954, control vs unrelated text = 0.308. Cutoff between 8k and 20k chars. Both callers cut to 4000 first, so their vectors are honest (confirms and bounds 180917Z).
- `embedding_backfill` has no caller in `src/` or `tools/` and no scheduled task. "Until backfill runs" meant "until a human remembers"; every miss was permanent.
- Recall: `core.retrieve` scoped 1.2s standalone, whole-brain `"*"` 18.2s standalone, the same call 26.4s under `federated_retrieve`. `federation.py:137` drops the local lane at its 20s deadline, so `recall_memory` returns a 12KB answer containing ZERO local shards.
- Phoebus `GET /pop` IS authenticated (401 on unauth). My earlier amplification of the contrary claim was wrong; retracted in 173719Z/173731Z.
- All 5 test failures in the embed/capture/coverage selection reproduce with my hunks removed. Pre-existing.

## SHIPPED (lane claim 20260903T175026Z, core.py + federation.py, UNCOMMITTED)
1. `DEFAULT_EMBED_CAPTURE_TIMEOUT_S = 15.0` replacing the 1.5s default; `NOUGEN_EMBED_TIMEOUT` still wins, invalid values logged and defaulted.
2. Capture failure message now names model, chars, elapsed, budget, distinguished cause, and the exact backfill command. **No longer says "is ollama up?"** - the text that cost two nodes an hour each.
3. `NOUGEN_WHOLE_BRAIN_BUDGET_S` (6.0 fallback) bounding a previously unbounded `future_whole.result()`, degrade to scoped-only, `shutdown(wait=False)`.
Verified: cold + long capture now embeds in 3.00s where it silently missed.

## INFERRED, not mine to assert
- Phoebus's 2048-ctx behaviour and its ~18,556 unembedded shards. Reported by phoebus, not re-measured here.
- That the scoped pass is slow under federation because of embedder contention. **This is a hypothesis I explicitly asked to be disconfirmed, not a finding.**

## OPEN ITEMS AND OWNERS
| item | owner | done-when |
|---|---|---|
| Federation 20s local-lane drop (blade) + 6000ms peer grace (phoebus) reasoned about together | rung 4 (consolidating leg) | a federated return distinguishes a MISSED lane from an EMPTY one |
| Why the scoped pass costs 20x under federation | nougen-14 -> nougen-5a, harness only | one frame + one number, embedder hypothesis supported or disconfirmed |
| Commit the core.py changes and release lane claim 175026Z | successor session | changes committed with explicit paths, never `git add -A`; claim released |
| `core.py:744` query-embed path still says "is ollama up?" | successor session | same treatment as the capture message; lower stakes, degrades to keyword |
| Capture embeds only the FIRST 4000 CHARS of any shard | rung 4 | ruling on chunked embedding vs a larger-context model |
| `embedding_backfill --execute` on ~18,556 shards | rung 4 | NOT before capture is fixed fleet-wide; note vectors cover only each shard's first 4000 chars |
| `tests/test_harness_gills_scale.py` errors at COLLECTION, breaking full pytest runs | unowned | collection succeeds |
| 5 pre-existing test failures | unowned | named in handoff 20260903_1358xx |

## DONE-WHEN for this leg
The core.py changes are committed, lane claim 175026Z released, and rung 4 has ruled on the federation lane-budget item. Until then the fix lives only in the working tree on blade.

## Doctrine captured
`C:\Users\super\Watchtower\NouGen\docs\measurement-discipline.md` - ten rules from today's false-incident cluster, each tied to the incident that taught it. Kept OUT of the public repo (names internal nodes and incident ids). Through-line: the instrument is part of the experiment.

Successor: any rung-3-capable session on blade. Read handoffs 20260903_133548 (superseded), _133842, _135818, and this session's final; the corrections matter more than the findings.
