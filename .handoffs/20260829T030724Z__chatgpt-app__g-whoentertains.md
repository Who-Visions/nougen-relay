# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix pre-2025 temporal contamination discovered in deep audit of 2001 through 2024 shard history
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T03:07:24.091Z

---
## Situation
Deep temporal audit of every populated pre-2025 era found that the current raw shard coverage is extending historical chronology using untrustworthy timestamps. Preserve all raw evidence, but do NOT let these records establish trusted activity dates without corroboration.

## Findings by era

### 2001
- One shard, id 24484, WATCHTOWER_IRIS_AI_REPO.
- Generated CMake artifact: `frontend_flutter\\build\\windows\\x64\\CMakeFiles\\...\\INSTALL_force.rule` with content `# generated from CMake`.
- Filesystem/source metadata says 2001-01-01, captured in 2026.
- This is sentinel/generated-artifact timestamp junk, not evidence Dave built Iris AI in 2001.

### 2018
- 27 nominal shards in July 2018.
- WATCHTOWER_VAULT_BACKUP_RECOVERY from `nougen_memories.db.bak-20260807`.
- Multiple unrelated children share near-identical 2018-07-29 15:19:20 timestamps.
- Content contains modern GitHub/Copilot/Spark/MCP material, Anthropic/Gemini Antigravity paths, TestingCatalog material discussing Jules V2, Google I/O 2026 and 2025/2026 agents.
- Bounded Griot provenance audit could not establish credible 2018 activity.
- Conclusion: recovered backup/container timestamp contamination.

### 2019
- One nominal May 2019 shard: `ERAFIX1787086416`, content `post-102 verification ERAFIX1787086416`.
- No temporal_meta/original_timestamp supporting historical provenance.
- Looks like synthetic era-fix verification/test data, not a real-world 2019 event.

### 2020
- No shards. Do not infer no activity; only no shard evidence on this node.

### 2021
- 53 nominal shards, November cluster.
- Same WATCHTOWER_VAULT_BACKUP_RECOVERY pattern from 2026 backup.
- Near-identical 2021-11-17 15:19:20 timestamps across unrelated records.
- Content includes task `Verify Brooklyn Comic Con 2024 Details` plus modern Gemini API docs mentioning Gemini 3, Nano Banana, Veo, Lyria 3, coding agents, Deep Research, Computer Use, etc.
- Nominal 2021 timestamps therefore cannot be event truth.

### 2022
- No shards. Again, absence of shard evidence != proof of no activity.

### 2023
- 8 nominal September shards.
- Same 2026 vault backup recovery provenance and timestamp collision around 2023-09-20 15:19:20.
- Content includes modern NouGen/Sol architecture: SolMemoryPalace, MCP/A2A mesh, fleet-sync, shard-management, gemma4 models, plus conversations explicitly targeting `Hyperion standard v2026` and `Ai with Dav3`.
- These are later artifacts wearing 2023 timestamps.

### 2024
- New ingestion has populated December 2024, but sampled records are again WATCHTOWER_VAULT_BACKUP_RECOVERY from the 2026 backup.
- Shard 25809 nominally 2024-12-04 contains code with `DATE_FILTER = September 1, 2025`, `MODEL_ID = gemini-3.1-flash-lite-preview`, and `.gemini\\antigravity` paths. It cannot represent a Dec 2024 event.
- Multiple unrelated records share near-identical 2024-12-04 15:19:20 timestamps.
- Another record contains a Medium article published Jan 25 2023, demonstrating that document publication date, retrieval date, filesystem date and user activity date are distinct dimensions.

## Root bug class
The recovery/indexing pipeline is collapsing multiple temporal concepts into `event_time_original` / effective chronology. Raw filesystem timestamps, backup/container metadata, recovered child timestamps, document publication dates, retrieval dates and actual user activity dates are not interchangeable.

## Required fix
1. Preserve raw timestamps exactly. Never erase or silently rewrite forensic metadata.
2. Introduce explicit temporal dimensions at minimum:
   - `raw_record_timestamp`
   - `source_created_at`
   - `source_modified_at`
   - `container_timestamp`
   - `recovery_timestamp`
   - `document_published_at`
   - `document_retrieved_at`
   - `embedded_event_timestamp`
   - `trusted_event_timestamp`
   - `shard_created_at`
3. Only `trusted_event_timestamp` may extend trusted historical coverage or support claims like `Dave was working in YEAR`.
4. Add `temporal_status`: VERIFIED, CORROBORATED, UNVERIFIED, ANOMALOUS, CONFLICTED, SYNTHETIC_TEST, GENERATED_ARTIFACT.
5. Add generated/build artifact detection: CMake/build/cache/temp/node_modules/generated/system-generated artifacts should default to weak event-time evidence.
6. Add sentinel timestamp detection for epoch/default/impossible/project-prehistory dates.
7. Add technology existence bounds and content chronology checks. If content names technology/events/releases that postdate the alleged event timestamp, flag TEMPORAL_ANOMALY automatically.
8. Add timestamp collision/batch anomaly detection. Many unrelated recovered child records sharing the same second/microsecond neighborhood is evidence of inherited container/recovery metadata, not independent event timing.
9. Recovered backup children must never inherit backup/container timestamps as event time by default.
10. Separate source chronology from content chronology. Publication date of an article is not retrieval/activity date.
11. Add project lifetime bounds. A file timestamp predating the known existence of its project/tool cannot establish project activity without independent corroboration.
12. Add neighborhood/outlier checks against adjacent source records, directory history, Git history, EXIF, communications, invoices, calendar, payments and other independent sources.
13. Derivative copies from the same backup/root source do not count as independent corroboration.
14. Synthetic test markers such as ERAFIX must be explicitly tagged and excluded from historical coverage.
15. Coverage/status API should expose BOTH `raw_source_span` and `trusted_event_span`, plus raw vs trusted counts per month/year.
16. Historical queries (`shards_window`, Griot, IRS evidence layer) should clearly distinguish raw timestamp matches from trusted historical events.
17. IRS evidence graph must be able to say simultaneously: `this source contains timestamp X` and `X is not credible evidence the business event occurred then`.
18. Never turn empty years into `no activity`; phrase as `no trusted evidence currently indexed`.
19. Run a migration/audit across existing shards and downgrade anomalous pre-2025 records rather than deleting them.
20. Build adversarial regression fixtures from these exact 2001, 2018, 2019, 2021, 2023 and 2024 examples.

## Done when
- Raw evidence remains immutable and searchable.
- Trusted chronology no longer starts in 2001 merely because of a generated CMake timestamp.
- 2018/2021/2023/2024 recovered backup collisions cannot pollute trusted coverage.
- ERAFIX/test artifacts cannot become historical events.
- Content anachronisms automatically quarantine alleged event dates.
- Coverage reports raw and trusted timelines separately.
- IRS/business-history queries only promote dates backed by credible temporal provenance and can walk every promoted date backward to original evidence.
