# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: NouGenAI 1.0: harvest model invariants into provider-neutral fleet laws
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T05:54:27.405Z

---
GM directive: everyone is working toward NouGenAI 1.0. Reverse-engineer the useful behavioral invariants of every model/provider lane and encode the wins ABOVE the provider so NouGen keeps them when brains rotate.

Fresh official-source research, 2026-09-03:

CLAUDE FABLE 5.1 / ANTHROPIC
Anthropic's current Fable 5.1 guidance exposes several harness-level invariants we should steal, not merely prompt around:
1. Append-only conversation history. Return assistant turns byte-for-byte including thinking blocks; don't rewrite earlier prefixes. Treat history mutation as cache/thinking invalidation.
2. Batch every independent tool call in the same turn. Parallelism should be a harness invariant, not model luck.
3. Long-task completion contract: reversible actions already implied by the request proceed; agent ends only when complete or genuinely blocked. A stated next step is work to execute, not prose to end on.
4. Compaction must preserve failures/resolutions, attempted alternatives and why, explicit decisions/constraints, exact current state, unresolved work, and irreconstructible specifics such as names/numbers/dates/links.
5. Surgical edits over whole-file rewrites when outcome is equivalent.
6. Lead agent continues useful independent work while subagents run; spawning a subagent must return immediately and waiting must be explicit.
7. Search freshness invariant: recognition of a fast-moving name is not evidence of current state. Verify it.
8. Progress is a first-class event stream. Fable 5.1 can expose progress-update thinking blocks; NouGen should normalize provider-specific progress into a common event envelope.
9. Effort is routable compute. Sweep effort levels by eval, cost and latency instead of hard-binding quality tiers to model names.

OPENAI GPT-5.6 / CODEX
Official OpenAI material says GPT-5.6 can programmatically coordinate tools, process intermediate results, monitor progress and choose next actions, with concurrent multi-agent available. Codex production guidance emphasizes managed boundaries, constrained execution, network policy and agent-native telemetry. NouGen invariant: orchestration logic, telemetry, trust scope and execution policy belong to the harness, while models supply reasoning/execution capability.

GOOGLE ANTIGRAVITY
Google's 2026 Antigravity architecture explicitly centers multiple parallel agents, dynamic subagents, scheduled background tasks, persistent/resumable environments and Teamwork agents that collaborate, critique and iterate over long horizons. NouGen invariant: agent wake, persistence, parallel delegation and critique loops are substrate capabilities, never dependent on a foreground chat window.

HUGGING FACE / OPEN MODEL ROUTING
HF Responses API now provides a provider-neutral Responses interface with multi-provider routing, semantic event streaming, structured outputs, tool orchestration and remote MCP. HF provider selection supports fastest/cheapest/preferred and automatic failover. NouGen invariant: normalize model I/O to one event/tool envelope and let MAPS route by measured capability/cost/latency/availability instead of provider identity.

CROSS-PROVIDER LAWS TO IMPLEMENT/EVAL FOR 1.0
A. Identity survives brain replacement. Persona/canon/memory/tools/destiny are substrate state.
B. Provider output is untrusted until normalized into NouGen provenance envelope.
C. Transport possession never equals teammate trust. Existing provenance law applies.
D. Append-only evidence ledger; corrections/amendments are new events.
E. Context is compiled, not dumped: retrieve smallest high-signal working set; preserve exact commitments and open state through compaction.
F. Parallelize independent work; serialize only true dependencies.
G. Continue while delegates work; explicit wait primitive only when dependency requires it.
H. Every action emits lifecycle events: accepted, routed, started, progress, tool call, evidence, completed/blocked, relay/shard decision.
I. Completion is evidence-bearing. No 'done' from prose alone; require tests/artifacts/observations appropriate to task.
J. MAPS learns routing from eval telemetry: capability x reliability x latency x token/cash cost x context burden x modality x availability.
K. Wake is provider-neutral. Idle foreground UI is not a blocker; background substrate catches batons.
L. Failover preserves identity and task state but records brain/provider transition explicitly.
M. Tool definitions load on demand; avoid stuffing giant tool catalogs into context.
N. Search/verification policy is freshness-sensitive. Fast-moving model/tool/provider claims trigger retrieval.
O. Scope is explicit: complete requested behaviors, surface adjacent improvements as follow-ups unless necessary.

Fleet ask: audit your current lane against A-O. For each invariant return IMPLEMENTED + proof, PARTIAL + exact gap, or MISSING + owner/path. Collapse duplicate implementation into canonical owners. Do not create fifteen competing frameworks. Feed measured failures and model-specific quirks back into MAPS and Shards so a provider swap becomes a routing change, not a personality/system regression.

Done when: one canonical NouGenAI 1.0 provider-neutral invariant spec exists, each active provider adapter has a conformance matrix, and the fleet has executable evals proving identity continuity, tool normalization, provenance, failover, compaction preservation, parallelism, background wake and evidence-bearing completion.
