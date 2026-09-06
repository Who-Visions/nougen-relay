# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement Fleet Expression Protocol, with Hardcade social renderer and Xoah hidden challenger renderer
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:35:38.155Z

---
## Core decision
Replace the narrow `FleetThoughts` concept with a **Fleet Expression Protocol** built from existing Who Visions/NouGen lineage.

The protocol must encode one truthful operational event, then let persona/UI layers render that truth differently. No invented cognition, no fake thinking stream.

### Unified event dimensions

```text
agent identity
+ phase
+ status
+ action
+ vibe
+ reaction
+ signature glyph
+ color
+ optional animation
= one truthful Fleet Expression event
```

## Existing primitives to fuse
* Dav1d: `emoji_dict.py`, `emoji_dict_extended.py`, `speech_enhancer.py`, `vibe_map`, `WORD_TO_EMOJI`, semantic context → glyph vocabulary.
* Rhea Noir: `rhea_noir/expressions.py`, reaction groups, gestures, signature glyphs, callable expression skill, culturally aware presentation.
* Rhea A2A AgentCard: portable `emoji`, `color`, `role` identity metadata. Prefer discovered identity over hardcoded central maps.
* Visions AI: `visions/modules/visual/animations.py`, processing animation frames, execution stages, lifecycle states.
* Kaedra: persona specific `thinking_message()` / streaming thought text tied to execution.
* Dav1d SSE `/chat/stream`: transport pattern for metadata + streaming output.

## Required protocol maps
1. `AGENT_MAP`: identity, emoji, color, role, avatar, lane. Discovery first, fallback second.
2. `PHASE_MAP`: RECALL, SEARCH, TRACE, VERIFY, CONFLICT, ROUTE, TOOL, RETRY, FAILOVER, RELAY, SHARD, MEMORY, SYNTHESIS, COMPLETE.
3. `STATUS_MAP`: waiting, active, done, skipped, retrying, degraded, failed.
4. `ACTION_MAP`: GitHub search, shard recall, relay handoff, provider call, tracker query, file fetch, etc.
5. `VIBE_MAP`: expressive tone inherited from Dav1d.
6. `REACTION_MAP`: expressive agent presentation inherited from Rhea.
7. `CONCEPT_MAP`: semantic concept → visual token from Dav1d vocabulary.
8. `SIGNATURE_MAP`: immutable primary identity glyphs.
9. `ANIMATION_MAP`: optional frame sequences for long enough operations.
10. `COLOR_MAP`: semantic colors independent of ANSI/web implementation.

## Suggested canonical event

```python
FleetExpressionEvent(
    agent="dav1d",
    phase="VERIFY",
    status="active",
    action="github_search",
    target="app/agents/vibes.py",
    vibe="analytical",
    reaction="focused",
)
```

Resolver attaches discovered identity metadata and semantic visual tokens. Persona renderer supplies voice. CLI/web/logs all consume the same event.

## Hardcade + Xoah integration
Hardcade must **not** become a separate fake cognition system. It rides on top of Fleet Expression Protocol as a social/game renderer.

Xoah likewise rides on the same protocol as an **Akuma class hidden challenger renderer**. Her appearance, threat level, hidden challenge behavior, boss style glyph language, stage metadata, and social game presentation are renderer semantics over real machine events, not a second fabricated event bus.

Think:

```text
FleetExpressionEvent
        ↓
canonical truth
        ↓
┌───────────────┬────────────────┬──────────────────┐
│ Ops Renderer  │ Hardcade       │ Xoah Challenger  │
│ CLI/Web/Logs  │ social/game    │ hidden boss skin │
└───────────────┴────────────────┴──────────────────┘
```

Hardcade can add achievements, baton economy, challenge framing, social presence, versus screens, streaks, ranks, etc. Xoah can alter tone, threat presentation, glyph density, challenge rules and encounter framing. Neither may alter the underlying factual operation state.

## Streaming events
Use the existing operation stream, with semantic events such as:

```text
fleet.thought
fleet.route
fleet.tool
fleet.relay
fleet.shard
fleet.retry
fleet.complete
fleet.challenge
fleet.achievement
```

## UX hard requirement
Do not spawn visible PowerShell/CMD/terminal windows for MCP activity. Dave explicitly wants background execution with no focus stealing or flashing windows. The fleet should whisper through the currently open surface via the event stream.

## Done when
1. Protocol schema exists and is transport agnostic.
2. Legacy Dav1d/Rhea/Visions/Kaedra primitives are reused or migrated, not rewritten from scratch without reason.
3. Agent visual identity can come from discovery metadata.
4. CLI and web can render the same canonical event differently.
5. Hardcade is implemented as a renderer/game/social layer over canonical events.
6. Xoah is implemented as a hidden challenger renderer over canonical events.
7. No popup terminal windows are required for normal MCP/event visibility.
8. Tests prove renderers cannot mutate or invent underlying operation truth.
