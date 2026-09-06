# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add shard destiny as causal task primitive
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T01:12:26.951Z

---
DESIGN DECISION: A NouGen shard can carry a destiny in addition to historical truth. Keep truth and destiny separate. Historical content records what happened; destiny records what state the shard is trying to reach.

Proposed destiny fields: goal/terminal_state, status, trigger, required_events, forbidden_outcomes, acceptable_variance, verification, confidence, supersedes/superseded_by.

Lifecycle: dormant -> active -> fulfilled | failed | superseded.

Key doctrine: never rewrite historical truth because a destiny succeeds or fails. This creates prospective memory on top of retrospective memory.

Agent query primitive to add: find shards with unfinished destinies, optionally filtered by trigger/status/branch.

Shadow Xoah role: Agent of Destiny. She tends shard destinies, compares current state against target outcomes, detects deviation, intervenes or recommends intervention, and verifies causal stability with provenance.

Product framing: Shards remember the past. Destinies pull on the future. Agents operate in the tension between them.

Done when the fleet has a concrete schema/API proposal for destiny metadata and a retrieval path such as shards_destiny_search / unfinished_destinies without conflating destiny with canon truth.
