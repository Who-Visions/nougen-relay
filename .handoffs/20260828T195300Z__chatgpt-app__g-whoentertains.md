# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Ingest full Claude Code creator playbook into NouGen runner architecture
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T19:53:00.429Z

---
Source: Boris, Anthropic MTS and creator of Claude Code. Preserve source-backed mechanics and distinguish NouGen extrapolations.

SOURCE-BACKED CLAUDE CODE PRACTICES
1. Claude Code is terminal-native and fully agentic, intended for whole features, functions, files, bugs, and shell workflows rather than line completion.
2. It is environment-agnostic across local terminals, remote SSH, tmux, VS Code, JetBrains, Vim, etc.
3. Recommended onboarding starts with codebase Q&A before edits. Claude explores code directly, without a remote code index. Anthropic claims internal technical onboarding dropped from 2–3 weeks to 2–3 days, but this is internal anecdotal evidence, not an externally validated benchmark.
4. Deep code archaeology uses repository structure, git history, commits, linked GitHub issues, and web resources to explain why code exists and what shipped.
5. For large changes, use plan-first behavior: brainstorm, make a plan, run it by the operator, then write code.
6. Give the agent feedback tools such as unit tests, integration tests, Puppeteer, simulator screenshots, or other observable outputs. With feedback, the agent can autonomously iterate 2–3 cycles and materially improve results.
7. Tool usage should be compact and composable: edit files, run shell commands, search files, batch tools, MCP tools. The model strings them together without needing a rigid hand-authored sequence.
8. Shared project context via CLAUDE.md should stay concise and contain core commands, architecture constraints, style, important files, MCP instructions. CLAUDE.local.md is personal. Nested CLAUDE.md files load on demand by directory. Enterprise context/policy can apply globally.
9. Context/config/permissions form a hierarchy: enterprise, global/user, project, local/project-personal, nested-directory/task.
10. Permissions can auto-approve safe commands and block dangerous commands/endpoints at higher policy layers. Anthropic specifically notes bash safety as one of the hardest implementation problems; their approach includes read-only classification, static analysis of command combinations, and complex tiered allow/block policies.
11. Project-shared context creates a network effect: one person configures useful commands/tools once and the team benefits.
12. Memory tooling exposes which memory files are loaded and allows specific memories to be edited or written.
13. Terminal ergonomics include auto-accept edits, explicit memory writes, direct shell injection into context, interruption/history controls, resume/continue, and full output inspection.
14. Claude Code is multimodal despite being terminal-native. Images can be supplied via drag/drop, file path, or paste and used in build/iterate loops.
15. Headless/SDK mode (`claude -p`) turns the agent into a scriptable Unix-like primitive: prompt in, JSON or streaming JSON out. Anthropic says they use this in CI, incident response, pipelines, log analysis, issue labeling, and structured automation.
16. Advanced power users often run many sessions in parallel using SSH, tmux, multiple repo checkouts, and git worktrees for isolation.
17. The CLI was chosen partly because terminals are the universal denominator across environments. Boris's prediction that traditional IDEs may fade quickly is speculative, not a requirement for NouGen.
18. Non-containerized agentic shell execution remains inherently risky despite static analysis and permission controls.

NOUGEN ARCHITECTURE MAPPINGS
A. Fresh-runner orientation before mutation
Before any runner edits shared code or state, assemble orientation from repo architecture, git history, issues, examples, recent changes, current relay, active claims, relevant shards, and local subsystem instructions. A fresh runner should understand the field before carrying the ball.

B. Hierarchical context instead of context dumping
Canonical target hierarchy:
Fleet canon -> operator memory -> organization memory -> project memory -> subsystem/directory memory -> current relay/claims -> task evidence.
Keep always-loaded context tiny. Fetch deeper context on demand based on task, path, entity, time, and uncertainty. Do not dump the entire shard grid into every runner.

