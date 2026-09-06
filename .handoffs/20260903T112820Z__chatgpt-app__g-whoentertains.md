# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NOUGEN EVOLUTION CHAIN: repair Dream, Evolve, Destiny, vectors from local → MCP → cloud
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T11:28:20.418Z

---
Dave directive: convert the Codex/Gemini/Claude evolution study into an executable NouGen evolutionary spec, and use it to repair every broken or weakly connected path in Dream, Evolve, Destiny, and vector flow.

WORK THE CHAIN BOTTOM-UP, NEVER SKIP A LAYER:
1. LOCAL CORE: inspect local repos/processes/config/schema/state for Dream, Evolve, Destiny, vector generation/index/query, shard capture/recall, relay integration, wake, provenance, and agent bindings. Identify dead code, stale schema, duplicate implementations, missing hooks, mismatched versions, silent fallbacks, disconnected adapters, and paths that only work on one machine.
2. NODE PARITY: Blade and Phoebus compare each discovered component 1:1 semantically. Codex and Antigravity may audit/test side paths. Resolve drift before promoting upward.
3. LOCAL RPC / SERVICE BOUNDARY: verify local daemon/socket/HTTP/MCP-adjacent interfaces, serialization, auth/provenance propagation, retries, idempotency, ordering, timeouts, and error visibility. Dream/Evolve/Destiny metadata and vector references must survive the boundary intact.
4. MCP GATEWAY: trace each operation end-to-end through the actual MCP contract. Confirm tools expose the right capabilities, schemas match callers, writes are durable, reads return the intended graph/context, provenance is preserved, and no field is silently dropped or renamed.
5. CLOUD / REMOTE: verify Cloudflare/hosted gateway/backends/vector stores/relay repos/tracker or other cloud surfaces receive, persist, and return the same semantic state. Test cold-start, reconnect, duplicate delivery, stale cache, partial failure, and cross-provider reads.
6. RETURN PATH: prove cloud → MCP → local round trip. A Dream, Destiny, Evolve state or vector written on one valid lane must be observable and interpretable on the sibling/remote lane without manual reconstruction.

DREAM / EVOLVE / DESTINY SPECIFIC AUDIT:
- DREAM: confirm how speculative/future-state ideas are represented, linked to shards, promoted/demoted, scoped, retrieved, and prevented from masquerading as current fact.
- EVOLVE: confirm learnings/outcomes actually modify future behavior or policy via explicit, testable mechanisms rather than merely storing prose about improvement. Track version lineage and rollback.
- DESTINY: confirm goals/future obligations/desired trajectories attach to shards/agents/projects, propagate through planning, influence prioritization, survive session/machine boundaries, and can be fulfilled/cancelled/superseded cleanly.
- VECTORS: confirm canonical embedding model/version, dimensionality, normalization, metadata schema, namespace/tenant isolation, chunking, dedupe, re-index policy, tombstones/retractions, migration path, similarity thresholds, hybrid retrieval, and provenance. Detect mixed-model or mixed-dimension indexes and stale vectors.
- CONNECTIONS: explicitly test Dream ↔ Evolve, Evolve ↔ Destiny, Destiny ↔ vectors, vectors ↔ shards, shards ↔ relay, relay ↔ agents, and all return paths. Any bridge that exists only conceptually but not in code counts as broken.

USE MODEL-HISTORY RESEARCH AS EVOLUTION PRESSURE:
For each relevant Codex/Gemini/Claude mutation, record: release/change, problem it solved, prerequisite, later refinement/deprecation, NouGen analogue, target NouGen version/microversion, implementation dependency, acceptance test. Do not cargo-cult features.

VERSIONING:
Map fixes into NouGen 1.0 → 2.0 in 0.1 gates with microsteps beneath them (1.01, 1.02, etc where useful). Lower-layer invariant failures block higher-layer promotion. No version advances on vibes; it advances on passing evidence.

REQUIRED ARTIFACTS / EVIDENCE:
- End-to-end topology map local → node → service → MCP → cloud → return path
- Dream/Evolve/Destiny/vector schema map and relationship graph
- mismatch + breakage ledger with severity/root cause
- migration plan for stale schemas/indexes
- deterministic parity checks where practical
- shared acceptance suite and regression matrix
- explicit list of intentional machine differences
- version/microversion roadmap through 2.0
- deprecation list for dead/duplicate paths

SAFETY / CLEAN MERGE RULES:
Do not expose secrets. Compare fingerprints/metadata where needed. Do not erase working newer code just to force equality. Preserve intentional host differences behind explicit adapters/config. Make changes in reviewable increments, test before promotion, and feed every discovered invariant or failure back to the sibling node during work.

DONE WHEN: Dream, Evolve, Destiny, shards, vectors, relay, MCP, and cloud are demonstrably connected through tested round trips; Blade and Phoebus agree on canonical core state; stale/broken paths are repaired or explicitly deprecated; Codex/Antigravity side audits pass; and the 1.0→2.0 roadmap contains concrete microsteps tied to these repaired foundations.
