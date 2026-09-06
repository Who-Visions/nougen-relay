# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix temporal provenance ranking for original artifact dates using BlerdHub as regression case
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:14:01.420Z

---
## Situation
User asked when BlerdHub started. Current retrieval repeatedly surfaced Aug 28, 2026 because that is the shard ingestion time and/or later embedded session evidence, not necessarily the project's true birth.

Direct temporal query explicitly searched for original metadata fields including `created_at`, `birthtime`, `ctime`, file creation time, repo creation timestamp, first commit timestamp, first session timestamp, and first path appearance for `C:/Users/super/Watchtower/BlerdHub`. Griot returned zero evidence for original creation metadata. Direct shard search still ranked the Aug 28 ingestion-backed Agent Brain record.

## Defect
Temporal provenance is flattening or ranking ingestion time above original source time when the user asks questions such as `when did I start X?`.

We need three clocks kept distinct end to end:
1. Event time: when the human actually did the thing.
2. Artifact time: original creation time of file/repo/session/object.
3. Ingestion time: when NouGen learned or re-indexed it.

For temporal questions, retrieval should prefer the strongest original source timestamp available and only fall back to ingestion time when no earlier source-backed timestamp exists. Ingestion timestamp must never silently become the canonical birth date.

## BlerdHub regression case
Canonical entity: `BlerdHub`.
Known path: `C:/Users/super/Watchtower/BlerdHub`.
Currently retrievable evidence: Aug 28, 2026 session/task record. Treat that only as `earliest currently retrievable ingestion-backed evidence`, NOT project creation date.

## Ask
Audit the ingestion schema, temporal provenance propagation, Agent Brain/session ingestion, Griot gather, shards_search/retrieval ranking, and any normalization layer for original timestamps. Confirm whether source file metadata, git history, session metadata, or repo metadata already carries older timestamps that are currently hidden or overwritten.

Add explicit provenance fields if needed, such as `event_time`, `artifact_created_at`, `source_timestamp`, `ingested_at`, plus confidence/source type. Temporal ranking should resolve `when did I start BlerdHub?` to the oldest defensible source-backed timestamp, with provenance.

## Done when
A regression test using BlerdHub proves the system can distinguish original project evidence from Aug 28 ingestion time, returns the oldest defensible timestamp with evidence type, and does not canonize ingestion time as creation time.
