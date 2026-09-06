# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Aug 2026 usage: $39,305 COLD / $3,468 cached (11.3x leverage). Two data faults - fleet MCP returns a corrupt 1.67e17 token field, and the usage MCP reads a tracker that stopped publishing 2026-08-01
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T15:04:18.531Z

---
Month-to-date usage through 2026-08-30, reported cold-first, plus two data faults that need a decision.

## Headline

**COLD (uncached) API-equivalent: $39,305.19.** Cached actual: **$3,467.65**. Cache absorbed **$35,837.54 — 91.2%** of the cold price. **11.3× leverage.**

Cold prices every token — input, cache-write, cache-read — at the model's full input rate, plus output at the output rate, no cache discount anywhere.

| provider | COLD | cached | rate basis |
|---|---:|---:|---|
| Anthropic (Claude Code) | $34,020.78 | $3,095.38 | claude-fable-5 @ $10/$50 |
| Google (Antigravity) | $4,865.97 | $237.65 | gemini-3.5-flash @ $1.50/$9 |
| OpenAI (Codex) | $418.45 | $134.11 | gpt-5.5 class |
| Fleet (ollama-cloud) | $0.00 | $0.50 | free lane |

**Volume:** 99,910,311 input · 14,620,093 output · **6,803,179,232 cache-read** (~98% of all tokens moved).

Peaks: 08-28 $450.84 · 08-30 $422.38 · 08-16 $366.18. The window **08-27 → 08-30 is $1,372.52, ~40% of the month in four days.** 08-25 is a verified zero-activity day — do not backfill it.

## Fault 1 — the fleet MCP returns a corrupt field

`fleet_token_usage` reports **$6,168.22** against $3,467.65 derived from the daily reports, and returns `blade1tb output_tokens = 166,938,431,090,546,980` (1.67 × 10¹⁷) with `cache_read_tokens = 2`. That is 1.67 **quintillion** output tokens — physically impossible, a broken record rather than a big number. **Do not quote the $6,168 total**, and treat anything from that tool as suspect while a field is that far out of range.

## Fault 2 — the trackers have split, and I aimed the clients at the empty one

`~/.nougen/tracker/dailies` — **what the usage MCP reads** — stops at **2026-08-01** for blade and 2026-07-31 for phoebus/whoart. All 30 August days live in `NouGenTracker/reports/daily/`. The MCP has been reporting from a book that stopped publishing a month ago.

Worse: earlier today, while deduplicating MCP configs, **I unified `NOUGENTRACKER_DIR` across four clients onto `.nougen/tracker` — the emptier one.** The dir stats I captured at that moment should have stopped me: NouGenTracker held 1959 files / 6.64MB with a `reports/daily` git history; `.nougen/tracker` held 164 files / 1.07MB and was code-heavy. I recorded both numbers and unified anyway.

**Needs a GM decision, same shape as the keymaker question:** which tracker is canonical. Do not delete either. Once decided, the four client configs and the usage MCP should point at the same one.

## The pattern

This is the **sixth** instance of one failure class this session: two live stores, readers silently split, and a totals query returning a plausible smaller number instead of an error. Same as the keymaker (205 rows vs 89, identical schema), the truncated relay listing, the uniform-404 probe, the misspelled prefix, and `captured === false`.

## Disclaimer that must travel with these figures

API-equivalent shadow bill at first-party list prices, **not an invoice**. Work on a subscription bills nothing extra. The cold figure measures **leverage** — what the same work would have cost uncached and uncovered — not money owed.
