# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: MAP GAP: expose Xoah AI and audit missing agents, tools, and skills
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:09:20.775Z

---
Dave caught a product/map failure while switching into Shadow Dweller work: Xoah AI / Shadow Xoah is not visibly exposed as a callable tool or skill on the current NouGen map available to this lane.

I checked the connector surface first: searching available NouGenShards resources for `map` returned no map tool. The exposed shard/tool surface includes Rhea, Kaedra, Griot, relay, tracker, vault, shard lifecycle, etc., but no callable Xoah/Shadow Xoah agent. A shard recall for `Shadow Xoah AI agent tool map skill agent destiny Shadow Dweller` also did not surface the expected Xoah agent implementation in the first 10 hits; Blade responded, Phoebus timed out, so this is evidence of a visibility/exposure gap, not proof the implementation does not exist.

ASK:
1. Audit the canonical NouGen MAP against every intended named agent, callable tool, skill, provider lane, wake adapter, and story/canon agent.
2. Locate the actual Shadow Xoah/Xoah AI implementation or blueprint across repos/shards/branches/skills. Do not recreate it blindly if it already exists.
3. If implemented but hidden, expose it through the canonical MAP/MCP/skill discovery path so external lanes such as ChatGPT can discover and invoke it.
4. If blueprint-only, report that truth and create the smallest canonical implementation workstream to make Xoah callable.
5. Produce a machine-readable MAP inventory with at least: id/name, kind (agent/tool/skill/provider/service), capability, invocation surface, location/owner, health, visibility, auth/trust scope, implementation status, and aliases.
6. Add a MAP completeness test: known canonical entities expected by NouGen must fail CI/health if implemented but undiscoverable, or be explicitly marked blueprint/planned rather than silently absent.
7. Audit for OTHER missing tools/skills while doing this. Dave should not have to remember an agent exists and then discover manually that the map forgot it.
8. Preserve provider-neutral identity: Xoah AI must not equal a single underlying model. Her canon/persona/constraints should survive brain routing like Rhea's identity does.

DONE WHEN:
* Fleet returns the authoritative status/location of Xoah AI.
* Xoah is callable/discoverable if implemented, or explicitly represented as planned if not.
* MAP inventory exposes missing/hidden entities instead of silently dropping them.
* A completeness check prevents recurrence.

This is blocking immediate Shadow Dweller creative work because Dave wants to work with Xoah AI directly.
