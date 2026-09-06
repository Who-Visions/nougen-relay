# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to ccr TODO 140309Z (leg 160149Z): provenance-grounded shard-to-content pipeline SHIPPED (content_engine.py + tools/shard_content.py, 6 tests); first weekly retrospective published with 5 resolvable citations and 0 uncited paragraphs on the free cloud lane; VRAM gate fixed to admit -cloud models
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T19:27:22.103Z

---
# Shard-to-content pipeline (claude-cli, blade1tb, 2026-09-02 15:27 EDT)

War-game: wargames/shard-to-content-pipeline.md. Shard: "SHIPPED 2026-09-02 15:26 EDT: provenance-grounded shard-to-content pipeline".

## What it does
gather -> outline -> draft -> fact_check -> publish in src/nougen_shards/content_engine.py, CLI tools/shard_content.py.
- Evidence ledger per era from every grid DB, using the temporal columns the grid already has (original_timestamp = era, temporal_meta.captured_at = ingest). Each row is classed contemporaneous / backfill / research.
- Citation key [shard:ID@dbN]; the draft gets only the evidence block and the allowed keys.
- Mechanical check: unknown citation = fail; every body paragraph must cite (NOUGEN_CONTENT_MAX_UNCITED, default 0). A failed check never publishes.
- Published text stamps backfills as [shard:ID@dbN, backfilled DATE] and research as [..., research: host], and ends with a Provenance table. One CONTENT shard per publish carries the cited ids. No existing shard row is ever touched.
- Kinds: retrospective, devlog, changelog, timeline, origin_story, tutorial, case_study, commentary.

## Live proof
retrospective 2026-08-24..2026-08-31: ledger 40 rows; draft gemma4:31b-cloud 2.9s; check 5 cited, 0 unknown, 0 uncited; published to <GLOBAL_DIR>/content/retrospective_2026-08-24_2026-08-31.md + CONTENT shard. Thin piece (5 of 40 rows used) but nothing invented; the gate is the product.

## Fixed on the way
vram_gate refused gemma4:31b-cloud for lacking a measured size; cloud tags (NOUGEN_CLOUD_MODEL_SUFFIXES, default -cloud) are now admitted at 0 GB. tests/test_vram_gate_cloud.py 2/2.

## GM calls
- Publish target beyond disk + shard: NouGenSite blog path or vault_put.
- Which via: labels count as fleet vs third-party (NOUGEN_CONTENT_FLEET_SOURCES).
- All uncommitted on codex/shards-capture-main with the rest of today's work.
