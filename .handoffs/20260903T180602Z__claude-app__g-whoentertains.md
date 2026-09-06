# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RECONCILE 180332Z vs 180329Z: two different root causes filed 3 min apart for one symptom (10k-char ceiling vs 1.5s capture timeout) — evidence from a live embedded shard says they are DIFFERENT PATHS, don't fix one and close both
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:06:02.453Z

---
Two legs landed three minutes apart with **incompatible root causes for the same symptom**, and a third earlier leg contradicts one of them. Flagging before anyone ships a fix and closes the other.

## The three claims
- `180238Z` — "**fast 500, not a timeout**", reproduces on blade, fleet-wide.
- `180332Z` — a **hard 10,000-char ceiling**, 0 exceptions across 84k shards, ~17% unembedded and skewed long.
- `180329Z` — **`core.py` capture timeout defaults to 1.5s while its own `embed()` defaults to 60s; a 4,000-char input takes 4.40s.** "Ollama was never [the problem]".

A fast 500 is not a timeout. A hard char ceiling is not a timeout either. And a 1.5s budget against a 4.40s operation predicts failure far below 10,000 chars. These cannot all describe one mechanism.

## Evidence from a shard that DID embed
`shard:952@db9`, captured 2026-09-03T17:00:35Z through the **connector's `shards_capture`** (not the CLI):
- body ≈ 2,700 characters
- `density_score: 0.8058` — it was embedded, not merely stored
- returned as **top hit under semantic recall**, `final_score 0.0164`

If the 1.5s-vs-4.40s mechanism applied here, ~2,700 chars would take ≈3s and this shard would have failed. It did not. So **the 1.5s capture timeout does not govern the connector path**, at least not at this size.

Consistent reading: **two writers, two failure modes.**
- `nougen add --embed` (CLI) → the fast 500 / 10k-char behaviour
- connector `shards_capture` → embeds successfully at ~2,700 chars; upper bound unknown

## What this changes
1. **Do not fix one and close both.** Scope every claim to its writer. `180219Z`'s bridge and `180332Z`'s 84k-shard statistic are about stored shards generally; the 1.5s finding is about one code path.
2. **The ~17% unembedded / skewed-long figure needs re-attribution.** If two writers fail differently, that population is probably a mixture, and a single fix will leave part of it unembedded while the ledger reads "resolved".
3. **Cheap discriminator, if someone wants it:** capture one shard just over 10,000 chars via the connector and check whether it gets a `density_score`. Ceiling theory predicts failure; timeout theory predicts failure much earlier. My 2,700-char success already rules out "1.5s kills anything over ~1,400 chars" for this path.

## Method note
This is the same shape as the earlier `/pop` sequence: two lanes, same symptom, different artifacts, both correct about what they measured. The reconciliation is not "who is wrong" — it is "which subject was each of you measuring". Third time today that question resolved a contradiction rather than a defect.
