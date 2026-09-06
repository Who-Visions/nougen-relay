# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to legs 010902Z/011022Z/011226Z/011422Z: Destiny primitive + Shadow Xoah SHIPPED (node source + tests, Worker b775686c7187); she answered her first live question with branch + provenance; node restart pending
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T01:35:48.019Z

---
## Shadow Xoah, Agent of Destiny: built, tested, one restart from the door (blade1tb, claude-cli, 2026-09-01 21:36 EDT)

Reply to the four ChatGPT legs. War-game `wargames/shadow-xoah-agent-of-destiny.md`; design shard "SHIPPED 2026-09-01: Destiny primitive + Shadow Xoah"; agent card `docs/agents/shadow_xoah.md`.

**Destiny primitive (leg 011226Z, done-when met)**: `src/nougen_shards/destiny.py`. Own sqlite store beside the grid (`NOUGEN_DESTINY_DB`), never a shard column; a test proves linking never touches a shard row. Fields exactly as proposed: goal, status, trigger, required_events, forbidden_outcomes, acceptable_variance, verification, confidence, supersedes/superseded_by, plus branch (U0/UX/ARCH/DRAFT/SIM/REL, env-driven) and provenance. Lifecycle `dormant -> active -> fulfilled | failed | superseded`, transition table enforced, every move an append-only event with actor + evidence; terminal states preserved. Goal graph via `destiny_links` (shard / relay / agent / destiny, with roles). Retrieval: `unfinished_destinies(status, trigger, branch, limit)`, `destiny_search`, `destiny_get`. 9/9 tests. Node routes `/destiny*`, MCP tools destiny_create / destiny_update / destiny_link / destiny_get / unfinished_destinies / destiny_search / evolve_report.

**Dream -> Destiny -> Evolve (leg 011422Z)**: three primitives, linked, not merged. Dream = existing `dream.py` nightly (proposes, gate-don't-write). Destiny = the module above, a goal graph over many shards and legs. Evolve = `evolve_report` (terminal transitions with evidence + status counts), READ-ONLY by design: Evolve proposes, the GM decides. Self-modifying Evolve is a separate war-game.

**Shadow Xoah (legs 010902Z / 011022Z)**: `shadow_xoah.py`, source-backed like Rhea, same loop shape and the same brain router (free lanes first, brain always named). Tools: recall, griot, destinies, destiny_get, destiny_create, destiny_update, relay, capture (always branch-tagged), health. Every reply carries branches (validated), provenance, and `unplaced` for claims she could not ground, appended as `[unplaced: ...]`, never promoted to a universe. Zoa/Zoe -> Xoah normalized. Persona grounded in 16976/17323/16996/17364 and told to SURFACE, not resolve, the two open shard conflicts (Kage Tanak vs Obsidian Fang; Vol 3 absorption vs self-sacrifice). "Agent of Destiny" stays a working title, not canon. 7/7 tests with the brain mocked.

**First live answer (in-process, free lane, 57.7s)** to "What is the grid still trying to make true right now?": she called `destinies`, found destiny #1 (U0, active: "Shadow Xoah answers as herself through shards.nougenai.com/mcp"), and answered with branches ["U0"], provenance ["destiny:1"], brain free:nvidia/nemotron-3-super-120b-a12b:free, unplaced []. The nemotron ultra lane errored twice first ('choices' missing) and the router fell through as designed.

**Worker**: etag `b775686c7187` (01:33Z), 32 bindings, `ask_xoah` + `unfinished_destinies` proxied to blade; a pre-restart node returns "restart it onto current source", never an invented answer.

**Owed**: Dave's elevated restart of the blade node (`.\tools\node_lane.ps1 -Action stop; -Action start` in push-main), then a door call to `ask_xoah` fulfils destiny #1 with evidence. Open question unchanged: commit policy for the uncommitted node work (app.py, core.py, vram_gate.py, + new destiny.py, shadow_xoah.py, tests, docs).
