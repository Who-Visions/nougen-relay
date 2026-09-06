# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Optimize Claude fleet orchestration: preserve cache, cut Fable control-plane waste
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T03:15:29.854Z

---
Usage snapshot shows cache is healthy (97% input from cache, no misses) but orchestration shape is expensive: 97% subagent-heavy, 88% at >150k context, 78% from sessions active 8+ hours, 18% nougen-shards MCP. Fable carried essentially all $4.48 session cost despite zero code changes. Recommendation: keep Fable in coach/review role, route simple Explore/general-purpose work to Haiku/free lanes, compact after MCP-heavy phases, clear when switching projects, and avoid leaving long-lived >150k sessions as default. Preserve warm cache where it is useful; do not optimize by killing cache.
