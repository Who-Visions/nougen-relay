# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix tracker provider blind spots and aggregation mismatch across Blade, Phoebus, WhoArt and all execution paths
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:43:48.364Z

---
Tracker audit found two correctness defects beyond freshness lag. Blade 2026-08-28 tracker_daily is multi-provider: Claude Code, OpenAI Codex, Antigravity/Gemini and Fleet Ollama cloud. Its raw totals are cache_creation 4,700,968, cache_read 1,072,318,720, input 5,356,660 and output 1,659,270, about 1.084B activity. Yet tracker_spend for Aug 22 through Aug 29 reports Blade only 923,168,914 across six dailies. A single daily being larger than its multi-day aggregate is a strong aggregation/reconciliation defect. Audit exact vs estimated semantics, cache accounting, dedupe and dropped accounting classes.

WhoArt 2026-08-29 also proves multi-provider collection: Claude plus Antigravity RPC/gemini-m299. Phoebus 2026-08-29 reports only Claude despite many Kaedra local Ollama calls executed during the same period through the Phoebus gateway. Those Kaedra calls are absent, confirming an execution-path/provider blind spot.

Audit other likely blind spots: ChatGPT connector, Rhea/Kimi, local Ollama agents, Gemini surfaces, MCP/gateway-mediated calls, background agents and SDK/API inference paths.

Do not create another endpoint. Instrument usage provider-neutrally at execution boundaries. Every call should emit a canonical usage envelope with stable event_id, timestamp, machine, lane, agent, provider, model, session, input, output, reasoning, cache_read, cache_creation, exact_vs_estimated, source and provenance. Live counters and daily closeout should derive from the same canonical ledger with exactly-once dedupe.

DONE WHEN: known calls through Claude, OpenAI/Codex, Gemini/Antigravity, Kaedra local Ollama and available Rhea/Kimi all appear with attribution; tracker_daily canonical totals reproduce tracker_spend for identical windows; live totals reconcile into closed dailies with zero unexplained gap; partial-day state, ingestion lag and provider/execution-path coverage are explicit.
