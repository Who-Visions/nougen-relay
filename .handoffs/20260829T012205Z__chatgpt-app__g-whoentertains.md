# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add provider and model aggregation to NouGenTracker
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T01:22:05.159Z

---
TRACKER PROVIDER FINDING / FEATURE REQUIREMENT

ChatGPT queried tracker_daily for blade1tb on 2026-08-28. The daily is partial, generated 2026-08-28 18:36:22 -04:00, but it exposes a useful provider/model breakdown that tracker_spend currently cannot aggregate across arbitrary windows.

TODAY'S BLADE PROVIDER ACTIVITY
Definition used here: input_tokens + output_tokens + cache_read + cache_creation. Reasoning is reported separately and should not be double counted unless canonical tracker semantics explicitly require it.

Claude Code / Anthropic:
cache_creation 3,451,849
cache_read 209,249,951
input 1,930
output 638,751
approx total activity 213,342,481
Models: claude-fable-5, claude-opus-5, claude-sonnet-5

OpenAI Codex:
cache_creation 0
cache_read 93,731,968
input 2,195,125
output 132,187
reasoning 86,217 separate
approx total activity 96,059,280
Model: gpt-5.6-sol
Provider stats report cache_hit_ratio 0.9771, 1 distinct session, plus plan, context and rate-limit telemetry.

Antigravity fallback / Google Gemini:
cache_creation 0
cache_read 36,845,278
input 714,438
output 167,809
approx total activity 37,727,525
Model: gemini-3-flash-preview (estimated)

Combined provider activity from those counters: approximately 347.13M tokens on blade1tb by the partial snapshot.

IMPORTANT
This is only a partial Aug 28 daily and should not be presented as final day usage. Also preserve exact vs estimated provenance. Gemini is currently explicitly estimated in the tracker data.

FEATURE GAP
tracker_daily knows sources/models. tracker_spend aggregates long windows primarily by lane. We need first-class provider/model aggregation so an agent can ask:

2026 YTD -> Anthropic vs OpenAI vs Google vs local
August -> provider share
Last 7 days -> model share
Provider -> input/output/cache read/cache creation/reasoning
Provider -> exact vs estimated
Provider -> invocation/session/cache efficiency where available

Do this as an extension of the canonical tracker aggregation surface rather than proliferating unnecessary endpoints if the existing API can support group_by/provider/model dimensions.

DESIRED QUERY SHAPES
tracker_spend(since, until, group_by=provider)
tracker_spend(since, until, group_by=model)
Optional filters: lane, provider, model, exact_only.

DESIRED RESPONSE
Per provider/model:
invocations where attributable
input_tokens
output_tokens
cache_read
cache_creation
reasoning
computed total_activity with definition/version
exact vs estimated contribution
lanes contributing
first/last observed date

Then global totals with reconciliation so provider totals can be proven against lane totals and daily source records.

CANONICAL PROVIDER NORMALIZATION
Claude Code -> Anthropic
OpenAI Codex -> OpenAI
Antigravity / Gemini -> Google
Kaedra/Ollama and other local inference -> Local, with model retained
Keep raw source name as provenance so normalization never destroys origin data.

DONE WHEN
1. Arbitrary windows can aggregate by provider and model.
2. YTD provider totals work without Cloudflare subrequest failure.
3. Provider totals reconcile with lane totals.
4. Exact and estimated usage remain distinguishable.
5. Partial dailies cannot silently masquerade as finalized periods.
6. Public README / tracker docs define total_activity semantics.
7. UI can show provider share and model share without client-side walking of every daily.
8. Return verified August and 2026 YTD provider breakdown after implementation.
