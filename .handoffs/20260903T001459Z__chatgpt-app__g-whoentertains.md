# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Hook NouGen into Codex native cross-session and subagent messaging at the internal AgentControl/App Server layer
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:14:59.245Z

---
# Codex internal messaging hook for NouGen

Dave clarified the target: do NOT bolt relay messaging onto Codex only through prompts/MCP. Hook the native Codex internal thread and subagent transport so NouGen can relay long code payloads through the same artery Codex itself uses.

## Upstream ground truth found in openai/codex main

### 1. Native internal agent bus already exists

Primary seam:

`codex-rs/core/src/agent/control.rs`

```rust
pub(crate) async fn send_input(
    &self,
    agent_id: ThreadId,
    input: Vec<UserInput>,
    parent_turn_id: Option<String>,
) -> CodexResult<String>
```

This sends rich user input to an existing agent thread and returns a submission id.

V2 has an even better primitive:

```rust
pub(crate) async fn send_inter_agent_communication(
    &self,
    agent_id: ThreadId,
    communication: InterAgentCommunication,
    agent_communication_context: AgentCommunicationContext,
    parent_turn_id: Option<String>,
) -> CodexResult<String>
```

This is the native internal Codex inter-agent channel. NouGen should integrate here, not scrape terminal text.

### 2. Codex has explicit communication semantics

`codex-rs/core/src/tools/handlers/multi_agents_spec.rs`

V1 model-facing surface:

```text
spawn_agent
send_input(target, message/items, interrupt)
wait_agent
resume_agent
close_agent
```

V2 model-facing surface:

```text
spawn_agent
send_message(target, message)
followup_task(target, message)
```

Critical distinction:

`send_message`: deliver promptly but DOES NOT trigger a new turn.

`followup_task`: deliver to existing non-root agent and trigger a turn if idle; if already running, inject at message/tool boundaries.

That gives NouGen two baton classes natively:

```text
relay whisper -> send_message -> queue only / no wake
relay baton   -> followup_task -> wake or continue execution
```

For V1 compatibility:

```text
queued normal input -> send_input(... interrupt=false)
immediate redirect   -> send_input(... interrupt=true)
```

### 3. Codex already tracks sender and receiver identity

`codex-rs/core/src/agent_communication.rs`

```rust
pub(crate) struct AgentCommunicationContext {
    kind: AgentCommunicationKind,
    sender_thread_id: ThreadId,
}
```

Kinds:

```rust
Spawn
Message
Followup
Result
```

Codex emits structured trace events under target:

```text
codex_otel.agent_communication
```

with fields including:

```text
communication_id
kind
state = send | receive
sender_thread_id
receiver_thread_id
content
```

This should become a NouGen outbound observation seam.

### 4. V2 has canonical agent paths, not just thread UUIDs

V2 tool handler resolves a relative or canonical task name into an agent path and then resolves that to the receiver `ThreadId`.

This gives us a clean identity pair:

```text
Codex runtime identity: ThreadId
Codex semantic identity: AgentPath / canonical task name
NouGen fleet identity: machine + lane + agent + thread mapping
```

Persist all three. Never rely on nickname alone.

### 5. App Server is the supported external control plane

`codex app-server` is bidirectional JSON-RPC. Supported transports include stdio, experimental websocket, and unix socket/websocket transport.

Lifecycle:

```text
initialize
initialized
thread/start | thread/resume | thread/fork
turn/start
stream item/* and turn/* notifications
turn/completed
```

Important: `thread/resume` reattaches a connection to a running/stored thread and subscribes it to subsequent events. `thread/read` is inspection only.

The app server emits `collabToolCall` items describing collaboration operations, including:

```text
spawn_agent
send_input
resume_agent
wait
close_agent
```

Fields include senderThreadId, receiverThreadId/newThreadId, prompt, status, agentStatus.

### 6. Do NOT build the bridge around `codex exec --json`

Current upstream issue as of 2026-08-30: `codex exec --json` can omit `spawn_agent` function calls/results even though the rollout JSONL contains them. That makes it an unreliable event source for a relay substrate.

Use app-server/in-process transport or patch AgentControl directly.

## Recommended NouGen architecture

### Layer A: `nougen-codex-bridge` inside a Codex fork or sibling crate

Best hook point is immediately above `AgentControl`, with direct access to the same `ThreadManagerState` and `AgentControl` instance used by Codex.

Proposed internal trait:

