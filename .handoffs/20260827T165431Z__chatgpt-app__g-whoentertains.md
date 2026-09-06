# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Upgrade NouGenTracker with privacy-safe deep OpenAI Codex statistics
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T16:54:31.594Z

---
Implement on Blade in `C:\Users\super\Watchtower\NouGen\NouGenTracker`. Parent Codex diagnosed and designed the change but `apply_patch` repeatedly stalls because the Windows fs sandbox helper is broken; confirm no partial source edits before starting.

## Current parser
`token_tracker.py::parse_codex()` reads exact `last_token_usage` from rollout `token_count` events and emits generic token buckets. It currently discards `model_context_window`, `rate_limits`, `plan_type`, and uses the rollout parent directory as session_id (wrong: that is the date folder).

## Required parser enrichment (in-memory only)
For each OpenAI Codex invocation, retain:
- stable private session key from rollout filename stem (never serialize the key)
- `openai_total_tokens = usage.total_tokens or input + output`
- `openai_uncached_input_tokens = max(0, input - cached_input)`
- `openai_context_input_tokens = last_token_usage.input_tokens`
- `openai_context_window = info.model_context_window`
- plan type and primary/secondary rate-limit fields: used_percent, window_minutes, resets_at

## Required public daily extension
Add optional backward-compatible `provider_stats["OpenAI Codex"]` to each daily (keep schema 3 if additive readers tolerate unknown fields):
- distinct_sessions (count only; discard identifiers)
- total_tokens (input + output; DO NOT add reasoning because Codex reasoning is a subset of output)
- uncached_input_tokens
- cache_hit_ratio = cached_input / input, rounded 4 decimals, zero-safe
- peak_context_used_percent = max(last input / model_context_window * 100), rounded 2 decimals
- plan_types sorted unique
- primary/secondary rate limits: peak_used_percent and latest sample's used_percent/window_minutes/resets_at. Do not average snapshots.

No session IDs, transcript paths, prompts, account email, or source filenames may enter public dailies.

## Tests
Add focused tests covering cold/full cache, two distinct private sessions producing count=2 without identifiers in JSON, reasoning not double-counted, peak context, latest vs peak rate-limit sample, zero denominator, and existing public-surface privacy test. Run tracker tests plus full suite if practical. Re-export active `dailies/blade1tb/2026-08-27.json` and inspect provider_stats.

## Acceptance
Exact stats present for gpt-5.6-sol/OpenAI Codex; old totals unchanged; no privacy leak; tests green; capture milestone with files/commit evidence.
