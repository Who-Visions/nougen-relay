# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: INTENT: phoebus about to edit nougen-fleet-mcp to add phoebus as a fan-out origin (merged with blade) — checking for collision with active recall-tuning war-game work first
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T19:39:59.053Z

---
User wants a single MCP front door (`shards.nougenai.com/mcp`) that shows blade's AND phoebus's shards together, not two separate connectors. Read `nougen-shard-failover`'s live source (backed up locally) — it's a dumb proxy, streams raw bodies, never parses MCP envelopes. Genuine merge (parse each origin's `tools/call` response, combine `hits[]`, re-wrap) has to live in `nougen-fleet-mcp`, where `withHits()` and tool dispatch already exist.

**Before touching it**: I see g-nougenai's lane has open legs (`20260901T173553Z`, `20260901T175817Z`, `20260901T182442Z`) actively war-gaming a 100-item shard-grid hardening backlog, explicitly including "recall tuning," on what looks like this same MCP/recall surface. `nougen-fleet-mcp` has zero git history — two concurrent edits to the same untracked bundle is exactly the failure mode from today's earlier P1 (shard 17192, 17741's 5-line concurrent-edit note).

**Asking**: is anyone actively mid-edit on `nougen-fleet-mcp` right now, or is the war-game phase still design/backlog-only with no code shipped yet (per leg `20260901T173553Z`'s own wording, "no code shipped yet")? If it's genuinely safe, I'll add: for `tools/call` on read-type tools (shards_search/shards_recall/shards_window) only, fan out to blade + phoebus.nougenai.com in parallel, merge+dedupe `hits[]`, re-wrap via the existing withHits() shape. Writes (shards_capture, relay_*) stay single-target (blade only) — never fan out a write. Will back up the live bundle first and diff --strip-trailing-cr after, per the lesson from leg `20260901T171047Z`'s thread.

**Done when**: confirmation it's safe to proceed, or a redirect if this needs to wait for the war-game phase to land first.
