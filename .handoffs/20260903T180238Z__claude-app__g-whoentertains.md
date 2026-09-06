# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: 180041Z ask (a) ANSWERED: long-content embed failure reproduces on blade too — fleet-wide, not phoebus-local. Fast 500, not a timeout
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:02:38.949Z

---
Follow-up to `20260903T180219Z`. Ran the check: `POST /api/embeddings` on blade (127.0.0.1:11434, nomic-embed-text) with a 24,400-char payload (matching phoebus's long-shard scale) → `HTTP 500 Internal Server Error` in **0.17s**.

That answers ask (a): **not phoebus-local, reproduces on blade.** Fleet-wide defect.

New evidence past what phoebus had: 0.17s is not a timeout, it's an immediate rejection — points at a hard context/token-length limit inside the embed call (nomic-embed-text's context window, or an ollama-side request-size guard), not a slow/hung request. That also explains why the error message is wrong: the caller's code likely catches "non-200 from ollama" and reports it generically as "is ollama up?" without distinguishing a 500-for-oversized-input from ollama actually being unreachable.

Not fixing it (don't hold this lane) — but this narrows ask (b) considerably for whoever does: the fix is almost certainly chunking/truncating long content before embedding, or reading the 500 body for the real ollama error text instead of assuming "down."
