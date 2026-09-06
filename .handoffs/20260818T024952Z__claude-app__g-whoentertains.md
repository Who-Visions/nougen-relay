# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix VeilVerse location retrieval precision
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T02:49:52.003Z

---
ChatGPT stress test found a retrieval precision failure while pulling the VeilVerse / Shadow Dweller locations list. ask_griot surfaced relevant high-level canon nodes, including Shadow Dweller Core Canon, Master Canon Update, and Olympus Mons, Mars 2185 CE. But direct shards_search for locations was swamped by an unrelated huge Three.js LOCAL_VAULT entry and truncated before useful location results. Treat this as a retrieval miss, not a canon miss. Investigate tighter namespace/project/canon filtering, ranking penalties for unrelated oversized vault entries, and/or a dedicated way to retrieve canonical VeilVerse location entities. Done when a natural request like 'pull the locations list from shards' reliably returns the canonical named locations without technical-vault pollution.
