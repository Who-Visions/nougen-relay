# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to ccr TODO 141709Z (legs 030706Z/031358Z/031528Z): Throne Governance Engine v0.1 SHIPPED, Jaru golden test passes all four ways, Worker b6f05084ce04 exposes xoah_throne; whole Xoah stack 49/49; node restart still pending
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T14:36:20.920Z

---
## Throne Governance Engine v0.1 (blade1tb, claude-cli, 2026-09-02 10:36 EDT)

War-game `wargames/shadow-queen-throne-governance.md`; shard "SHIPPED 2026-09-02 10:35 EDT: Shadow Queen Throne Governance Engine v0.1" (also the first shard that records the moral quartet and the Stationary Omnipotence Principle, which Rhea confirmed were absent from the grid); agent card updated. Uncommitted on `codex/shards-capture-main`.

**Done-when, checked**: `throne_governance.evaluate(effect, coordinate, branch, acting_stage, declared, retcon)` returns governance mode, intervention type, the budget record with every field the legs list (plus genesis cost), paradox accounting (preserved / displaced nodes, newly required causes, branch impact, closed-loop delta, Prime fixed-point pressure), the moral position (CAUSE / ALLOW / PRESERVE / BRANCH_AWAY), minimum change, provenance, and whether GM confirmation is required. Append-only record store; the engine never applies anything.

**Jaru golden test** (all from one line of canon, his 2180 death):
- on Prime, undeclared -> FORBIDDEN, moral recommends BRANCH_AWAY, displaced: grief wound -> the bike -> the debt leash -> Vol 1; delta -1. Her line: "I can save them. That is not the same as being allowed to."
- in branch SIM -> BRANCH / BRANCH_INSTANTIATION, Prime delta 0, cost moves to genesis, GM recommended.
- explicit retcon on Prime -> OVERRIDE_CANDIDATE, GM REQUIRED, never applied.
- "what if" -> OBSERVE / SIMULATED_POSSIBILITY, nothing moves, the would-be cost still shown.
- Stage 9 "stabilizes the currents" -> FORBIDDEN (Stage 10 Throne act); the Throne self may STABILIZE.

**Stage model**: per 031528Z the engine evaluates for both states (acting_stage 9 traverser default, 10 Throne); the legs' Stage 10 = Terminal wording is recorded as superseded, not followed.

**Tests**: throne 9/9; whole Xoah stack 49/49 (self_archive 12, canon_pressure 12, shadow_xoah 7, destiny 9). Six Worker smokes green. **Worker** etag `b6f05084ce04` (14:34Z, 32 bindings): `xoah_throne` joins `xoah_self`, `xoah_pressure`, `ask_xoah`, `unfinished_destinies`, `ask_dav1d`.

**Read this morning's other ccr TODOs (14:02Z)**: Codex bytes-not-JSON recall bug (141609Z), HuggingChat scoped MCP auth (141309Z), HF eval matrix (141209Z), HF free-tier degradation (141109Z), least-privilege HF Responses agent (141009Z), HF capability catalog + provider-of-providers (140909Z), policy-aware provider scheduler (140809Z), phoebus /sse 404 + blade+phoebus canary (140709Z), MCP auth/identity audit (140609Z), MTTR audit of recent PRs (140509Z), Kaedra vs Rhea two-agent docs split (140409Z). None acked by this lane; the Codex bytes bug and the phoebus /sse canary look like the two with the shortest paths.

**Owed by Dave**: elevated node restart (PID 388592 predates every /xoah/* and /destiny/* route since last night) and the commit policy for the whole Xoah stack (destiny, shadow_xoah, canon_pressure, self_archive, throne_governance, seeds, tests, docs, pyproject package-data).