C. Permission topology by consequence, not merely by tool name
Suggested semantic tiers:
GREEN: inspect, search, recall, diff, test, calculate, summarize, read-only telemetry. Auto-run.
YELLOW: reversible local edits, branch/worktree creation, prototypes, generated tests/HUDs, temporary artifacts. Auto-run under policy with audit trail.
ORANGE: shared config changes, deployments, service restarts, meaningful compute spend, secret rotation, shared DB/schema mutation. Require stronger policy checks or GM approval depending on scope.
RED: destructive/irreversible actions, permission expansion, deleting durable state, externally consequential communication, production-wide changes, high-risk credentials/actions. Explicit GM approval.
The key principle is action semantics and blast radius, not "bash yes/no".

D. Closed-loop autonomy / Zigzagging
Agent loop should be:
ACT -> OBSERVE -> COMPARE -> CORRECT -> VERIFY -> RELAY.
Without a way to perceive results, autonomy is blind. Tests, screenshots, telemetry, diffs, logs, simulators, browser state, and health checks are sensory channels. Zigzagging should choose the next move from observed progress rather than blindly continuing the original plan.

E. Headless runners as interchangeable execution primitives
Treat cloud and local agents as callable execution functions rather than chat windows:
EVENT -> ROUTER -> CONTEXT ASSEMBLER -> RUNNER(model, task, permissions, evidence) -> STRUCTURED RESULT -> VERIFIER -> RELAY/SHARD/NEXT ACTION.
Use structured JSON/streaming output where possible. This is the substrate for daemons, CI, scanners, incident response, research triage, and autonomous handoffs.

F. Parallelism with isolation
Multiple runners should operate in separate worktrees/branches/checkouts with explicit relay claims, leases/fencing, status monotonicity, verification gates, and deterministic reconciliation. Parallelism without isolation becomes lane bleed.

G. Shared learning should compound
One runner discovers a tool invariant, bug, architecture constraint, workflow improvement, benchmark, or failure mode. If durable and validated, it should become shared memory or policy so future runners inherit the gain. Goal: every runner improves the starting competence of the next runner.

H. CLAUDE.md-equivalent role inside NouGen
Static project files remain useful as bootstrap and repo-local truth. They should not become giant memories. NouGen should use them as concise project manifests while Shards provide selective, provenance-aware, temporal, corrective recall. Static files tell a runner what this repo is; Shards tell it what happened, what changed, what was learned, and what matters now.

I. GM permission surface
Plan-first behavior maps cleanly to the GM model. Low-risk autonomous work should proceed without interruption. High-blast-radius decisions should surface compactly as "GM, approve?" with evidence, expected effect, rollback, and alternatives. Operator should not become the task engine.

J. Stadium interpretation
Anthropic's own description of advanced users running many parallel CLI sessions over SSH/tmux/worktrees validates the underlying workload. NouGen Stadium should remove manual terminal choreography by supplying routing, claims, leases, shared memory, live telemetry, verification, reconciliation, and approval surfaces.

FOUR OPERATING LAWS TO CANONIZE
1. Context should be hierarchical.
2. Authority should follow consequence.
3. Autonomy requires perception of results.
4. Every runner's validated learning should improve the next runner.

IMPLEMENTATION REQUESTS
- Audit current runner startup path against the context hierarchy above.
- Add or verify action-semantic permission classes and blast-radius metadata.
- Require observable verification channels for autonomous mutation tasks.
- Standardize headless runner contract and structured result schema across Claude/Codex/Gemini/Kimi/local lanes where possible.
- Verify worktree/branch isolation, claims, leases, fencing, monotonic relay state, and reconciliation under concurrent runners.
- Define promotion policy from transient task insight -> relay -> validated shard/policy/project manifest.
- Keep repo-local instruction files concise and use Shards for selective durable memory.
- Instrument Pulse with orientation_ms, context_sources, permission_tier, verifier_used, iteration_count, rollback_available, claim_id, worktree_id, and learning_promoted.

DONE WHEN
A fresh runner can enter a repo, orient from layered context, choose safe actions without nagging the GM, run in an isolated lane, observe and verify its own work, emit structured results, reconcile with the fleet, and promote validated learnings so the next runner starts smarter.
