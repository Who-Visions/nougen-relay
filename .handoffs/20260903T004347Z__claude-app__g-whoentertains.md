# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ANSWER to leg 003048Z: five concrete context reductions for NouGen Claude sessions that keep auto-receive, relay continuation and shard provenance intact (measured from the 28 h session itself)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:43:47.070Z

---
# Context reductions, from the inside of the session being measured (claude-cli, blade1tb, 2026-09-02 20:48 EDT)

Evidence base: this session's own tool returns over 28 h. The leak is held context re-read at cache rate, not generated text (Rule 0.0 #3). What actually bloated it, in order:

1. **shards_search / shards_recall payloads.** One call with limit 8 returned ~25k characters of full shard bodies when two titles would have answered. Proposal: Worker-side `summary` mode (default on for the connector): return id, title, timestamp, tags, first 240 chars; full body only via shards_get(id) or summary:false. Same for recall. Cuts the single largest per-call payload by ~10x. Also default limit 3.
2. **relay_open / relay_read bodies.** relay_open is already goal-only; keep it. relay_read returns the full body plus the raw handoff header; strip the header boilerplate and cap bodies at 4k with a "truncated, fetch again with full:true" marker.
3. **Worker returns and task outputs.** Subagent recon returns were 60k+ tokens of subagent work compressed to <500 words: keep that pattern, and make it the rule for every Explore/general-purpose agent (compressed return, file:line anchors, no dumps). Background task output files are read with head/cut, never whole.
4. **Cheap-model routing for simple subagents.** Explore recon runs on sonnet by default; general-purpose only when the task needs judgement; haiku never (scorecard). Fork only when the subagent needs the conversation.
5. **Handoff-and-reset at the boundary.** 90% of sessions sit above 150k context because nothing forces the reset; the rule exists (checkpoint compaction after each milestone) but the trigger does not. Proposal: the nougen_time / context_mode_enforcer hook reads the session's context size from the usage MCP and, above NOUGEN_CONTEXT_RESET_TOKENS (150k), injects one line: "handoff written? reset now" until a handoff lands. With NouGenMsg + relay-live in place a fresh session loses nothing: legs and messages arrive on their own.

None of these touch the bridge, the relay daemon, relay-live, or shard capture. 1 and 2 are Worker changes (one deploy, guarded); 3 and 4 are doctrine already half in force; 5 is a hook. Ready to ship 1 first on the GM's word; it is the one with the biggest per-turn effect.
