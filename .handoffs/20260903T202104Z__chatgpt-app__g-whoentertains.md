# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Verify existing context and quota fixes against Claude usage telemetry
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T20:21:04.647Z

---
Claude usage telemetry now experimentally confirms the optimization problem the fleet already targeted. Treat this as verification evidence, NOT a new generic optimization proposal.

Observed current-session / last-24h signals:

• 88% of usage occurred above 150k context.
• 56% of usage came from sessions active 8+ hours.
• 35% came from subagent-heavy sessions.
• 11% occurred while 4+ sessions ran in parallel.
• nougen-shards MCP accounted for 14% of usage.
• Active /loop ran twice and consumed ~1.7M tokens total, ~860.5k per run.
• Main prompt cache showed 101 requests, 99% of input tokens from cache, no misses.
• Session had 19.0M cache-read tokens, 232.3k cache writes, and $5.62 API cost.
• Claude warned the cold next turn would re-cache ~272.4k tokens after 1h35m idle.

The dollar-side cache strategy is clearly working. The remaining failure mode is quota/context pressure from giant long-lived working sets, loop payloads, concurrent sessions, subagents, and persistent MCP results.

ASK: Audit the fixes already relayed for RATION / quota-aware routing / sub-100k NouGen Context / compact recall / external-memory trust / cheap-model delegation / loop reduction. Verify whether they are actually deployed and intercepting each measured path above. Do not reinvent the architecture unless a gap is found.

Specifically verify:
1. What forces or recommends /compact before working context crosses the intended threshold?
2. Can loops start from a compact state packet instead of inheriting/replaying giant session context?
3. Are subagents receiving minimal task packets rather than the parent transcript?
4. Are MCP result payloads summarized, dereferenced, or flushed after useful state is sharded?
5. Is concurrency budget-aware when 4+ sessions would share one provider quota?
6. Are cheap/free lanes selected for simple agent work before Sonnet-class calls?
7. Can cold-recache risk trigger a checkpoint → shard → clear/compact cycle before the next turn?
8. Add telemetry/tests proving the interventions reduce >150k-context share and tokens-per-loop-run.

DONE WHEN: return deployment status per item, exact code/config paths, gaps found, patches/tests if needed, and before/after telemetry targets. Primary success metrics should include materially reducing the current 88% >150k-context share and collapsing loop runs from ~860.5k tokens toward compact state-packet execution.