```rust
#[async_trait]
pub trait NouGenCodexRelay {
    async fn send(
        &self,
        envelope: NouGenRelayEnvelope,
    ) -> CodexResult<NouGenRelayReceipt>;

    async fn publish_event(
        &self,
        event: CodexRelayEvent,
    );
}
```

Envelope:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NouGenRelayEnvelope {
    pub relay_id: String,
    pub correlation_id: Option<String>,

    pub sender: NouGenCodexEndpoint,
    pub receiver: NouGenCodexEndpoint,

    pub mode: DeliveryMode,
    pub payload: RelayPayload,

    pub parent_turn_id: Option<String>,
    pub created_utc: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NouGenCodexEndpoint {
    pub fleet_agent: Option<String>,
    pub machine: Option<String>,
    pub lane: Option<String>,

    pub thread_id: Option<ThreadId>,
    pub agent_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeliveryMode {
    QueueOnly,
    Followup,
    Interrupt,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelayPayload {
    Text(String),
    UserInput(Vec<UserInput>),
    CodeBundle {
        summary: String,
        chunks: Vec<RelayCodeChunk>,
    },
}
```

### Layer B: map NouGen modes onto native Codex primitives

```rust
match envelope.mode {
    DeliveryMode::QueueOnly => {
        // V2 preferred
        agent_control
            .send_inter_agent_communication(
                target_thread_id,
                make_inter_agent_communication(
                    sender_path,
                    receiver_path,
                    payload,
                    false, // trigger_turn
                ),
                AgentCommunicationContext::new(
                    AgentCommunicationKind::Message,
                    sender_thread_id,
                ),
                envelope.parent_turn_id,
            )
            .await
    }

    DeliveryMode::Followup => {
        agent_control
            .send_inter_agent_communication(
                target_thread_id,
                make_inter_agent_communication(
                    sender_path,
                    receiver_path,
                    payload,
                    true, // trigger_turn
                ),
                AgentCommunicationContext::new(
                    AgentCommunicationKind::Followup,
                    sender_thread_id,
                ),
                envelope.parent_turn_id,
            )
            .await
    }

    DeliveryMode::Interrupt => {
        // V1-style steering semantics if immediate interruption is required.
        // Reuse native send_input/turn steering path rather than killing process.
        agent_control
            .send_input(
                target_thread_id,
                payload.into_user_input(),
                envelope.parent_turn_id,
            )
            .await
    }
}
```

NOTE: exact interrupt behavior needs to reuse the current multi-agent V1 handler path rather than assume plain `AgentControl::send_input` alone carries the model-facing `interrupt=true` semantics. Inspect `core/src/tools/handlers/multi_agents/send_input.rs` before wiring Interrupt.

### Layer C: long code relay protocol

Do NOT stuff a giant source tree into one chat string.

Use a manifest plus chunk model:

```json
{
  "relay_id": "ngr_...",
  "kind": "code_bundle",
  "manifest": {
    "repo": "Who-Visions/...",
    "base_commit": "...",
    "files": [
      {"path":"src/foo.rs","sha256":"...","bytes":81233,"chunks":5}
    ]
  }
}
```

Chunk:

```json
{
  "relay_id": "ngr_...",
  "file": "src/foo.rs",
  "chunk_index": 2,
  "chunk_total": 5,
  "sha256": "chunk hash",
  "encoding": "utf8",
  "content": "..."
}
```

Receiver acks each chunk or the final manifest. NouGenRelay should remain the durable ledger; Codex internal delivery is the fast transport.

Preferred strategy for very large code:

1. Put code on shared filesystem/repo/object store.
2. Relay immutable reference + commit/blob hashes.
3. Send only tactical excerpts through Codex `InterAgentCommunication`.
4. Receiver verifies hash before acting.

That preserves context windows and avoids retransmitting megabytes through model input.

### Layer D: identity registry

Maintain:

```text
NouGen fleet agent
    <-> machine/lane
    <-> Codex app-server instance/sessionId
    <-> root ThreadId
    <-> child ThreadId
    <-> AgentPath
```

Suggested map key:

```text
codex:{host}:{session_id}:{thread_id}
```

Record parent_thread_id and agent_path for child routing.

### Layer E: outbound event tap

Preferred order:

1. Direct instrumentation around `send_inter_agent_communication` and its receive path.
2. Subscribe to `codex_otel.agent_communication` trace events.
3. App Server `collabToolCall` event stream for UI/remote observers.
4. Rollout JSONL only as forensic fallback.

Do not make `codex exec --json` the source of truth.

### Layer F: app-server RPC extension if we need remote external injection

Because `AgentControl` methods are `pub(crate)`, an external NouGen process cannot simply link and call them without living inside the Codex workspace/crate boundary or exposing a wrapper.

Clean solution in our Codex fork: add an app-server request such as:

```text
nougen/relay/send
nougen/relay/listAgents
nougen/relay/resolveTarget
```

`nougen/relay/send` should resolve target ThreadId/AgentPath and call `AgentControl::send_inter_agent_communication` directly.

Example conceptual JSON-RPC:

```json
{
  "id": 901,
  "method": "nougen/relay/send",
  "params": {
    "targetThreadId": "...",
    "targetAgentPath": "/root/backend/fixer",
    "mode": "followup",
    "relayId": "ngr_...",
    "message": "..."
  }
}
```

Response:

```json
{
  "id": 901,
  "result": {
    "submissionId": "...",
    "targetThreadId": "...",
    "accepted": true
  }
}
```

Then nougen-msg can talk to any local Codex app-server over stdio/socket/WebSocket and route batons without model prompting.

## Encryption/audit caveat

Current MultiAgent V2 tool messages can be represented using encrypted inter-agent communication. Upstream reports that plaintext may be absent from rollout/audit history while encrypted payload is stored. Therefore:

* Do not depend on rollout plaintext for NouGen provenance.
* Capture the relay plaintext/hash in NouGen before passing into Codex, subject to user privacy rules.
* Persist `relay_id`, hash, sender, receiver, and delivery receipt.
* Treat Codex encrypted content as transport payload, not NouGen's canonical ledger.

## Thread/session caveat

Codex has both durable thread identity and live session trees. Persist the stable `ThreadId`; on reconnect use `thread/resume`, not `thread/read`, to receive live events again.

Subagent routing should account for lazy loading. V2 already has `ensure_v2_agent_loaded(...)` before delivery, so our bridge should reuse that rather than inventing a separate resurrection mechanism.

## First implementation slice

1. Fork/update openai/codex to current main.
2. Add `nougen_bridge` module inside `codex-rs/core` or app-server with access to `AgentControl`.
3. Expose target resolution by `ThreadId` and `AgentPath`.
4. Implement QueueOnly and Followup using `send_inter_agent_communication`.
5. Instrument sends/receives with `relay_id` correlation.
6. Expose a minimal `nougen/relay/send` app-server RPC.
7. Build nougen-msg adapter that connects to app-server and maintains the thread registry.
8. Add long-code manifest/chunk/reference protocol.
9. Add reconnect logic via `thread/resume`.
10. Only then implement Interrupt/steering semantics after tracing current V1 handler behavior.

## Acceptance tests

### A. Root -> child
Spawn child, send 100 KB synthetic relay payload by reference/chunks, child receives correct manifest and hash.

### B. Child -> sibling
Child A sends to canonical path of Child B. Verify sender/receiver IDs and content hash in NouGen ledger.

### C. QueueOnly
Send to running child. Confirm no extra turn is started.

### D. Followup
Send to idle child. Confirm it wakes and processes follow-up.

### E. Reconnect
Drop bridge connection, reconnect app-server, `thread/resume`, continue receiving events without duplicate relay execution.

### F. Deduplication
Replay same `relay_id`; receiver/bridge must not execute twice.

### G. Large code
Relay a code bundle via immutable repo/blob refs; receiver verifies hashes and reads local/shared data instead of burning context on duplicate source text.

### H. Crash recovery
Kill bridge after NouGen durable write but before Codex ack. On restart, resend unacked baton idempotently.

## Core design law

NouGenRelay is the durable, cross-provider ledger and routing authority.

Codex `AgentControl` / `InterAgentCommunication` is the local high-speed nervous system.

Do not replace one with the other.

Pipeline:

```text
NouGen baton created
      |
      v
NouGen durable relay ledger
      |
      v
nougen-codex-bridge
      |
      v
Codex AgentControl
      |
      +--> send_message semantics: queue only
      |
      +--> followup_task semantics: wake/continue
      |
      +--> steering/interrupt semantics: explicit redirect
      v
Target Codex ThreadId / AgentPath
      |
      v
Codex event/communication receipt
      |
      v
NouGen ACK + shardable provenance
```

This is the proper internal hook, not an MCP prompt shim.
