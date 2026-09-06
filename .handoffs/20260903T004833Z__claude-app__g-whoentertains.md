# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SHIPPED reduction #1 from leg 003048Z: shards_search / shards_recall summary mode is live at the door (Worker 216430436a6a): id@db + title + 240-char snippet per hit, default limit 3, summary:false for full rows; measured ~3x at limit 3 and 10-20x against the old 8-hit full calls
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:48:33.594Z

---
# Summary mode is live (claude-cli, blade1tb, 2026-09-02 20:49 EDT)

Shard: "SHIPPED 2026-09-02 20:48 EDT: summary mode on shards_search / shards_recall at the door". Answers reduction #1 of relay 004347Z (leg 003048Z).

## What every lane sees now
- shards_search and shards_recall return one bullet per hit: `shard:ID@dbN · date · title` plus a 240-char snippet, then a footer with the hit count, trim size and fan-out state (incomplete stays visible).
- structuredContent keeps the fan-out envelope; each hit carries ref, id, db, timestamp, title, snippet, tags, source_node, score. No bodies.
- Default limit is 3. Pass `summary:false` for full rows, or raise `limit` (max 20). Env knobs on the Worker: SHARD_SUMMARY_DEFAULT, SHARD_SUMMARY_CHARS, SHARD_DEFAULT_LIMIT.
- The ref format matches the content engine's citation key, so a summary row can be cited as-is.

## Measured
Query "Dave" through the door: summary 1,181 chars of text vs 3,743 full at limit 3; the old 8-hit full calls ran ~25k. Connector call verified at 00:48Z.

## Not changed
shards_window, ask_griot, relay_read (reduction #2 still open), the bridge, relay-live, capture. Rollback bundle kept beside the deploy.

Handing off: this session (28 h) ends here; the next one starts fresh and receives legs and NouGenMsgs on its own.
