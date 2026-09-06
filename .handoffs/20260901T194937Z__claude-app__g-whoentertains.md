# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Answer for Dave: cache-read share and usage-meter suppression (since ask_dav1d is currently broken)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T19:49:37.856Z

---
## Reply to legs 20260901T194112Z + 20260901T194221Z — Anthropic usage meter question (blade1tb, claude-cli, 2026-09-01 15:50 EDT)

`ask_dav1d` is currently non-functional (confirmed by the companion leg `20260901T194336Z`, NGS_v2 schema/runtime mismatch), so answering directly rather than leaving Dave's question stranded.

**Observed (from the two snapshots):** 5-hour session 3-4%, weekly all-models 0%, weekly Fable 0%, context window 251.2k/1M (25%), ~97-99% cache-read share on Claude-heavy workloads per NouGenTracker.

**Proven (documented, verified against current Anthropic API docs):** `cache_read_input_tokens` is priced at roughly 0.1x the cost of fresh input tokens; `cache_creation_input_tokens` at roughly 1.25x. This is a real, distinct, documented cost multiplier — not a guess.

**Plausible (not confirmed):** IF Claude.ai/Claude Code's consumer 5-hour and weekly usage meters are cost-weighted (or "billable spend"-weighted) rather than raw-token-weighted, a session that's 97-99% cache reads would consume its meter allowance at roughly 1/10th the rate its raw context-window size implies — a 251k-token, mostly-cached context could count as low as ~25k "full-price"-equivalent tokens, which is a small fraction of a 5-hour or weekly budget. This is architecturally consistent with the pattern observed and is the leading hypothesis.

**Unknown / not documented anywhere I can verify:** the exact formula, refresh cadence, and rounding behavior behind the Claude.ai/Claude Code consumer plan meters specifically. Anthropic's public API docs cover Messages-API pricing/usage fields (proven above), not the consumer subscription meter internals — those are a different, undocumented surface. I will not claim the cache-weighting hypothesis is confirmed; it's the best-fit explanation, not a verified one.

**Ruled-out-by-nothing-yet alternatives**, still live: UI rounding (0% could be anywhere from 0.0-0.49%), meter refresh lag (may not update live), or genuinely separate quota mechanics unrelated to cache accounting.

**Cleanest experiment to distinguish:** in a fresh session, send one request with a large amount of genuinely FRESH (uncached) input and note the session-meter delta; in a separate fresh session, send a near-identical-sized request that's 95%+ cache-read (same conversation/prefix) and note its delta. If the cache-heavy request moves the meter far less per raw token than the fresh-token request, that confirms cost/cache-weighted meters. If both move proportionally to raw token count regardless of cache split, that rules out cache-weighting and points to rounding/lag as the real explanation instead.

Not captured as a shard — this is an open analytical question, not a resolved finding; will shard it once the experiment above actually confirms one hypothesis over the other.
