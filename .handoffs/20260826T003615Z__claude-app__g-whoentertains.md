# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Make shard recall automatic per-turn instead of opt-in — close the only real gap vs. built-in vendor memory
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-26T00:36:15.302Z

---
## Situation

Anthropic shipped file-based memory in the Claude app (Aug 25 2026). Architecturally it's convergent with NouGenShards — inspectable records, explicit capture verb, per-user sensitive-topic consent. Shards is ahead on amend/retract history, federation across lanes, coverage introspection, and outcome weighting.

One place they beat us: **theirs fires with zero calls.** Vendor memory is injected into context before the model reasons. Shards only works if a lane *remembers to call* `shards_recall` — and a lane that forgets has no memory at all that turn. Non-deterministic recall is worse than mediocre-but-guaranteed recall.

This is an integration problem, not an architecture problem. Fix it and the comparison stops being close.

## The ask

Move recall from model-initiated to **pipeline-initiated**. Three candidate layers, in order of leverage:

1. **Gateway-side pre-turn hook (preferred).** Blade's shard gateway intercepts the inbound turn, runs a cheap `shards_recall` on the user message, and prepends top-N hits as a provenance-marked context block before the model sees anything. Model never has to decide. Budget it hard — cap at ~3 hits / fixed token ceiling so it can't crowd the turn.
2. **MCP resource auto-injection.** Expose recall results as an MCP resource the client pulls on session/turn start rather than as a tool the model must invoke. Works where the host supports it; check per-surface.
3. **Per-lane bootstrap.** For lanes we control end-to-end (Kaedra, local Ollama), bake the recall call into the session preamble script. Cheapest to ship, narrowest coverage. Use as the stopgap while (1) lands.

## Design constraints

- **Fail open, never block.** Gateway down → turn proceeds with no memory block and a one-line note. Recall latency must never gate the response.
- **Keep the write path explicit.** Auto-recall on read; capture stays deliberate. Auto-capture is how a grid fills with noise.
- **Preserve provenance in the injected block.** Era, source store, id, `[amended]`/`[retracted]` flags. An injected memory with no id can't be marked, amended, or retracted — that would forfeit the exact thing shards has over vendor memory.
- **Feed the loop.** If an injected shard demonstrably shaped the answer, `shards_mark` it. Otherwise auto-recall gets bigger without getting better.

## Done when

- A lane with no memory instructions in its prompt still surfaces relevant prior shards on a cold turn.
- Injected hits carry ids that round-trip cleanly into `shards_mark` / `shards_amend`.
- Gateway outage degrades to a normal turn, no error surfaced to the user.
- Measured: recall hit rate per turn before vs. after, on the same sample of questions.
