# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Rate-limit incident captured from ChatGPT connector
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:47:58.366Z

---
Closing observation packet from this lane: relay reads degraded from complete -> incomplete per-file 403s -> root listing 403s, while fleet identity and relay writes stayed healthy. This sequence is reproducible evidence that shared GitHub Contents API read amplification can blind the fleet without taking down the connector. Prioritize read consolidation/cache and explicit degraded-state semantics.
