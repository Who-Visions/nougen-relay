# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGenTube shipped: YouTube lane is standing infrastructure (commit 78bb0b0)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T00:30:20.962Z

---
## Situation
GM order "make the youtube a routine" executed per `wargames/nougentube.md`. `tools/nougentube.py` is live in the public repo at **78bb0b0** (on top of 6cff987 era-capture).

- CLI: `nougentube <url|playlist|manifest.json> [--dry-run] [--limit N] [--manifest path] [--print-config]`; deps as optional extra `[tube]` (youtube-transcript-api, yt-dlp).
- Tiered fetch -> no-LLM distill (header + chapters/lead extract + verbatim tail) -> `capture(original_timestamp=publish date)`, tags `[youtube, nougentube, <channel-slug>, tube:<id>, provenance:third_party]`.
- Rhea defects fixed and regression-tested: dry-run gates ALL writes (live proof: playlist dry-run, grid 158854 rows before/after), exact-id dedupe gate (tube:<id>, never semantic), playlists first-class. Forks: no-transcript stub, era-unknown at now.
- Live capture: shard 17591 (video p79T9P2WmTI) landed at 2026-08-05 = true publish era, confirmed via shards_window.
- Tests: 12 new, suite 560 passed / 4 skipped (test_mcp_endpoint.py excluded — pre-existing merge markers in the dirty working tree, unrelated).

## Ask
Next lane: build Dave's private channel manifest (config, not code — one entry per channel) and schedule the routine run. The public repo ships only the tool.

## Done-when
Manifest exists in private config, a scheduled run drains it, and new videos land era-stamped without manual invocation.
