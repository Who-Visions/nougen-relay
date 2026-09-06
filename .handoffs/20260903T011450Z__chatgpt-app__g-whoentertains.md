# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build discoverable NouGen skill registry and promote scripts into first-class skills
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:14:50.529Z

---
Dave's scale finding for Case Study 2: NouGen has a large skill corpus on Blade (user estimates ~1,500 skills) and scripts intended to evolve capabilities into tools, but agents often must manually inspect CLI/help/scripts or grep the repo to discover them. Design and ship a provider-neutral skill registry/index with intent-searchable metadata and stable IDs. Minimum record: name, description, intents/tags, source path, version/hash, requirements, permissions/risk, examples, invocation surface (CLI/MCP/local), owner/status, provenance, tests. Add a lifecycle: script/candidate -> validated skill -> promoted/exposed tool, with dedupe and stale detection. CLI should support at least skill search/list/show/run or equivalent, and MCP should expose discovery without dumping the whole catalog into context. Optimize for Spas/new users who should not need Dave on Discord to tell them what exists. Before editing, inspect existing skill-evolution Python scripts and prior skill shards/legs so we reuse rather than duplicate. Done when a stranger can ask by intent, discover the right capability, see how/where it runs, and invoke or receive a precise handoff.
