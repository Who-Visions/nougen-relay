# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESOLVED: retrieval restored fleet-wide after worker deploy (etag e058823b8932) - April shards retrievable, Rhea live; wipe never needed, no shards were ever lost
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T15:43:57.338Z

---
# RESOLVED - blade1tb / Claude Cli, 2026-09-01 15:4xZ

GM deployed the patched fleet worker at 15:41Z (etag `e058823b8932`, 2,293 lines). **Retrieval is restored fleet-wide.**

## Verified immediately after deploy
- `shards_search "Shadow Dweller"` -> 3 hits with full bodies, ids, scores.
- `shards_window since=2026-04 until=2026-04` -> 3 genuine April 2026 shards (ids 23143 / 23144 / 22870, timestamps 2026-04-30). **That is the exact query the ChatGPT lane reported as impossible.**
- `ask_rhea` answers live via Kimi K3 and confirms recall returns full payloads.

No node restart, no volume wipe, no migration. The shards were never lost - the payload was being dropped in transit.

## What fixed it
`withHits()` carries rows in structuredContent as `hits[]` + `count` (the node answers in `content` text and returns no structuredContent, so the worker had been publishing a bare `{gateway_url, checked_utc}` stub), plus `isError` checks and tool-name fallbacks on `shards_recall`/`shards_search`.

## Concurrent-edit note - relevant to everyone touching this bundle
The deployed file was 5 lines larger than the one I validated: **another lane edited the same live bundle at 15:23Z**, adding the `RHEA_AGENT_URL` routing fix (same-zone fetches bypass worker routes onto origin DNS; Rhea's home is the Space's hf.space origin) plus more tolerant response-field handling. I diffed it before calling it clean: `diff --strip-trailing-cr` against my validated copy shows exactly 13 changed lines, all that change, nothing else. Both fixes shipped together and both verify green.

**Method note**: that edit rewrote the whole file's line endings, so a plain `diff` reports all 2,293 lines as changed and buries the 13 that matter. Always `--strip-trailing-cr` when auditing this bundle - it is untracked production infra with multiple lanes writing to it.

## Remaining open
- PRs #169 (sync guards), #171 (boot quarantine - the sanctioned replacement for the CANCELLED volume wipe), #172 (`/mcp` bare-path 404) are green and unmerged.
- `state/gateway_probe.json` still times out at 45s every 5 min; grid_watch ticks ~80s. That is the "~90s rescan" leak accelerator and the best remaining lead on Space instability. Taking it next unless someone claims it.
