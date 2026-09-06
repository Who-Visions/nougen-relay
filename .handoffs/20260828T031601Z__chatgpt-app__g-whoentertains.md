# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement top 1% temporal provenance architecture for Griot and shards
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T03:16:01.043Z

---
## Mission
Upgrade NouGen temporal memory from single timestamps into a provenance aware temporal evidence system that can reconstruct what happened, when it happened, when NouGen learned it, which artifact or agent supplied the date, whether AI touched it later, and how confident the archive should be.

This relay is grounded in current best practices from SQL bitemporal modeling, W3C PROV, RFC 3339, EDTF / ISO 8601 uncertainty, Adobe XMP, EXIF/media metadata, C2PA action provenance, OpenLineage event/run lineage, event sourcing, and temporal knowledge graph research.

## Core doctrine
Griot is the archival time authority. He must prefer withholding over false chronology. Temporal claims become admissible only when supported by explicit evidence with source, precision, timezone semantics, and confidence.

Never collapse chronology into one field called `timestamp`.

A shard needs at minimum two orthogonal temporal dimensions:

1. `valid_time`: when the fact/event/artifact state was true in the modeled world.
2. `system_time`: when NouGen learned, stored, or asserted that fact.

Use half open intervals `[start,end)` internally where possible, matching standard temporal database practice, because adjacent states compose without overlap ambiguity.

## Add a temporal evidence model
Represent every candidate time as an evidence record rather than overwriting prior dates.

Suggested shape:

```python
@dataclass(frozen=True)
class TemporalEvidence:
    evidence_id: str
    shard_id: int | None
    semantic_role: str
    # event_time, file_created, file_modified, captured, published,
    # metadata_changed, ai_first_touch, ai_last_touch,
    # ingested, migrated, amended, retracted, observed, exported, etc.

    start_utc: datetime | None
    end_utc: datetime | None
    local_value: str | None
    timezone_name: str | None
    utc_offset: str | None

    precision: str
    # second, minute, hour, day, month, year, interval, unknown

    certainty: str
    # exact, derived, approximate, uncertain, inferred, unknown

    confidence: float
    authority_rank: int

    source_kind: str
    # exif, xmp, filesystem, git, provider_api, chat_log, connector,
    # email_header, calendar, photo_metadata, c2pa, manual_claim,
    # migration_manifest, ai_agent, database, etc.

    source_uri: str | None
    source_field: str | None
    source_hash: str | None
    extractor: str | None
    extractor_version: str | None
    observed_at_utc: datetime
    actor_id: str | None
    immutable: bool = False
```

Do not delete conflicting evidence. Keep all candidates and resolve them at query time. Griot must be able to say why a date won.

## Required shard temporal fields
Existing `timestamp` remains for compatibility but becomes a projection, not source of truth.

Add or derive:

```json
{
  "valid_time": {
    "start": null,
    "end": null,
    "precision": "day",
    "certainty": "exact",
    "confidence": 0.98
  },
  "system_time": {
    "recorded_at": null,
    "version_start": null,
    "version_end": null
  },
  "temporal": {
    "event_time": null,
    "capture_time": null,
    "file_created_time": null,
    "file_modified_time": null,
    "resource_create_time": null,
    "resource_modify_time": null,
    "metadata_time": null,
    "published_time": null,
    "ingested_time": null,
    "migrated_time": null,
    "ai_first_touch_time": null,
    "ai_last_touch_time": null,
    "last_human_touch_time": null,
    "amended_times": [],
    "retracted_time": null,
    "timezone": null,
    "precision": null,
    "confidence": null,
    "authority": null
  },
  "temporal_evidence_ids": []
}
```

## Filesystem timestamps are evidence, never truth by themselves
Capture all available OS values:

* birth / creation time when filesystem supports it
* modification time
* metadata change time if available
* access time only as weak evidence

Filesystem creation time must rank below embedded resource creation metadata because copying files can rewrite filesystem creation dates. Adobe XMP explicitly distinguishes `xmp:CreateDate` from filesystem creation time.

Track source filesystem and inode/file identity where available so copy operations can be detected.

## Media metadata priority
For images/video/audio, extract and preserve all relevant embedded times rather than selecting one:

1. EXIF DateTimeOriginal or equivalent capture time
2. EXIF CreateDate / media creation time
3. XMP CreateDate
4. QuickTime / container creation timestamps
5. XMP ModifyDate
6. XMP MetadataDate
7. filesystem modified time
8. filesystem creation time

BUT priority is context dependent. `DateTimeOriginal` answers when a photo was captured. `ModifyDate` answers when the resource changed. They are different claims and must never overwrite each other.

Preserve original timezone offset tags. If timezone is absent, mark local time as timezone unknown rather than silently assuming UTC.

## C2PA and AI touch chronology
If a C2PA manifest exists, parse actions as first class temporal events:

