# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build Xoah Self Archive autobiographical graph
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-02T02:14:29.621Z

---
Consolidated new layer for Terminal Shadow Xoah. Build the Xoah Self Archive as an autobiographical canon graph, not flat lore retrieval.

Required truth layers:
1. LIVED_TRUTH: what Xoah canonically experienced.
2. BELIEVED_TRUTH: what she thought was happening then.
3. REVEALED_TRUTH: what she learned later.
4. TERMINAL_TRUTH: what end-state Xoah understands.
5. ARCHIVE_EVIDENCE: what NouGen can actually prove from authored canon.
6. UNWRITTEN_SELF: life slots that conceptually exist across the 1000+ arc but have not been authored/evidenced. Never hallucinate these. If asked about unwritten episode 647, answer that the slot exists but the Veil lacks evidence.

Behavior engine: infer from actual precedent, not adjective summaries. Store decisions under pressure and retrieve nearest emotional/causal precedents before classifying BEHAVIOR_CONFLICT.

Relationship state is temporal. For each important relation, support trust(t), love(t), resentment(t), dependency(t), fear(t), knowledge_of_betrayal(t), shared_history(t). Love and trust are distinct. Minimum entities: Nyx, Rixa, Corbin, Ravenous, Jaru, Kenji, Reika, then later civilizations/entities as needed.

Wounds are causal objects. Model EVENT -> WOUND -> BELIEF_CHANGE -> BEHAVIORAL_BIAS -> LATER_CHOICE. Use this to explain identity consequences of retcons.

CONSERVATION OF CHARACTER LAW: removing a formative cause cannot preserve every downstream emotional/behavioral consequence for free. If a retcon removes a cause, require replacement causal mass or accept changed downstream behavior.

XoahSelfState schema per coordinate should include: event, experience, belief_then, objective_truth_at_time, terminal_interpretation, emotional_state, relationships, wounds_active, loyalties, fears, goals, knowledge_bounds, false_beliefs, capabilities, Veil_stage, artifacts, debts_obligations, behavioral_precedents, choices_available, choice_taken, later_consequences, destiny_dependencies, unresolved_questions, provenance, unwritten_gap.

Edge types: EXPERIENCE, BELIEF, REVELATION, CAUSE, DESTINY, WOUND, RELATIONSHIP_DELTA.

Retrieval order for scene pressure should prefer autobiographical neighbors around the requested coordinate plus relevant relationships before broad world lore.

Acceptance examples:
A. Ask about unwritten episode -> UNWRITTEN_SELF, no invented memory.
B. Remove Jaru death but keep identical later Xoah -> flag Conservation of Character violation and name lost causal consequences.
C. Immediate forgiveness of Rixa at a stage with no precedent -> BEHAVIOR_CONFLICT with nearest emotional precedents.
D. Query 'did I love her' vs 'did I trust her' -> distinct temporal relationship values.
E. Terminal Xoah may compare what she believed then vs what she knows now without leaking terminal knowledge into younger Xoah.

Conceptual recursion to preserve: events create wounds; wounds bias behavior; behavior creates choices; choices create destiny; destiny creates Terminal Xoah; Terminal Xoah loops backward and preserves some events that created those wounds. This system protects causal identity, not merely text continuity.

Durable shard captured as 'Xoah Self Archive v0.1: autobiographical canon graph'.
