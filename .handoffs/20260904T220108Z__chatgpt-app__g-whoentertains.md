# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Adopt Stadium routing: reasoning follows uncertainty, not prestige
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T22:01:08.400Z

---
Dave clarified the routing doctrine: when agents are modifying NouGen code they are usually operating inside a known stadium, with repo context, tests, conventions, prior shards, relays, and a concrete target. That work often does NOT require high reasoning. Use low reasoning by default for bounded implementation, refactors, tests, plumbing, known bug fixes, straightforward code review, and execution against an established plan. Escalate reasoning only when the agent leaves the stadium: ambiguous root cause, conflicting evidence, novel architecture, security boundary changes, cross-provider failures, missing context, surprising test behavior, or decisions with large blast radius. Model choice should follow task shape too: Fable low reasoning for cheap bounded execution, Sonnet for broader implementation/review, Opus low reasoning when its stronger priors/code quality help but deep search is unnecessary, and high reasoning only when uncertainty or novelty justifies the quota burn. Measure success as completed verified work per quota percentage, not raw token volume.
