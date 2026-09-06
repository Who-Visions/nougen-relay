# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add full temporal provenance to shards so Griot can reconstruct original chronology
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:12:33.022Z

---
Finding from live temporal test on 2026-08-27: shards_window can retrieve May 2026 research docs because those records carry explicit May timestamps, but ask_griot found 12 then 20 candidate Dave/NouGen memories and held all of them back under since=2026-05/until=2026-05 because their dates could not be proven. This is correct refusal behavior, but it exposes a legacy temporal-provenance gap.

FIX DIRECTION: treat time as a provenance vector, not one timestamp. Every shard/artifact should preserve distinct fields where available:

1. event_time_original: when the real-world event/content actually occurred, authored, photographed, recorded, or first existed.
2. source_created_at: original filesystem/cloud/file creation time from source metadata.
3. source_modified_at: original source modified time.
4. source_accessed_at if useful and trustworthy.
5. captured_at: when NouGen first ingested/captured the memory.
6. ai_first_touched_at: first known time an AI lane parsed, summarized, transformed, labeled, embedded, or otherwise touched the artifact.
7. ai_last_touched_at: latest AI processing time.
8. migrated_at: when moved between Notion, shard DBs, archive stores, repos, etc.
9. amended_at[]: append-only list of later shard amendments/corrections.
10. retracted_at if applicable.
11. source_system/source_path/source_id plus provider-native timestamps when available.
12. timezone_original and timezone_normalized, preserving original offset where known and normalized UTC separately.
13. temporal_precision: exact_timestamp | minute | hour | day | month | year | inferred | unknown.
14. temporal_confidence: explicit metadata vs filename-derived vs content-derived vs AI-inferred, with confidence score or provenance label.
15. timestamp_authority: which field should answer 'when did this happen?' for different query classes. Real-world event time should outrank capture/migration time for historical recall.

FILE BACKFILL: for legacy files, harvest original file creation time, modified time, EXIF/XMP capture time for photos/video, document metadata created/modified fields, git author/commit times, Notion created_time/last_edited_time, Drive/Dropbox/provider timestamps, chat/message sent times, filesystem birthtime/mtime where available, and filenames/date headers only as lower-confidence evidence. Preserve conflicts rather than overwriting. If AI generated or rewrote a derivative, keep parent artifact timestamps plus derivative creation/touch lineage.

SCHEMA IDEA: temporal_provenance as structured JSON object with all candidate times, source, precision, confidence, and immutable history. Keep legacy shard.timestamp for compatibility but define it clearly, ideally captured_at, and add an event_time resolver for temporal queries.

QUERY BEHAVIOR: shards_window/Griot bounded history should filter primarily on resolved event_time_original when present, then authoritative source-created time, and only fall back to captured_at for memories whose event itself was the capture. Never let migrated_at or AI touch time masquerade as the historical event date. Return a temporal_evidence footer showing which field admitted the shard into the window.

AI TOUCH LINEAGE: when ChatGPT, Claude, Gemini, Rhea, Dav1d, Kaedra, Griot, or another lane touches a shard/artifact, append agent/model/lane/time/action rather than replacing prior times. This lets us answer questions such as 'when was this first created?', 'when did AI first see it?', 'when was it last changed?', 'what existed before AI touched it?', and 'what did we know as of date X?'.

BITEMPORAL / AUDIT OPTION: support valid_time (when fact was true in the world) separately from system_time (when NouGen learned/recorded it). This is important for corrections and retrospective backfills. A fact learned in August about an event in May must be queryable in May-history by valid_time while still showing that NouGen only learned it in August.

BACKFILL STRATEGY: batch legacy corpus by source type, extract timestamps, write provenance without destroying existing rows, flag conflicts for review, and mark undated memories explicitly instead of inventing dates. Prioritize personal history, Who Visions, NouGen development, chats, photos, videos, docs, and project artifacts before bulk research docs.

ACCEPTANCE TESTS:
A. ask_griot('What was Dave actually doing in May 2026?', since='2026-05', until='2026-05') should surface only memories with provable May valid/event time and explain temporal evidence.
B. A file created May 10, modified June 2, ingested Aug 27 must appear in a May creation query, June modification query, and August ingestion query depending on requested temporal dimension.
C. A May photo edited by AI in August retains EXIF capture time and separate ai_first_touched_at.
D. A retrospective shard captured in August about a May event is visible in May historical reconstruction but can also answer 'when did NouGen learn this?' as August.
E. Conflicting timestamps are preserved with provenance and confidence; no silent overwrite.
F. Existing shards_window callers remain backward compatible.

Do not fake missing dates. The current Griot hold-back behavior is valuable and must remain the safety rail while temporal provenance is expanded.
