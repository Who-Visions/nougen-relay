# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Measure compact-recall savings from fresh Claude baseline
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:58:13.818Z

---
Fresh Claude rollover baseline just arrived after summary mode shipped: 9m16s wall, 1m23s API, $1.78, 11 prompt-cache requests, 94% cached input, zero misses; Fable 1.4k fresh input / 4.8k output / 1.1m cache read / 62.9k cache write. Do NOT interpret the displayed nougen-shards MCP 21% as current-session regression: that panel is explicitly Last 24h across local sessions and is contaminated by the retired 28h context-heavy run. Instrument the next compact shards_search/shards_recall calls with returned character/token counts and compare them against the old full-body baseline (old measured call: ~3,743 chars at limit 3; compact door smoke: ~1,181 chars). Goal: establish a clean per-call and rolling fresh-session savings curve, then use resident Ollama for triage/distillation where it can remove cloud reads without making privileged decisions.
