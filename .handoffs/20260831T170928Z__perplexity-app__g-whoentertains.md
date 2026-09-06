# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: Temporal Model Spec v1.0 — six clocks, precision + provenance per date, coverage v2 / window v2, and the era-restamp parser plan
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T17:09:28.802Z

---
## Situation

GM asked to expand how coverage sees times and dates and to populate origin/creation dates correctly. Spec written: `nougen-temporal-model-spec.md` v1.0, from lane `perplexity-app`, all claims sourced to live rows or existing shards (provenance table in the appendix).

**Core diagnosis: the grid has one clock doing four jobs.** `timestamp` is set at write time, so for anything migrated, ingested or backfilled it records when the ROW was created, not when the thing happened. Every temporal read path bins on that field. Hence a span of 2010-05-08 -> 2026-08-31 while ~98.5% of the mass (63,100 of 64,039) sits in 2025-11..2026-08 — the eight months the migrations ran.

`shards_capture` already accepts `event_time`, so the design intent exists. Nothing populates it retroactively and no read path is guaranteed to bin on it.

## Evidence (all live, 2026-08-31)

Origin dates are sitting in plain text in title strings, machine-parseable today, read by nothing:

| id | db | title | timestamp | delta |
|---|---|---|---|---|
| 4066 | 7 | `Vision Shard: 2026-04-19 00:14:20` | 2026-08-17T03:00:10Z | ~120d |
| 3840 | 7 | `Vision Shard: 2026-04-18 22:26:20` | 2026-08-17T02:56:22Z | ~121d |
| 2836 | 7 | `Vision Shard: 2026-04-18 21:18:52` | 2026-08-17T02:37:07Z | ~121d |
| 16 | 5 | `Vision Shard: 2026-04-18 21:17:28` | 2026-08-03T00:00:00Z | ~107d |
| 23 | 2 | `Vision Shard: 2026-04-18 20:46:24` | 2026-08-03T00:00:00Z | ~107d |

Ids 16 and 23 carry exactly `T00:00:00Z` in two different DBs — a synthesized default, currently indistinguishable from a real midnight write. Also found origin dates in body prose: 3494 (`date_added: "2026-02-27"`), 16725 (`Ingested: 2026-02-25`).

`undated: 0` is true and misleading. Nothing is undated because every row gets a write clock; almost nothing is correctly dated.

## The model — six clocks, separated

- `captured_at` — server-assigned, immutable, never editable. THE AUDIT TRAIL. Restamping must never touch it.
- `event_time` — when the described thing happened (exists today, unpopulated)
- `origin_created_at` — artifact authored (EXIF, ctime, front matter)
- `ingested_at` — entered ANY NouGen vault; survives migration
- `source_published_at` — external publish date (video upload, paper, article)
- `valid_from` / `valid_until` — when the ASSERTION is believed true

`valid_until` is the one that fixes the stale-decision problem shard 195 documents — a "Verified" assessment outliving its evidence by eighteen minutes and being recited as current by a later lane. A closed validity interval lets recall down-rank it instead of trusting every reader to notice the amend.

Plus two things that matter as much as the columns:

- **`precision` per date** (second/minute/hour/day/month/quarter/year). Never store `2026-04` as `2026-04-01T00:00:00Z`. Fabricated zeros are indistinguishable from observed zeros — that IS the bug in rows 16/23.
- **`date_source` + `date_status`** (`exact` / `inferred` / `placeholder` / `unknown`). Placeholders excluded from span and histograms by default, counted separately. `unknown` is first-class — an honest null beats a confident midnight.

`effective_time` is materialized on write from the precedence event_time -> source_published_at -> origin_created_at -> ingested_at -> captured_at, with `effective_time_axis` recording which one won, so a reader can see whether a shard is dated by evidence or by fallback.

## Restamp plan

Seven parsers in confidence order: P1 vision-title regex (highest confidence, largest yield, cleanest pattern), P2 intelligence-shard titles, P3 YAML front matter, P4 `Ingested:` prose, P5 source metadata, P6 migration-batch carry-forward, P7 midnight-sniff — which does NOT invent a date, it flags a lie as a lie.

Protocol, per the constitution note in shard 506 (dry-run per source before write-mode):

1. Dry-run every parser per DB, report only, zero writes
2. Eyeball 20 random matches per parser — 99% right on 30k rows still means 300 confidently wrong dates
3. Write in a transaction, ONE parser, ONE DB at a time — fanning across nine loses attribution on a bad restamp
4. Never overwrite `captured_at`
5. Tag every restamped row `restamped:<parser>:<date>` — append-only applies to metadata too
6. Publish the reconciliation report as a shard, with the before/after month histogram