* created
* opened
* edited
* placed
* generated
* exported
* transformed
* AI generated or trained algorithmic media source type

Link each action to actor/tool/model and parent asset when available.

For NouGen AI interactions, create action records such as:

```json
{
  "action": "ai_touched",
  "agent": "chatgpt-app",
  "model": "gpt-5.6-sol",
  "operation": "summarize|edit|classify|caption|transform|reason|ingest",
  "input_hash": "...",
  "output_hash": "...",
  "started_at": "...",
  "completed_at": "...",
  "run_id": "uuidv7"
}
```

First AI touch and last AI touch should be projections over the append only action log, not mutable fields manually maintained.

## Provenance graph
Model lineage using W3C PROV concepts:

* Entity: file, shard, message, photo, document, model output, dataset
* Activity: capture, edit, ingest, migrate, AI transform, amendment, export
* Agent: human, ChatGPT, Claude, Gemini, Rhea, Dav1d, script, camera, application

Essential edges:

* wasGeneratedBy
* used
* wasDerivedFrom
* wasAttributedTo
* wasAssociatedWith
* wasInvalidatedBy

This lets Griot distinguish:

`original photo captured May 4` -> `edited May 7` -> `AI captioned July 2` -> `ingested July 5` -> `shard amended August 27`

without pretending all five operations happened on the same date.

## System time must be immutable / append only
Every shard mutation creates a new system version rather than rewriting history invisibly.

Suggested storage:

```sql
CREATE TABLE shard_versions (
  shard_pk TEXT NOT NULL,
  version_id TEXT PRIMARY KEY,
  valid_start TEXT,
  valid_end TEXT,
  system_start TEXT NOT NULL,
  system_end TEXT,
  payload_hash TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  actor TEXT,
  operation TEXT NOT NULL
);
```

Current row has `system_end IS NULL`. On amendment/retraction, close previous version and append a new one.

Do not erase temporal corrections. A corrected date must preserve the former assertion and the reason it lost authority.

## Uncertain and approximate dates
Support EDTF semantics or an equivalent internal representation.

Examples:

* exact day: `2026-05-14`
* month precision: `2026-05`
* approximate: `2026-05~`
* uncertain: `2026-05?`
* uncertain and approximate: `2026-05%`
* unspecified day: `2026-05-XX`
* interval: `2026-05-04/2026-05-07`

Never convert month precision into midnight on the first day and then pretend that instant is exact.

A stored `2026-05` should query as the interval `[2026-05-01T00:00, 2026-06-01T00:00)` with precision=`month`, not as May 1.

## Timezone rules
Canonical storage uses UTC for known instants plus original local representation.

Store:

* normalized UTC instant if resolvable
* original local datetime
* IANA zone if known
* numeric offset if known
* `offset_unknown=true` when appropriate

Do not infer timezone from the current user location for historical artifacts unless another source proves it.

If only a numeric offset is known, preserve that and do not fabricate an IANA timezone.

## Authority ranking
Temporal evidence resolution should be semantic role aware.

Suggested base ranks, tune empirically:

100: cryptographically signed provenance / trusted provider event record / authoritative API
95: camera EXIF DateTimeOriginal with timezone or C2PA capture action
90: source application XMP CreateDate / provider original-created timestamp
85: Git commit authored/committed times when answering source history
80: signed email/calendar/server message timestamp
75: local application metadata
65: filesystem mtime
55: filesystem birth/create time
45: file naming convention with parsable date
35: textual date inside artifact
25: model inferred date from content
15: user or agent retrospective estimate without corroboration

Rank alone does not decide truth. Semantic role compatibility comes first.

Example: filesystem mtime cannot defeat EXIF DateTimeOriginal for capture time because they describe different events.

## Conflict resolution
Implement a resolver that returns both winner and evidence packet.

```python
def resolve_time(evidence, role, query_interval=None):
    candidates = [e for e in evidence if compatible(e.semantic_role, role)]
    candidates = normalize_without_destroying_original(candidates)
    candidates.sort(key=lambda e: (
        role_specific_authority(e, role),
        e.confidence,
        e.precision_score,
        source_independence_score(e),
        e.observed_at_utc,
    ), reverse=True)
    return TemporalResolution(
        chosen=candidates[0] if candidates else None,
        corroborating=..., conflicting=..., explanation=...
    )
```

Corroboration from independent sources should raise confidence. Ten copied metadata fields from the same upstream source count as one lineage family, not ten votes.

## Temporal admissibility for Griot
Griot bounded queries should operate on resolved `valid_time`, not `system_time` or generic shard timestamps.

For query `since=2026-05 until=2026-05`:

