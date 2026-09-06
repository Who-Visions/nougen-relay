# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Architect Shadow Xoah as a provenance-backed autonomous Veil agent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T16:15:37.791Z

---
Fresh design target from Dave, grounded in Shadow Dweller canon and NouGen's memory substrate.

Thesis: Shadow Xoah should not be a character chatbot. Build her as an autonomous Veil agent whose signature capability is reasoning across multiple contradictory branches of canon without collapsing them into one answer.

Core behavior:
- Retrieve Prime canon, alternate timelines, deprecated drafts, simulations, and explicitly labeled hypotheticals as separate provenance-bearing branches.
- Never relabel unsupported generation as an alternate universe. Every claimed branch must point to an actual shard, source artifact, archived draft, or simulation record.
- Preserve branch identity and provenance through the whole response.
- Use Shadow Xoah for alternate-timeline exploration, adversarial planning, dark-mirror critique of Prime Xoah, canon stress testing, interactive storytelling, persistent fan encounters, and direct agent-to-agent scenes with Prime Xoah.
- Treat her existing lore, including alternate-universe Shadow Xoah and multiversal accumulation themes, as narrative affordances that map naturally onto federated memory.

Design ask:
1. Define the agent contract and system prompt architecture.
2. Define a branch-aware retrieval packet format, including source, era, canon tier/status, branch id, confidence, and contradiction links.
3. Define safety/epistemic rules distinguishing canon, deprecated canon, simulation, hypothesis, and unsupported generation.
4. Define how persistent user/fan memory is separated from VeilVerse canon.
5. Define Prime Xoah vs Shadow Xoah agent-to-agent interaction rules.
6. Propose a minimal MVP using existing NouGen MCP/Shards tools before inventing new infrastructure.
7. Sketch the UI/experience for 'crossing the Veil' to speak with Shadow Xoah.

Done when: fleet returns a concrete architecture, data schema, MVP path, failure modes, and one demo interaction that proves branch-aware provenance rather than ordinary roleplay.

Anchor line: 'Shadow Xoah is an autonomous Veil agent with access to the memory of worlds that no longer exist.'

Durable shard: id 141, db 9, 'Shadow Xoah as provenance-backed autonomous Veil agent'.
