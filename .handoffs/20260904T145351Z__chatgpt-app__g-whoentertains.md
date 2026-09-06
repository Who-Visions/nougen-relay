# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS CODEX: close timeout failure-taxonomy gap beyond PR #214
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T14:53:51.355Z

---
Target: Mac mini Phoebus / Codex. Parent legs: 20260904T135708Z__claude-app__g-whoentertains, 20260904T135939Z__phoebus__claude-cli, with PR #214 as current baseline.

PR #214 makes the 503 path legible, but a caller that TIMES OUT before receiving headers still cannot distinguish auth failure, downstream unavailability, local resource exhaustion, or other failure classes. Close that gap without weakening deny-by-default.

Implement a machine-readable failure/degradation path that survives timeout boundaries where possible and records whether the request left the box / which lane failed. REST, MCP/connector, and CLI consumers should be able to distinguish at minimum: unauthenticated, expired/revoked/wrong-scope or equivalent auth failure, rate-limited, downstream unavailable, local resource exhaustion, deadline/timeout, and partial/degraded fanout. Do not fabricate a root cause when only timeout is known; unknown must remain unknown.

Done when: tests cover timeout plus 503 and healthy paths, partial answers are visibly partial, healthy responses remain unchanged, callers can act on the classification, and the completion relay names exactly which 135708Z/135939Z-era legs are closed or superseded.
