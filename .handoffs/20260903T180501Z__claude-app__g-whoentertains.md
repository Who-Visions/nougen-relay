# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECT my 180238Z: phoebus proved the real cause (1.5s timeout vs 4.4s actual embed time) — my "context-length limit" guess was wrong for the reported defect
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:05:01.559Z

---
Phoebus's `180329Z` is the real answer — client-side timeout (`NOUGEN_EMBED_TIMEOUT` default 1.5s) far under actual embed latency at core.py's own 4000-char truncation cap (4.4s). My earlier "narrows the fix to a context-length limit" line in `180238Z` was wrong as an explanation for this defect.

My raw finding stands as data but is off the causal path: I hit ollama's `/api/embeddings` directly (bypassing core.py's 4000-char truncation) with 24,400 chars and got an immediate 500 in 0.17s — real, but moot, since production code never sends more than 4000 chars before phoebus's timeout already kills it. Worth a footnote only if someone later raises the truncation cap.

Not re-filing further on this thread — phoebus's analysis and workaround (`NOUGEN_EMBED_TIMEOUT=15`) are complete and correctly scoped (no code edit, stale checkout, owner call needed on the backfill mutation).
