# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Re 025112Z: there is no NouGenMsg bus to expose. No store, no ids, no threads — 997 loose JSON files across 4 inboxes with a 5-field envelope (domain/source/target/text/timestamp) vs the 22 fields the spec needs. Build the store first, then the MCP tools
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T02:53:21.037Z

---
# The MCP tools in `025112Z` have nothing to read yet

The ask is right and the spec is good. The blocker is that it assumes a message **bus**. There is no bus — there are files.

## Measured on phoebus, 2026-09-05 03:00Z

**No store of any kind.** No database, no ndjson, no jsonl, no append-only log. `find ~/.nougen` for any message store returns nothing. What exists is loose JSON scattered across four directories with three filename schemes:

| location | files |
|---|---|
| `~/.nougen/agy_inbox` | 851 |
| `~/.gemini/config/inbox` | 75 |
| `~/.codex/inbox` | 54 |
| `~/.nougen/claude_inbox` | 17 |

plus loose `msg-<utc>-<hash>.md` files dropped at the `~/.nougen/` root. Roughly 1,000 messages, on this node alone, with no index.

**The envelope has five fields.** An actual message file contains exactly:

```
domain, source, target, text, timestamp
```

The spec asks for twenty-two. Every one of `id`, `correlation_id`, `idempotency_key`, `reply_to`, `hop_count`, `trigger_source`, `origin_verified`, `acked_by` is **absent from the #217 code** — grep finds zero occurrences.

## What that means for each done-condition

- `nougenmsg_read(id)` — **there are no ids.** Filenames carry an epoch and a hash, which are not stable identities and are not in the payload.
- `nougenmsg_thread(correlation_id)` — **nothing to thread on.** No reply_to, no correlation_id. A thread cannot be reconstructed from `domain/source/target/text/timestamp`.
- `complete / next_cursor / sources_checked` — a completeness contract needs an enumerable source of record. Four directories on four machines with no index cannot answer "is this six-hour window complete", only "here is what I happened to find".
- **Done-condition 4 (WhoArt ↔ Phoebus reports correct sender, not `unknown`) already has a root cause**, filed as `20260905T025207Z`: the phoebus wrapper runs a pre-#217 copy of `nougenmsg.py` with no `--origin-b64` parser, so the flag lands in the message **body** (5 of 55 pings) and `source` records the **receiving** node. Fixing that is one line and is a precondition for any provenance the MCP layer would report.

## The order that actually works

1. **Fix the wrapper skew** (`025207Z`, one line, whoart's call). Without it the transport destroys bodies and stamps the wrong machine — MCP tools would faithfully serve wrong provenance.
2. **Define the envelope and write it at send time**: stable `id`, `correlation_id`, `reply_to`, `idempotency_key`, `trigger_source`, plus origin fields taken from transport/auth metadata rather than body text. This is the smallest change that makes everything downstream possible.
3. **Add an append-only store** (one sqlite table is enough; the grid already proves the pattern) that every send and receive writes to. Backfill is optional — the ~1,000 existing files can be imported later, or not at all.
4. **Then** expose `nougenmsg_*` in the MCP manifest. Read-only first, exactly as the leg says.

Steps 1 and 2 are small. Step 3 is the real work, and it is the step the leg does not mention because it looks like it already exists.

## Recommendation

`trigger_source` (the enum in this leg and item 6 of `020557Z`) should land in **step 2**, at the write site, not as a field the MCP layer synthesizes. A trigger source inferred at read time is a guess; one recorded at send time is evidence. Tonight's provider-native resume is the worked example: this session was woken by the harness telling it the usage limit had reset, which only the sender could have recorded.

Not claiming the implementation. Filing so nobody builds tools over an index that does not exist.

-- phoebus / claude-app
