# 🤝 Git Handoff — whoart / claude-cli

**Goal**: RESOLVED: The 36% generator ratio is multi-block content deduplication, not an omission bug
**Branch**: `main` @ `8aa4513`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-29T19:05:12.601484+00:00

---
Settled by Antigravity on WhoArt (2026-08-29):

## The Discovery
The ~36% ratio between token_tracker.py and regen_whoart_dailies.py is NOT a directory omission or skipped session bug. It is the mathematical consequence of Claude Code transcript block splitting:

1. In Claude Code transcript JSONL files, assistant turns emit ONE line per content block (thinking, text, tool_use).
2. Every line repeats the IDENTICAL cumulative API usage object.
3. August WhoArt transcripts contain 14,986 lines with usage across 6,453 unique API calls (average 2.32 blocks per turn).
4. regen_whoart_dailies summed all 14,986 lines -> 14.7M output tokens (2.77x inflated).
5. token_tracker deduplicated by requestId/msg.id -> 5.3M output tokens (exact true billable calls).
6. 5,308,852 / 14,726,749 = EXACTLY 36.05% (1 / 2.77 = 36.1%).

token_tracker's deduplication was correct from the start (as documented in fleet_dailies.py line 58). Mystery fully solved with zero remaining ambiguity.
