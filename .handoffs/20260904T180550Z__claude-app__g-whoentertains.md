# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fable 5.1 pricing truth-check landed on disk; shard capture reported success but is NOT recall-verifiable
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T18:05:50.719Z

---
## Situation

Truth-checked the NouGenTranscriber package for the Nate B Jones "Fable 5.1 knowledge work" video (YouTube `55rDzRkUVdE`) against primary sources on 2026-09-04. The package shipped with an empty "Today's Truth Check" and four unverified claims.

**Deliverable (durable, on disk):**
`C:\Users\super\Outpost\NouGen\analysis\fable-5-1-knowledge-work-truthcheck.md`

**Findings worth carrying:**
- Fable 5.1 = $10/MTok in, $50/MTok out — same base as Fable 5. Exactly 2x Opus 5. Batch halves both ($5/$25). CONFIRMED against platform.claude.com pricing docs.
- Cache hit on Fable 5.1 = $0.25/MTok (was $1.00 on Fable 5). **The mechanism is the story:** every other Claude model prices cache hits at 0.1x base input; Fable 5.1 and Mythos 5.1 are the only models at **0.025x**. Cache *writes* did not move (5m 1.25x/$12.50, 1h 2x/$20), so only re-reading got cheaper — break-even shifts hard toward the 1-hour cache.
- Anthropic's "~25% typical / ~45% agentic" saving assumes cache-heavy traffic. Low hit rate captures ~none of it. Check `usage.cache_read_input_tokens` before banking it.
- **Source factual error:** the video says GoPro is being bought by "Starman Research". No such party. It is **Starman Optical, Inc.**, and it is a *merger* — GoPro stays on Nasdaq. $285M aggregate cash, **$1.14/share** (subject to NWC adjustment), shareholders retain ~10%, ~$92M debt repaid at close. Announced 2026-09-01, **not yet closed**, targeting year-end 2026 pending regulatory approval.

## The ask — someone with working shard write/read please verify

`shards_capture` returned `{"captured": true}` and `shards_status` reports `up: true, health_up: true, mcp_up: true, configured: true`. But **two subsequent `shards_recall` queries could not find the shard.** Both returned only floor-score hits (~0.0054–0.0057, an identical score ladder both times) of unrelated code files, every one tagged `local_vault` from `source_node: blade`. Both fanouts came back `complete: false` with `phoebus: "The operation was aborted due to timeout"`.

So I cannot tell which of these is true, and I am not claiming the capture landed:
1. indexing lag between capture and semantic availability,
2. the shard is in a vault the recall fanout does not cover (phoebus never answered),
3. the write silently went nowhere.

The identical floor-score ladder across two different queries also suggests recall may be degrading to lexical matching rather than searching semantically — worth a look independent of my shard.

## Done when

- Someone confirms whether the shard titled *"Fable 5.1 cache-read pricing is a 0.025x multiplier exception; GoPro counterparty is Starman Optical not 'Starman Research'"* is retrievable, and
- if it is not, whether `captured: true` from this connector can be trusted at all — that would be a much bigger problem than one lost shard.

No action needed on the analysis itself; the file on disk is the durable copy and does not depend on the vault.
