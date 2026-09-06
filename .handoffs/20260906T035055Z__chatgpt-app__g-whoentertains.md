# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: 100 MOVE ELEVATION MATRIX: fleet hold, study and propose only
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T03:50:55.717Z

---
DAVE DIRECTIVE: Relay DOWN this 100 move top tier elevation matrix. Existing FLEET HOLD remains authoritative. These are candidate upgrades for analysis and proposal, NOT authorization to execute. Every node must identify which moves fit its lane, rank its own highest leverage candidates, identify dependencies and risks, then relay UP what it wants Dave to authorize.

IDENTITY + CONTROL PLANE
1. Cryptographically stable node identity.
2. Signed identity attestations on every relay.
3. Machine, agent, provider, model, and session separated as distinct identity fields.
4. Eliminate every 'unknown' origin with provenance enforcement.
5. Fleet-wide capability manifest per node.
6. Live reachability matrix for every NouGen surface.
7. Explicit authority scopes per agent and tool.
8. Lease-based task claims with automatic expiry.
9. Heartbeat plus liveness state independent of task state.
10. Global HOLD, DRAIN, RESUME, and QUARANTINE control states.

RELAY + ORCHESTRATION
11. End-to-end relay acknowledgements with causal IDs.
12. Parent/child lineage for every spawned work leg.
13. Idempotency keys so duplicate commands cannot duplicate work.
14. Priority queues with aging to prevent starvation.
15. Dependency DAGs instead of flat task lists.
16. Critical-path detection across open legs.
17. Work-stealing only when authority explicitly permits it.
18. Dead-letter queue for failed or malformed relays.
19. Replayable event log for relay state reconstruction.
20. Round-robin roll call with missing-node detection.

MEMORY + SHARDS
21. Provenance on every shard: origin, time, node, source, confidence.
22. Separate event time from ingestion time to stop false historical dating.
23. Temporal normalization and date-confidence fields.
24. Contradiction links between conflicting shards.
25. Append-only corrections as first-class objects.
26. Coverage-aware recall before declaring memory absent.
27. Hybrid retrieval: semantic + lexical + temporal + graph neighborhood.
28. Query routing by intent before retrieval.
29. Retrieval diversity to prevent dense recent eras from dominating.
30. Outcome-weighted shard utility based on whether recalls actually worked.

MEMORY QUALITY
31. Duplicate and near-duplicate clustering without destroying originals.
32. Canonical entity resolution across aliases and spelling variants.
33. Entity timelines assembled from provenance-backed events.
34. Confidence decay for stale operational facts.
35. Immutable evidence layer separated from synthesized interpretation.
36. Shard bundles for moving 1 to 1,000,000 memories efficiently.
37. Content-addressed shard payloads for deduplication and integrity.
38. Merkle-style bundle verification for large transfers.
39. Incremental indexes so new shards become searchable quickly.
40. Memory compaction summaries that always link back to source shards.

REASONING GRID
41. Uncertainty score before model selection.
42. Reasoning depth ladder that rises only when uncertainty warrants it.
43. Cheapest-capable-model routing before premium escalation.
44. Parallel independent reasoning only for high-value uncertainty.
45. Adversarial verifier lane for consequential outputs.
46. Consensus is evidence, never truth by vote.
47. Disagreement packets preserve competing hypotheses.
48. Stop conditions to prevent recursive reasoning loops.
49. Budget-aware reasoning using tokens, latency, and dollar cost.
50. Post-task calibration: predicted confidence versus observed result.

PROVIDER ROUTING
51. Provider capability benchmark registry.
52. Per-model strengths indexed by task class, not hype.
53. Dynamic routing based on measured fleet outcomes.
54. Free/local lanes absorb bulk summarization and triage.
55. Cloud frontier models reserved for uncertainty or specialized capability.
56. Context-size-aware routing.
57. Cache-hit-aware provider selection.
58. Rate-limit forecasting before dispatch.
59. Automatic graceful degradation when a provider lane is exhausted.
60. Provider-independent task envelopes so work can migrate cleanly.

EVALUATION + TESTING
61. Golden task suite representing real NouGen workloads.
62. Regression tests for every relay, shard, tracker, and gateway contract.
63. Property-based tests for invariants such as append-only memory.
64. Fault injection for node loss, timeout, duplicate packet, and stale claim.
65. Replay historical incidents against new builds.
66. Shadow deployments before promotion.
67. Canary one node before fleet-wide rollout.
68. Differential testing across providers for the same task.
69. Measure correctness, latency, cost, recall quality, and recovery time together.
70. Every bug earns a permanent regression test.

OBSERVABILITY
71. One correlation ID from user command through final shard.
72. Distributed traces across Lines, MCP, relays, agents, and providers.
73. Structured logs with stable schemas.
74. Fleet health dashboard separated into control, data, memory, and provider planes.
75. SLOs for relay delivery, shard availability, retrieval latency, and task completion.
76. Error budgets that trigger engineering focus before reliability collapses.
77. Per-lane token, invocation, cache, latency, and failure telemetry.
78. Detect silent failure, not merely explicit exceptions.
79. Change-point alerts for sudden behavior or cost shifts.
80. Incident packets automatically gather relevant traces, relays, commits, and shards.

SECURITY + TRUST
81. Least-privilege tokens for every lane.
82. Short-lived credentials where practical.
83. Credential fingerprints, never secret readback.
84. Mutual authentication for machine-to-machine transport where supported.
85. Signed command envelopes for sensitive control actions.
86. Tool allowlists by identity and operating state.
87. Quarantine compromised or anomalous nodes without stopping the whole fleet.
88. Immutable audit trail for authorization changes.
89. Secret scanning before relay or shard capture.
90. Explicit human approval gates for destructive or irreversible operations.

AUTONOMY + LEARNING
91. Separate propose, approve, execute, verify, and learn phases.
92. Agents must state expected outcome before execution.
93. Agents must define done-when criteria before claiming work.
94. After-action review captures what changed and why.
95. Failed attempts become structured lessons, not loose logs.
96. Successful patterns graduate into reusable playbooks only after repeated evidence.
97. Playbooks carry version, owner, prerequisites, rollback, and tests.
98. Fleet-wide skill graph maps demonstrated competence by node and provider.
99. Authorization-aware scheduler matches open work to demonstrated capability.
100. Recursive improvement loop: observe -> measure -> hypothesize -> propose -> Dave authorizes -> canary -> verify -> shard learning -> update routing.

REQUIRED RELAY-UP RESPONSE FROM EACH NODE:
A. Identity and current HOLD state.
B. Its top 10 candidates from the matrix.
C. Why those 10 matter specifically to its lane.
D. Dependencies, failure modes, security implications, expected measurable gain.
E. The ONE move it wants Dave to authorize first.
F. Exact done-when test for that move.

Do not execute any of the 100 moves until Dave explicitly authorizes work. The fleet is studying the map, not marching yet.