**The 2010-05 cluster: DO NOT RESTAMP YET.** 698 rows, sixteen years before the next live month, 178 empty months either side. Investigate first — all one db_index? one origin_file? Is 2010-05-08 a constant across all 698 (means a default was written) or spread across the month (means something genuinely dated them, and the question is what)? Output is a recorded decision, not a silent bulk update.

## coverage v2

New args: `axis` (effective/captured/event/origin/ingested), `include` (status filter), `granularity`.

Required output additions:
- per-axis span side by side — today's single span silently means "captured"
- precision histogram — the honest measure of how well-dated the grid is
- status histogram, placeholders named and excluded from span
- **`federation_in_scope: true|false` + `stores_expected`** — a `0` meaning "not mounted on this path" must not render identically to a `0` meaning "empty." Most misleading field on the failover lane today (leg 20260831T163842Z)
- **per-DB date ranges** `{db_index, min, max, count}` for all nine — this alone would have exposed the window defect immediately
- gap CLASSIFICATION: `gap_interior` (real, alert) / `gap_sparse` (expected) / `outside_lived_span` (suppress). The current flat list of ~178 months from 2010-2025 collapses to a handful of interesting ones and becomes actionable

Note what this does to the headline: an `effective` span of 2025-11 -> 2026-08 is a TRUTHFUL description of this grid. The 2010-2025 span was an artifact of one mis-dated cluster.

## window v2

`shards_window(query?, since, until, axis='effective', limit, fields='summary'|'full', include_status)`

1. Fan out to all nine DBs and merge BEFORE truncating (currently returns only db 2 for an August window while 08-31 rows sit in db 9)
2. Global newest-first, not per-partition
3. Precision-aware bounds — a month-precision shard must match `since=2026-04`; compare at the coarser precision
4. `fields='summary'` DEFAULT — one `since=2026-08 until=2026-08 limit=10` call currently blows past 25,000 chars and truncates mid-record
5. Honest empty result: `0 rows in range; 9/9 DBs queried; federation not in scope; axis=effective` — replace `that era may live on another node`, which offers an excuse in place of a diagnosis and is factually wrong on this node

## capture v2 (additive, non-breaking)

Add `event_time_precision`, `origin_created_at`, `source_published_at`, `valid_from`, `valid_until`, `date_source`. Two rules: **shape implies precision** (`2026-04` -> month, never pad, never promote), and **refuse a future `event_time`** past clock-skew tolerance or mark it `unknown` — a future event time is almost always a parse error.

Lane rule for the integration guide: any shard describing something that already happened MUST pass `event_time`. Its absence is a defect in the capture, not a default.

## Acceptance tests (10, all falsifiable)

1. `shards_window since=2026-08-31 until=2026-08-31` returns 14010 and 141
2. August window returns db 9 rows, 08-31 ahead of 08-17
3. Shard 4066 -> `effective_time 2026-04-19T00:14:20`, axis `event_time`, source `parsed_title`, status `inferred`, `captured_at` UNCHANGED
4. Rows 16 and 23 -> `date_status placeholder`, excluded from default span
5. `coverage axis=effective` span starts at the first dense month; 2010-05 counted separately
6. `federation_in_scope: false` distinguishable from `stores: 0`
7. A month-precision shard returns from a `since=2026-04 until=2026-04` window
8. `fields=summary limit=10` returns under 4,000 chars
9. `2026-04` round-trips as `precision=month`, never rendered as `2026-04-01T00:00:00Z`
10. Per-DB date ranges visible for all nine

## Sequencing

1. Read-path honesty first — coverage v2 reporting (additive, no writes, makes everything after it measurable)
2. Fix window's DB fan-out — independent of schema work, currently the most dangerous defect because it manufactures confident absences
3. Schema delta, columns nullable, `effective_time` defaults to `captured_at` so nothing regresses
4. Parsers in dry-run, P1 first
5. Restamp per DB per parser, reconciliation report as a shard
6. Investigate 2010-05, record the decision
7. THEN resume the widened ingestion from shard 506's GM order — with `event_time` mandatory, so this backlog never rebuilds

Step 7 is the whole point. Every batch ingested before the write path requires `event_time` is another cohort someone restamps later.

## Ask

A blade-side implementer to take steps 1 and 2 (both additive/read-path, no schema risk) and report the per-DB date ranges back as an amend to this leg. That output is the measurement everything else is judged against.

## Done when

- All 10 acceptance tests pass
- Reconciliation report published as a shard with before/after histograms
- 2010-05 decision recorded
- `event_time` mandatory on the capture path for past-tense shards
