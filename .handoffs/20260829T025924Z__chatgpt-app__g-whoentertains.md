# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix temporal truth bug: generated build artifacts can inject impossible historical dates into shard coverage
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T02:59:24.073Z

---
# Temporal Truth Bug: CMake build artifact falsely backfilled NouGen history to 2001

## Finding
A new shard appeared under January 2001 during the current source-grounded file pass:

Title: `Iris AI Repo — frontend_flutter\\build\\windows\\x64\\CMakeFiles\\3bb6b98838184ca19d906f258929757a\\INSTALL_force.rule`
Content: `# generated from CMake`
Source path: `C:\\Users\\super\\Watchtower\\Iris-ai-repo\\frontend_flutter\\build\\windows\\x64\\CMakeFiles\\3bb6b98838184ca19d906f258929757a\\INSTALL_force.rule`
Recorded source_created_at: `2001-01-01T00:00:00Z`
Recorded source_modified_at: `2001-01-01T00:00:00Z`
Captured_at: `2026-08-29T01:53:44.796810Z`
Event type: `WATCHTOWER_IRIS_AI_REPO`
Shard id: 24484
DB index: 5

This file is a generated CMake build artifact. Its metadata timestamp was faithfully preserved, but NouGen coverage interpreted that timestamp as historical activity, pushing the grid's earliest span from 2019 back to 2001.

## Root problem
SOURCE TIMESTAMP is currently able to become EVENT TIME without sufficient temporal plausibility checks.

The source metadata itself should remain immutable evidence. The interpretation of that metadata as `event_occurred_at` must be separately scored and can be rejected.

Generated artifacts are especially dangerous because toolchains, archives, dependency packages, copied filesystems, extraction utilities, virtualized environments, Git checkouts, FAT/NTFS timestamp behavior, ZIP normalization, SDKs, installers and reproducible-build machinery can preserve or synthesize sentinel/default timestamps that have nothing to do with the human activity being reconstructed.

## Required architecture fix
Do not delete or rewrite the source timestamp. Introduce a temporal evidence layer that distinguishes:

`source_created_at`
`source_modified_at`
`source_metadata_timestamp`
`event_occurred_at`
`event_time_basis`
`event_time_confidence`
`temporal_anomaly_flags`

The original `2001-01-01T00:00:00Z` metadata should remain attached to the source, but should not automatically qualify that source for January 2001 business/history coverage.

## Temporal sanity rules wishlist

### 1. Generated path detection
Strongly down-rank file timestamps as historical-event evidence when paths or metadata indicate generated/cache/build content. Examples:

`build/`
`dist/`
`.gradle/`
`.dart_tool/`
`CMakeFiles/`
`node_modules/`
`target/`
`DerivedData/`
`__pycache__/`
`.next/`
`out/`
`vendor/` where provenance is dependency-derived
SDK/toolchain/generated folders

Do not blanket discard them because generated artifacts can still prove work occurred. Instead, treat their timestamps as weak evidence unless corroborated.

### 2. Sentinel/default timestamp detection
Flag suspicious dates such as exact midnight on January 1 of an implausibly old year, DOS/ZIP epoch-like dates, Unix epoch values, 1980-01-01 style archive dates, 2000/2001 sentinel timestamps, filesystem minimums, and other known reproducible-build constants.

Avoid a brittle single-year blacklist. Detection should consider timestamp shape + file type + path + surrounding corpus.

### 3. Repository plausibility bounds
For a source inside a known repository/project, establish plausible project-life bounds using stronger signals such as earliest Git commit, repository creation evidence, surrounding source files, package metadata, conversation/project history and first known project reference.

A generated Iris AI build rule claiming 2001 is temporally incompatible with the surrounding project corpus and should be flagged.

### 4. Neighborhood consensus
Compare timestamps to sibling and parent artifacts. If one generated file claims 2001 while thousands of related project files cluster in 2026, classify the 2001 value as an outlier rather than creating a new historical era.

### 5. File-type provenance
Generated `.rule`, lockfiles, compiler outputs, object files, binaries, cache files and vendored artifacts should not have equal temporal authority to original authored documents, photos with EXIF, signed contracts, invoices, messages, Git commits or primary source code history.

### 6. Independent corroboration before historical backfill
Creating a previously unseen year/month in shard coverage should require stronger evidence than one weak timestamp.

Possible rule: a new historical era outside the current plausible span is not promoted to canonical coverage unless at least one high-authority primary source supports it, or multiple independent medium-authority sources converge.

The shard can still exist and remain searchable under source metadata, but canonical historical coverage should distinguish `raw_source_span` from `trusted_event_span`.

### 7. Split coverage metrics
Recommend exposing at least:

`raw_source_span`: min/max timestamp found anywhere in source metadata.
`trusted_event_span`: min/max event times passing temporal provenance threshold.

Likewise monthly counts could expose raw vs trusted counts. This prevents one malformed artifact from rewriting the apparent history of the entire system.

### 8. Temporal anomaly flags
Suggested examples:

`GENERATED_ARTIFACT_TIMESTAMP`
`SENTINEL_TIMESTAMP`
`PROJECT_LIFETIME_CONFLICT`
`NEIGHBORHOOD_OUTLIER`
`ARCHIVE_TIMESTAMP`
`COPY_TIMESTAMP`
`LOW_AUTHORITY_EVENT_TIME`
`UNSUPPORTED_HISTORICAL_BACKFILL`

### 9. Preserve source truth while rejecting event inference
Desired representation for this exact CMake shard conceptually:

source_created_at = `2001-01-01T00:00:00Z`
source_modified_at = `2001-01-01T00:00:00Z`
event_occurred_at = UNKNOWN or corroborated 2026 time
event_time_basis = `GENERATED_ARTIFACT_METADATA`
event_time_confidence = LOW
temporal_anomaly_flags = [`GENERATED_ARTIFACT_TIMESTAMP`, `PROJECT_LIFETIME_CONFLICT`, `UNSUPPORTED_HISTORICAL_BACKFILL`]

This preserves what the filesystem reported without falsely claiming Dave/NouGen/Iris activity in 2001.

### 10. Existing shard remediation
Do not erase shard 24484. Amend/reclassify its temporal interpretation or regenerate derived temporal indexes so that its 2001 metadata remains provenance but does not count as trusted historical activity.

Because this system is intended for IRS/evidence use, append-only correction is preferable to silent mutation. Record that the original timestamp was observed and later classified as non-authoritative event-time evidence.

## IRS relevance
This is not cosmetic. For audit-grade reconstruction, the system must distinguish:

`the file's metadata says X`
from
`the business activity occurred at X`.

A source can be authentic while one metadata field is unsuitable for dating the underlying human event. Failing to separate those claims can create false work histories, false expense associations and misleading audit timelines.

## Tests requested
Add adversarial temporal tests covering at minimum:

1. CMake generated rule dated 2001 inside a 2026 repo.
2. ZIP/archive extracted file with 1980 epoch timestamp.
3. Git checkout where file mtime is checkout date but commit proves older authored date.
4. Copied photo where filesystem timestamp is recent but EXIF capture time is older.
5. Generated artifact with old timestamp but surrounding authored source strongly establishes current event.
6. Legitimate old primary document that really should open a new historical era.
7. Single weak artifact should not move `trusted_event_span`.
8. Multiple independent strong historical sources should move `trusted_event_span`.

## Done when
The original CMake source timestamp remains retrievable and immutable, but NouGen no longer reports January 2001 as trusted human/project activity based solely on that generated artifact. Coverage and historical synthesis must be able to distinguish raw metadata chronology from evidence-backed event chronology.
