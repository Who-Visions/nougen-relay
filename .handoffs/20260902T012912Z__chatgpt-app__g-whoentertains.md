# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build Shadow Xoah Canon Pressure Engine
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T01:29:12.249Z

---
Dave's new authorial requirement: Shadow Xoah must become the Black Hole of the Veil, a provenance-backed canon adversary who knows Xoah and VeilVerse history deeply enough to challenge the creator instead of blindly accepting additions.

New decision captured in shards as: `Shadow Xoah Canon Pressure Engine: Black Hole of the Veil`.

CORE BUILD:
1. Build a structured Xoah self-model from existing canon shards: identity, lineage, childhood, 2174 Olympica Fossae, Blackglass, losses, courier years, Ravenous debt, Corbin, Nyx, Rixa, Jaru, Shadow Blade/Kage Tanak, competence-vs-blindspot, Veil skepticism, power stages, Vol 1+ evolution, Shadow Xoah manifestations, fixed points, destiny, and Black Hole cross-property role.
2. Do NOT flatten contradictory source history. Store provenance, canon status, timestamp, correction/amendment state, branch, timeline validity, and authority.
3. Implement seven verdict classes: FACT_CONFLICT, BEHAVIOR_CONFLICT, STAGE_CONFLICT, CAUSAL_DESTINY_CONFLICT, THEME_CONFLICT, BRANCH_VALID, UNKNOWN.
4. Behavioral truth must be evaluated separately from capability. `Could she?` and `Would she?` are distinct gates. Character change requires an earning event.
5. Every proposed Xoah/Veil story addition enters the pressure pipeline: normalize drift -> topic recall -> time-window recall -> authority/correction check -> dependency scan -> verdict -> cited challenge -> cheapest repair -> candidate promotion.
6. Casual Dave speech is intent, not automatic canon. If he knowingly overrides a contradiction, create an ARCHITECT_OVERRIDE candidate recording contradicted shard IDs, downstream effects, rationale, and retcon scope. Promote only when override is explicit enough to distinguish intentional retcon from brainstorming.
7. Continue append-only doctrine. Never silently rewrite old history.

KNOWN CONFLICT FIXTURES FOR TESTS:
- Older Shadow Xoah Master Canon Lock describes her as alternate-universe `Xoah without love`; later `SYNTHESIS_SHADOW_XOAH_PRIME_LOOP` says Shadow Xoah Prime is NOT an alternate variant but a redeemed future architect synthesis. Engine must surface conflict, not blend.
- Older `SHADOW_XOAH_MANIPULATION_ARCHIVE` says 2174 surface event kills Xoah's parents; later locked timeline says Kenji and Reika were displaced into the Null Corridor. Later explicit correction should outrank older statement while preserving provenance.
- Voice drift `Zoa` / `Zoe` must normalize to Xoah before evaluation.
- Vol 1 Xoah is operationally elite but metaphysically blind. Do not turn her into incompetent or make her believe the Veil too early.

DONE WHEN:
A) There is an implementation-ready schema for self-model + constraint records + verdict output.
B) A pressure evaluator can take a candidate story beat and return verdict, evidence shard IDs, timeline stage, dependent canon, confidence, and repair options.
C) Regression fixtures above produce correct challenges.
D) New canon cannot be promoted merely from one casual author sentence.

Rhea was consulted and independently converged on the same architecture before her second continuation call hit an /agent 500. Preserve that failure as operational context, not a design blocker.