1. Resolve valid interval for each candidate memory.
2. Include only if its admissible valid interval intersects May.
3. If only ingestion/migration time is May but event time is unknown, do not present it as a May event.
4. If event date is approximate but still provably overlaps May, present it with uncertainty.
5. If date cannot be proven, hold back and report held_back count.
6. Return provenance summary with each result: chosen temporal role, precision, confidence, evidence source.

Suggested response metadata:

```json
{
  "temporal_resolution": {
    "role": "event_time",
    "start": "2026-05-14T18:22:04Z",
    "end": "2026-05-14T18:22:05Z",
    "precision": "second",
    "confidence": 0.99,
    "authority": "exif_datetime_original",
    "evidence_count": 3,
    "conflict_count": 1
  }
}
```

## Query language improvements
Extend `shards_window` with optional dimensions:

```python
shards_window(
    since="2026-05",
    until="2026-05",
    time_axis="valid",       # valid | system | capture | modified | ai_touch | any
    precision_min="day",
    confidence_min=0.70,
    include_uncertain=True,
    include_provenance=False,
)
```

Default remains `time_axis=valid` for historical questions.

Examples:

* What happened in May? -> valid/event time
* What did NouGen learn in May? -> system/ingestion time
* Which files were modified in May? -> resource modification time
* What did AI touch in May? -> AI activity time
* What photos were actually captured in May? -> capture time

This distinction is critical.

## Temporal index
Do not force semantic vector search to solve chronology.

Create dedicated indexes, e.g. SQLite:

```sql
CREATE INDEX idx_temporal_role_start
ON temporal_evidence(semantic_role, start_utc);

CREATE INDEX idx_temporal_role_end
ON temporal_evidence(semantic_role, end_utc);

CREATE INDEX idx_shard_valid
ON shard_temporal_projection(valid_start, valid_end);

CREATE INDEX idx_shard_system
ON shard_versions(system_start, system_end);
```

For millions of shards, consider RTree / interval index or backend native range indexes.

Filter by time FIRST, semantic rank SECOND. That is what prevented August density from burying May.

## Ingestion adapters
Every importer must emit temporal evidence before content embedding.

Adapters should include:

* filesystem files
* images and video
* PDFs / office documents
* Git repositories
* Notion
* Gmail / messages
* Calendar
* ChatGPT / Claude / Gemini transcripts
* NouGen relay legs
* tracker data
* research/arXiv docs
* C2PA manifests
* browser captures

Each adapter owns source-specific parsing, but writes one normalized evidence contract.

## Original file creation / modification requirement
For every filesystem artifact ingested, preserve both raw values and source platform semantics. Do not write a universal `created_at` without naming where it came from.

Example:

```json
{
  "source_kind": "filesystem",
  "platform": "windows_ntfs",
  "file_birth_time": "...",
  "file_mtime": "...",
  "file_ctime_semantics": "metadata_change_or_platform_specific",
  "observed_at": "..."
}
```

On migration or copying, generate a new observation, do not overwrite original evidence.

## AI touched dates
Maintain append only `provenance_actions` with run IDs, model identifiers, prompt/input hashes where privacy policy allows, operation type, output hash, and timestamps.

AI touch MUST NOT mutate original file creation date.

If ChatGPT edits a 2018 photo in 2026:

* capture_time remains 2018
* resource version created by AI may be 2026
* AI activity time is 2026
* NouGen system ingestion might be another date

This separation is mandatory.

## Migration strategy for existing shards
Do not rewrite the entire archive with guessed dates.

Pass 1: schema migration only, preserve old timestamp as `legacy_timestamp`.

Pass 2: deterministic backfill from authoritative metadata.

Pass 3: source adapters rescan artifacts where available.

Pass 4: infer low confidence dates only when useful, explicitly marked inferred.

Pass 5: Griot temporal audit compares legacy timestamp against new valid time and flags suspicious collapses such as every migrated document at `00:00:00Z`.

Backfill rules must be idempotent and provenance preserving.

## Temporal anomaly detector
Create warnings for:

* file modified before file created
* AI touched before source existed
* ingestion before source creation
* timezone conversion shifts date unexpectedly
* all records in a batch pinned to midnight
* dates equal to migration date across unrelated historical artifacts
* future timestamp beyond allowed clock skew
* duplicated timestamp across thousands of unrelated files
* low confidence inference overriding high authority source
* EXIF and filesystem times diverging by suspicious copy interval

Do not auto-correct anomalies silently. Capture them as temporal conflicts.

## Clock skew
For machine produced live events, record producer clock and receiver observation time when feasible.

```json
{
  "producer_time": "...",
  "receiver_time": "...",
  "estimated_skew_ms": 428,
  "clock_source": "system|ntp|unknown"
}
```

Use receiver time as a sanity bound, not as replacement for producer event time.

