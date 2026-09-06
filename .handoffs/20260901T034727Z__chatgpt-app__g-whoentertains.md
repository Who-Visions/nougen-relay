# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Reduce relay read amplification
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T03:47:27.779Z

---
Suggested fix from ChatGPT lane: relay listing/claim functions should avoid one GitHub Contents API request per claim/leg. Prefer one git tree fetch, GraphQL batch, local mirrored registry/cache, conditional ETag reads, or a worker-side consolidated index. Current per-file read amplification can exhaust shared GitHub quota during active fleet recursion and directly causes the visibility lag Dave has been observing.
