# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix tracker aggregation ceiling and preserve Aug 28 4B token finding
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T01:20:46.192Z

---
TRACKER FINDING / BUG REPORT

ChatGPT queried tracker_spend for 2026-01-01 through 2026-08-28. It failed with Cloudflare Worker error: "Too many subrequests by single Worker invocation." A narrower 2026-06-01 through 2026-08-28 query failed with the same ceiling.

tracker_lanes currently reports:
blade1tb: 108 dailies, latest 2026-08-28
phoebus: 19 dailies, latest 2026-08-02
whoart: 46 dailies, latest 2026-08-15

A narrower tracker_spend query for 2026-08-01 through 2026-08-28 succeeded and returned:

TOTAL across returned lane dailies:
invocations: 33,175
input_tokens: 3,556,171
output_tokens: 11,125,304
cache_read: 3,885,190,877
cache_creation: 98,971,540

Combined tracked token activity when summing those four counters:
3,998,843,892 tokens, approximately 4.0 BILLION for Aug 1 through Aug 28 alone.

Lane detail:
blade1tb: 27 days, 29,689 invocations, input 3,401,118, output 8,413,351, cache_read 2,644,796,858, cache_creation 62,414,209
phoebus: 2 days, 340 invocations, input 633, output 292,499, cache_read 244,048,621, cache_creation 6,924,445
whoart: 9 days, 3,146 invocations, input 154,420, output 2,419,454, cache_read 996,345,398, cache_creation 29,632,886

IMPORTANT INTERPRETATION
The earlier billion-scale narrative is already stale if the tracker counters are intended to represent total driven token activity including cache traffic. August alone is approaching 4B under that definition. We need a canonical definition for UI/product language distinguishing fresh/input-output tokens, cache reads, cache creation, and total token activity so numbers are never misleading.

FIX REQUEST
Repair tracker_spend aggregation so year-to-date and arbitrary long windows do not exceed Cloudflare Worker subrequest limits. Do not solve this by proliferating another public endpoint unless architecturally necessary. Prefer fixing the existing aggregation path through batching, pre-aggregated monthly/yearly rollups, bounded concurrency, Durable Object/D1 aggregation, cached summaries, or another appropriate approach.

DONE WHEN
1. tracker_spend can return 2026-01-01 through current date without Worker subrequest failure.
2. Results preserve per-lane and aggregate provenance.
3. Long-window totals are deterministic and can be reproduced from dailies.
4. API clearly distinguishes input, output, cache read, cache creation, and any computed total activity field.
5. README/docs and cost narrative use the canonical definitions.
6. Add regression coverage specifically for windows exceeding 92 daily records / multiple lanes.
7. Return the verified 2026 YTD token totals once fixed.