## OpenLineage inspired run lineage
Give ingestion, migration, AI processing, and archival repair jobs unique UUIDv7 run IDs. Each run should record START, COMPLETE, FAIL, or ABORT events and inputs/outputs. That provides explainability for bulk temporal rewrites.

## Content hashing
Temporal provenance should bind evidence to artifact identity:

* SHA-256 content hash
* source URI/path
* stable provider ID where available
* parent hash for derived artifacts

A file with same name but different hash is a new version/entity, not silently the same object.

## Suggested tables

```sql
CREATE TABLE temporal_evidence (
  evidence_id TEXT PRIMARY KEY,
  shard_pk TEXT,
  semantic_role TEXT NOT NULL,
  start_utc TEXT,
  end_utc TEXT,
  local_value TEXT,
  timezone_name TEXT,
  utc_offset TEXT,
  precision TEXT NOT NULL,
  certainty TEXT NOT NULL,
  confidence REAL NOT NULL,
  authority_rank INTEGER NOT NULL,
  source_kind TEXT NOT NULL,
  source_uri TEXT,
  source_field TEXT,
  source_hash TEXT,
  extractor TEXT,
  extractor_version TEXT,
  actor_id TEXT,
  observed_at_utc TEXT NOT NULL,
  immutable INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE provenance_actions (
  action_id TEXT PRIMARY KEY,
  run_id TEXT,
  action_type TEXT NOT NULL,
  actor_id TEXT,
  tool_id TEXT,
  model_id TEXT,
  input_entity_id TEXT,
  output_entity_id TEXT,
  started_at_utc TEXT,
  ended_at_utc TEXT,
  details_json TEXT
);

CREATE TABLE provenance_edges (
  edge_id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_id TEXT NOT NULL,
  activity_id TEXT,
  observed_at_utc TEXT NOT NULL
);
```

## Griot API behavior
Griot should return evidence grade along with memories.

Potential grades:

A: direct authoritative timestamp, high precision
B: corroborated strong metadata
C: single reasonable metadata source
D: inferred or approximate, usable with caveat
F: inadmissible for bounded historical claims

When asked `What was Dave doing in May 2026?`, Griot should include A through C by default, optionally D when explicitly requested, and hold F.

## Explainability
Add `why_this_date` to debug/diagnostic output.

Example:

`2026-05-17 selected as event date because EXIF DateTimeOriginal and XMP CreateDate agree within 1 second; filesystem creation is 2026-07-05 and is classified as later copy/ingestion evidence.`

That sentence is worth more than a mysterious confidence score.

## Tests
Create fixtures covering:

1. photo captured May, copied July, ingested August
2. document created May, edited June, AI summarized August
3. file with only mtime
4. file whose timezone is unknown
5. approximate month only
6. conflicting EXIF and XMP
7. batch migration where all files got midnight timestamp
8. Git authored time differs from commit time
9. C2PA source plus AI transformation
10. later shard amendment correcting event date
11. retracted incorrect date preserved in system history
12. source with clock skew
13. duplicate filenames with different hashes
14. same artifact copied across machines
15. personal memory captured months later but describing a dated event

## Acceptance tests
The upgrade is done when all of these hold:

A. `shards_window(since="2026-05", until="2026-05")` can retrieve lived May history using valid time even if shards were ingested in July/August.

B. `time_axis="system"` returns what NouGen actually learned/stored in May, which may be a completely different set.

C. A photo copied in July still appears in a May capture query if EXIF proves May capture.

D. A July migration timestamp never overwrites an original May date.

E. Griot can explain each admitted date and name its provenance source.

F. Ambiguous undated memories remain held back instead of being hallucinated into the requested month.

G. AI touch history is queryable independently from original creation/capture history.

H. Corrections are append only and `AS OF` style historical reconstruction is possible: what did NouGen believe on date X versus what does it believe now?

I. Backfill is idempotent, resumable, and never destroys original timestamp evidence.

J. A temporal audit on existing May 2026 shards identifies migration bucket timestamps and distinguishes them from genuine event timestamps.

## Priority order
P0: schema + evidence contract + Griot valid/system separation
P0: deterministic backfill of existing metadata
P0: never overwrite original evidence
P1: media EXIF/XMP/C2PA adapter
P1: AI provenance action log
P1: temporal anomaly detector
P1: Griot explainable temporal grades
P2: advanced interval indexing / temporal KG reasoning
P2: independent-source corroboration scoring
P2: clock skew estimation

## Architectural invariant
NouGen must be able to answer four different questions without conflating them:

1. When did this happen?
2. When was this artifact created or changed?
3. When did an AI or human touch it?
4. When did NouGen learn it?

If one `timestamp` answers all four, the implementation is wrong.

Done when Griot can reconstruct historical chronology from provenance evidence with explicit precision and confidence, and a May 2026 bounded query can surface genuine lived history without leaking later migration/ingestion dates into the event timeline.
