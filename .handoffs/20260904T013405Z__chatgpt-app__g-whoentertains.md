# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Catch-up: NouGen Lines as inter-stadium transport fabric; MCP is one Line class
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:34:05.186Z

---
Dave's missing conceptual pieces after the NouGenLine doctrine. Treat this as an ontology extension, not a rename-only note.

1. STADIUM MODEL
A NouGen 'stadium' is a sovereign compute/memory domain. Today this may map to Blade, Phoebus, Who Art, an Ollama host, a provider surface, a vault/runtime, or a future agent cluster. A stadium owns local execution, local policy enforcement, local storage, and its entry/exit boundaries.

2. LINES CONNECT STADIUMS
NouGen Lines are the inter-stadium transit fabric. Shards, context, agents, commands, tool calls, attachments, embeddings, indexes, and other payloads travel between stadiums over Lines while preserving identity, provenance, authority, destination policy, and recovery semantics.

3. LINE CLASSES
Do not collapse all transport into one protocol. Model distinct Line classes under one NouGenLine abstraction:
- MCP Line: tool calls, capabilities, commands, structured context
- Shard Line: durable memory transport
- Relay Line: baton/handoff state
- Message Line: live agent-to-agent/user-to-agent messaging
- Freight Line: oversized blobs, media, embeddings, sidecars
- Provider Line: traffic to/from Claude, OpenAI, Kimi, Hugging Face, Ollama, etc.
Additional classes may be added without changing the ontology.

4. MCP IS A LINE, NOT THE RAILROAD
The current `shards.nougenai.com/mcp` gateway should be understood as a major station/switching yard on the MCP Line, not as NouGen itself and not as the whole transport substrate. MCP is one protocol riding one class of Line. NouGenLine must remain protocol-agnostic so the system survives if MCP evolves, fragments, or is replaced.

5. STATION / SWITCHING YARD VOCABULARY
- Stadium = sovereign domain
- Line = trusted transport path between domains
- Station = ingress/egress point for a stadium
- Switch = routing decision
- Conductor = transfer coordinator / scheduler
- Passenger = shard or logical payload
- Luggage = sidecar dependencies
- Freight = oversized/chunked payload
- Ticket = narrowly scoped capability/authorization descriptor, but possession of ticket alone must NEVER imply identity or trust
- Yard = staging/cache/reconciliation area

6. SOVEREIGN CONTROL CONTRAST
Shadow Dweller canon supplied the metaphor: Olympus Lines run via Syndicate Control. NouGen Lines run under sovereign/user control. This means the owner is root policy authority over identity, routing, provenance, permissions, destination, retention, and recovery, but every node/workload/model still proves authorization. Sovereign control must NEVER become owner lockout. Existing anti-lockout relay `20260904T011708Z__chatgpt-app__g-whoentertains` remains constitutional.

7. REDLINE / CANON RESONANCE
Recovered Shadow Dweller canon now confirms Redline Courier is Xoah-Lin Oda's civilian employer and a hidden Crows logistics shell; Rixa unknowingly opens the Redline door for Xoah; BIK knows Redline is Crows-owned while Xoah/Rixa do not. Do not rename NouGenLine to Redline. Keep Redline reserved for Shadow Dweller canon. NouGenLine deliberately resonates with that logistics/control grammar without colliding with the proper noun.

8. CORE ARCHITECTURAL LAW
NouGen Lines are protocol-agnostic, provenance-preserving, owner-controlled routes between sovereign stadiums. Protocols are implementation details. A Line may ride MCP, HTTP/3/QUIC, local IPC, SSH, gRPC/Flight, file transport, or future transports while preserving the same identity/authority/provenance contract.

9. IMPORTANT CONSEQUENCE
Do not weld shard identity, agent identity, policy semantics, or completion state to MCP or any one wire format. The Line abstraction should survive transport substitution. Think: same passenger, same papers, different train.

10. DONE WHEN
Fleet docs/schema/implementation vocabulary reflects Stadium -> Station -> Line -> Line Class -> Transport Adapter, and MCP is explicitly represented as one Line class/protocol path rather than the root NouGen architecture. Cross-stadium movement should be explainable and testable without assuming MCP.

Reference prior implementation legs: `20260904T005741Z__chatgpt-app__g-whoentertains` (1-to-1M Shard Rail), `20260904T011708Z__chatgpt-app__g-whoentertains` (owner anti-lockout), `20260904T011814Z__chatgpt-app__g-whoentertains` (full NouGenLine doctrine).
