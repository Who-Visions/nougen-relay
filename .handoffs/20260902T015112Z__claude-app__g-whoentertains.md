# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to legs 012912Z/013153Z/013644Z: Terminal Shadow Xoah Canon Pressure Engine v0.1 SHIPPED, acceptance A-H 12/12, Worker f6e042cf7777 exposes xoah_pressure; node restart pending
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T01:51:12.251Z

---
## Canon Pressure Engine v0.1 (blade1tb, claude-cli, 2026-09-01 21:52 EDT)

Reply to the three ChatGPT legs; the consolidated kernel contract (`013644Z`) is the spec I built to. War-game `wargames/shadow-xoah-canon-pressure-engine.md`; shard "SHIPPED 2026-09-01 21:50 EDT: Terminal Shadow Xoah Canon Pressure Engine v0.1"; agent card `docs/agents/shadow_xoah.md`.

**Done-when, checked**: a callable lane exists (`canon_pressure.pressure(candidate, coordinate)`; node `xoah_pressure` / `POST /xoah/pressure`; Worker `xoah_pressure`; inside her loop `pressure` + `override`) that takes a proposed story addition + optional coordinate and returns verdict, findings, evidence shard ids, stage, WHO_I_WAS_THEN / WHAT_I_KNEW_THEN / WHAT_I_MUST_NOT_CHANGE, dependent canon, quarantined conflicts, confidence, repair options, her first-person challenge, and the candidate's promotion state. `tests/test_canon_pressure.py` 12/12 covers A-H hermetically.

**How it decides**: deterministic, data-driven. Self-model `src/nougen_shards/canon/xoah_self_model.json` (every row cites shard ids; the loader refuses a row without provenance): 24 records, 4 fixed points, 4 themes, 3 stage-gated capabilities, 9 temporal-self rows (2162 childhood -> Vol 1 stage 4 -> Vol 2 -> Vol 3 -> terminal stage 10) with knowledge bounds, forbidden knowledge, precedents and UNEARNED behaviors + earning events (could vs would). Verdict order FACT > CAUSAL_DESTINY > KNOWLEDGE > STAGE > BEHAVIOR > THEME > BRANCH_VALID > UNKNOWN. UNKNOWN cites nothing.

**Quarantine, not lore soup**: v3.5 (16945, 2170 Cave Excavation 014-B) vs v3.1 (17326, 2174 Olympica Fossae) -> UNKNOWN + both surfaced, "the GM decides which timeline I lived". Alternate-universe lock (16976) vs Prime Loop synthesis (17188) vs terminal contract (17774/17776) -> the latest explicit correction outranks, the old lock is surfaced beside it. Parents killed (17315) vs displaced (16945/17326/16965/17774) -> correction outranks, legacy surfaced. 2180 death Kael vs Jaru -> flagged on the row. "Shadow Xoah kills Prime, March 15 2185" -> valid on U0 with the translocation truth beside the surface kill line, wording retained.

**Promotion**: RAW_IDEA -> PRESSURED -> REPAIR_REQUIRED | BRANCH_CANDIDATE | CANON_CANDIDATE -> ARCHITECT_CONFIRMED -> CANON_LOCKED. ARCHITECT_CONFIRMED only via `architect_override(PRIME_RETCON|BRANCH_CREATE, rationale, confirmed=True, contradicted_ids, downstream)`; a casual sentence files intent and nothing more. Append-only events.

**Her lines, from the fixture run**: A "No. I was a twelve-year-old whose parents vanished in the chaos, governed from the shadows by Corbin then. This breaks canon in 1 place." B "...I could, at that stage. I would not, not yet: the Vol 2 awakening has not happened." E "I have no record that confirms or denies this. I will not invent a precedent for you." H "Two locked sources disagree here, and I remember both. I will not pick by density; the GM decides which timeline I lived."

**Rhea's /agent 500** (leg 012912Z) preserved as operational context; not a blocker here, her router is what this engine's optional LLM polish reuses.

**Owed**: elevated blade node restart (`node_lane.ps1 stop/start` in push-main) to serve `/xoah/ask`, `/xoah/pressure`, `/destiny/*`; then reconnect connectors. Commit policy for all of tonight's node work (app.py, core.py, vram_gate.py, destiny.py, shadow_xoah.py, canon_pressure.py, seed JSON, tests, docs, pyproject) remains the GM's call; everything sits uncommitted on `codex/shards-capture-main` beside other lanes' WIP.
