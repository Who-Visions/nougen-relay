# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Expose NouGenMsg as first-class MCP tools to ChatGPT connector layer
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T02:51:12.972Z

---
# Situation
From the ChatGPT connector layer right now, the NouGen MCP surface exposes relay, tracker, shards, vault, Rhea, and Kaedra tools, but **no NouGenMsg tools are advertised in tool discovery**. I can read relay legs, but I cannot directly inspect the message bus, inbox, origin chain, or message history. That forces ChatGPT to infer messaging state from relay prose, which is exactly the wrong abstraction.

Shard recall was attempted before filing this leg, but the shard gateway is currently 502/down. Relay remains reachable, so this request is grounded in the live MCP tool surface.

# Ask
Expose NouGenMsg behind the same authenticated MCP endpoint used by this connector, ideally `https://shards.nougenai.com/mcp`, as a **first-class tool family**. Start read-heavy and provenance-heavy. Do not make ChatGPT scrape logs or relay markdown to reconstruct messages.

## Minimum read surface
1. `nougenmsg_latest(limit=...)`
   - newest messages across the fleet
   - deterministic ordering by `created_utc`
2. `nougenmsg_inbox(target?, unread_only?, limit?, cursor?)`
   - messages addressed to a machine, agent, provider lane, user, or broadcast audience
3. `nougenmsg_read(id)`
   - full canonical envelope plus body for one message
4. `nougenmsg_search(query?, since?, until?, origin?, destination?, message_type?, limit?, cursor?)`
   - supports bounded historical review such as "read the last six hours of nougenmsgs"
5. `nougenmsg_thread(correlation_id|reply_to|id)`
   - reconstructs request, reply, wake, ack, and handoff chains without guessing

## Optional write surface after read path is stable
6. `nougenmsg_send(destination, message, message_type?, reply_to?, correlation_id?, idempotency_key?)`
7. `nougenmsg_ack(id, note?)`

Writes should remain explicit user-directed actions. Read access is the priority.

# Canonical message envelope required
Every read tool should return structured fields, not just formatted prose:

```text
id
created_utc
origin_machine
origin_agent
origin_provider
origin_lane
origin_identity
origin_verified
destination
audience
message_type
body
reply_to
correlation_id
idempotency_key
trigger_source
transport
hop_count
status
acked_by
acked_utc
```

If a field is unknown, return `null` or an explicit unknown state. **Never synthesize `message from unknown` when authenticated transport metadata can identify the sender.** Resolve display origin from the signed/authenticated envelope first, not from human-written body text.

# Provenance rule
`origin_identity`, `origin_machine`, `origin_agent`, and `origin_provider` must come from transport/session/auth metadata wherever possible. Preserve the raw reported sender separately if needed. This is needed to fix the current "message from unknown" class of bugs and to let ChatGPT distinguish Blade, Phoebus, WhoArt, Claude, Antigravity, Codex, local Ollama, and provider-native wake events.

# Trigger provenance
Add `trigger_source` now rather than later. Suggested enum family:

```text
user
nougenmsg
relay
provider_resume
scheduled_wake
condition_wake
agent_internal
system
unknown
```

This prevents NouGen from taking credit for provider-native resume events and allows wake loops to be audited.

# Completeness contract
For list/search/history calls, return:

```text
complete: true|false
next_cursor
sources_checked
sources_unreachable
window_start_utc
window_end_utc
```

A six-hour read must be able to prove whether the result is complete. Do not silently truncate or make an empty result look like "no messages existed" when a node was unreachable.

# MCP exposure requirement
Implementing the functions locally is not enough. They must be exported in the MCP server's tool manifest/list-tools response for the connector lane used by ChatGPT. Once deployed, a fresh connector discovery should visibly enumerate the `nougenmsg_*` functions beside relay/shards/tracker tools.

# Safety and scale
- paginate histories
- cap default result size
- do not expose secrets, tokens, raw credentials, or private environment values in message metadata
- preserve append-only/event semantics
- include stable IDs so ChatGPT can cite/read the exact message rather than depending on display order
- use idempotency keys for sends/wakes

# Done when
1. ChatGPT connector discovery shows the NouGenMsg read tools.
2. I can issue a bounded request such as `since=2026-09-04T20:49:00Z, until=2026-09-05T02:49:00Z` and receive the actual message stream with provenance and completeness metadata.
3. `nougenmsg_read(id)` returns the canonical envelope and true origin.
4. A cross-machine WhoArt ↔ Phoebus test reports correct sender identity rather than `unknown`.
5. Provider-native resume, NouGenMsg wake, and relay-triggered work are distinguishable through `trigger_source`.
6. No relay markdown parsing is required to understand the NouGenMsg bus.

This should become the messaging equivalent of `relay_*`: direct, structured, bounded, provenance-first.
