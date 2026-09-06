# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix Shards federation truth fragmentation and false-empty recall
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:53:41.038Z

---
Observed live from ChatGPT connector on 2026-08-29. This is a memory correctness defect, separate from the tracker aggregation leg already active.

EVIDENCE
1. Earlier, another NouGen connector surface successfully returned shard id 22388 titled `Usage window Sat 2026-08-22 -> Fri 2026-08-28 blade1tb...` containing a 1.166B blended token snapshot (734M exact + 432M estimated).
2. On the current NouGenShards surface, `shards_search` for Saturday/token/1.5B/1.166B returned `(no matches)`.
3. `shards_recall` for the same known evidence returned `(no recall results)`.
4. `ask_griot` bounded 2026-08-22 through 2026-08-29 returned shown=0,total=0,held_back=0,failures=[] despite that known shard existing on another connector surface.
5. Separately, tracker_spend on this surface reports 994,889,354 total_activity and complete=true while richer archived tracker evidence reports at least 1.166B blended tokens. This shows both retrieval federation and accounting semantics can diverge by surface.

CORE FAILURE
A negative recall currently cannot be interpreted as `memory does not exist`. The fleet can possess a fact while a provider/lane sees an empty archive. That breaks the central invariant of NouGenShards: one recoverable memory substrate across agents/providers.

FIX REQUIREMENTS
* Establish a canonical federated shard manifest/version visible to every connector lane. Expose node/store/db membership and index generation/version in status/coverage responses.
* Make `shards_coverage` report which DBs/stores are mounted, expected vs reachable shard counts, last sync/index timestamp, stale/partial mounts, and federation generation.
* Never return an unqualified empty result when coverage is incomplete or stale. Return explicit `partial`, `coverage_gap`, `stores_unreachable`, or equivalent metadata.
* Make search/recall/Griot share the same federation membership contract. If Griot searches fewer stores than direct recall, disclose it.
* Add cross-lane parity tests: insert/capture a sentinel shard, then require retrieval by exact search, semantic recall, bounded window, and Griot through every provider connector lane.
* Add known-id diagnostic lookup or equivalent deterministic probe so fuzzy retrieval is not the only way to prove existence.
* Add index reconciliation/self-healing when a DB contains a row absent from keyword/vector indexes.
* Treat `complete=true` as query-execution completeness only unless global dataset completeness is proven. Prefer separate fields such as query_complete and federation_complete.
* Instrument misses: query fingerprint, lane, mounted DB set, index generation, stores queried, stores skipped, and reason.
* Regression case must include shard 22388 or an equivalent fixture where one connector previously found the record and another returned empty.

DONE WHEN
The same known shard is discoverable through all connector/provider lanes with search, recall, window/Griot where applicable; false-empty responses are impossible without an explicit coverage warning; and operators can distinguish `no matching memory` from `this lane did not search the full memory universe`.
