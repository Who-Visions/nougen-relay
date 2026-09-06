# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix April temporal recall and make shard archaeology observable
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T08:42:47.142Z

---
## Context
Deep April 2026 archaeology exposed a contradiction that should become a regression fixture.

Observed from the ChatGPT connector lane:

1. `shards_window(since=2026-04, until=2026-04, limit=50)` timed out.
2. Bounded `ask_griot` for April reported `total=12`, `shown=0`, `held_back=12`, meaning 12 candidate memories existed but none could be proven inside the requested era.
3. Subsequent keyword searches for `April 2026`, `2026-04`, and `Apr 2026` reached the gateway but returned gateway metadata with no hit payload.
4. Semantic recall attempts likewise reached the gateway but exposed no hit payload.
5. An unbounded Griot deep grep for April variants returned 0 candidates.

The dangerous failure mode is not simply an empty month. Different retrieval arms disagree about whether candidate evidence exists.

## Wishlist

### 1. First class temporal provenance
Every shard should preserve separate fields for `event_at`, `created_at`, `modified_at`, `ingested_at`, `source_created_at`, `source_modified_at`, and `ai_touched_at` where available. Never collapse these into one timestamp. Store timezone and provenance for each timestamp.

### 2. Temporal confidence
Add a machine readable `event_time_confidence` and `event_time_basis`, for example explicit source timestamp, filename timestamp, filesystem metadata, conversation timestamp, inferred from surrounding records, or unknown. Bounded queries can then return uncertain candidates rather than silently hiding them.

### 3. Explain held back candidates
When Griot says `held_back=12`, return safe diagnostic descriptors for those 12: store, id, title, candidate era, reason held back, timestamp fields present, and timestamp fields missing. The caller needs to inspect the evidence without falsely promoting it to verified history.

### 4. Candidate mode
Add `include_unverified=true` or an archaeology mode to bounded temporal retrieval. Verified results remain distinct from candidates. Never force the storyteller to choose between false certainty and total blindness.

### 5. Search arm parity
Keyword search, semantic recall, temporal window, and Griot should expose which stores were queried, which responded, hit counts per store, filtered counts, timeout counts, and serialization errors. A successful HTTP/gateway response with zero result payload must not masquerade as a legitimate zero hit search.

### 6. Partial result streaming
`shards_window` should return whatever it has before a slow DB causes the entire operation to timeout. Include `partial=true`, stores completed, stores pending/failed, elapsed time, and continuation cursor.

### 7. Pagination and cursors
Large month scans need deterministic paging by event time plus stable tie breaker, not one giant blocking query. April should be retrievable page by page even if the grid contains millions of shards.

### 8. Coverage fast path
`shards_coverage` timed out too. Maintain a lightweight materialized coverage ledger with counts per DB, month, timestamp type, verified temporal records, uncertain records, and undated records. Coverage should be cheap enough to call before every historical investigation.

### 9. Undated quarantine index
Do not lose shards merely because event dates are unknown. Maintain an `undated` or `temporal_unresolved` index searchable by content, source filename, filesystem dates, neighboring records, entities, projects, and ingestion batch.

### 10. Temporal repair pipeline
Build a repair worker that attempts to recover missing event dates from source metadata, Git history, EXIF, filesystem timestamps, chat exports, filenames, adjacent records, commit dates, document internals, and known ingestion manifests. Preserve both original evidence and inferred repair. Never overwrite provenance.

### 11. Neighbor inference
For unresolved records, expose chronological neighbors from the same source/import batch. If shard A is proven April 4 and shard C April 6, an undated B between them can be surfaced as a candidate with an explicit inference basis rather than disappearing.

### 12. Ingestion manifests
Every bulk ingestion should produce a manifest recording source path/hash, source date range, records discovered, records written, duplicates, failures, timestamp extraction success, unresolved timestamps, and shard IDs created. This gives us a forensic trail when an era vanishes later.

### 13. Search diagnostics endpoint/tool
Give agents a `shards_explain` or equivalent diagnostic call: query plan, stores touched, candidate counts, ranking/filter stages, rejected IDs/reasons, latency by stage, and whether the final zero means true zero, filtered zero, timeout zero, or backend visibility zero.

### 14. Regression fixture for April 2026
Capture this exact contradiction as a test. A bounded Griot gather must never claim 12 candidates while all other retrieval surfaces provide no way to inspect those candidates. Test across every federated store and connector lane.

### 15. Truth states in the API
Standardize response state: `verified_hit`, `candidate_hit`, `true_zero`, `partial_zero`, `filtered_zero`, `timeout`, `backend_unavailable`, `index_unavailable`, `serialization_failure`. A bare empty array is epistemically insufficient.

### 16. Historical reconstruction mode
Long term, Griot should be able to reconstruct a month using multiple evidence classes: verified dated shards first, candidate shards second, source artifacts third, neighboring chronology fourth. Output should clearly separate facts from inference and unresolved gaps.

## Done when
A query for April 2026 can reliably answer all of these without ambiguity:

* How many shards are definitively dated to April?
* How many are plausible April candidates?
* Why is each candidate uncertain?
* Which stores were actually searched?
* Which stores timed out or failed?
* Can every candidate be inspected by ID?
* Can the month be paged without a global timeout?
* Can an agent distinguish `nothing happened` from `we cannot currently see what happened`?

Core principle: **absence of retrievable evidence must never be represented as evidence of absence when the federation is partial, filtered, unresolved, or timed out.**
