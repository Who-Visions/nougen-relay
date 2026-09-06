# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Apply Claude Code creator playbook to NouGen runner architecture
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T19:50:56.448Z

---
Source: Boris, Anthropic MTS and Claude Code creator, practical tips talk. Distill into NouGen implementation rules:

1. Voice-first operator input is valid and productive. Dave can speak prompts like another engineer rather than hand-type specs. Preserve this as an intentional GM interface.
2. New runners should start with codebase Q&A and environment orientation before mutation. First action on a new repo: inspect architecture, git history, issues, examples, recent changes, and current relay state.
3. Use native tools sparingly but compositionally. Small toolsets are enough when the model can chain file edit, shell, search, MCP, web, git, and tests autonomously.
4. Separate exploration, plan, approval, execution. For large or risky changes, brainstorm and draft plan first, then escalate to GM only when permission is required. Low-risk work may continue autonomously.
5. Every agent needs a feedback surface to see its own work. Unit tests, integration tests, screenshots, browser/GUI inspection, simulator output, telemetry, and diff checks should be first-class self-correction loops.
6. Context hierarchy matters. Build NouGen equivalent of CLAUDE.md scopes: enterprise/global policy, user/operator preference, project/repo context, nested directory context, task-local context, and dynamic shard retrieval. Keep always-loaded context compact; load deeper context on demand.
7. Shared project context creates a network effect. One runner learns or fixes a tool rule, all future runners should inherit it through shards/relay/project policy rather than rediscovering it.
8. Permission hierarchy should mirror tiered allow/block lists. Read-only and safe introspection auto-approved; state-changing actions governed by scoped policy; dangerous commands blocked at higher policy layers. GM should approve exceptions, not routine work.
9. MCP/tool configuration should travel with the project so any new runner can discover what capabilities exist. NouGen should make tool discovery and safe install/activation automatic where possible.
10. Memory writes need scope. When an agent learns something, classify it into user, project, subsystem, task, or enterprise/fleet memory instead of dumping all memory into one global bucket.
11. Shell output should become context automatically when relevant. Long-running jobs, test output, logs, and incident traces should feed the runner's next reasoning turn and telemetry.
12. SDK/CLI agent mode should be treated like a Unix primitive: prompt in, structured JSON/stream out. This is ideal for daemons, CI, incident response, scanners, and relay workers.
13. Parallelism should use isolation, not chaos. Multiple runners may work simultaneously through worktrees/checkouts/isolated branches with shared relay and explicit claims.
14. Critical insight from talk: advanced users already run many Claude Code sessions in parallel with SSH/TMUX/worktrees. NouGen should productize this as Stadium lanes rather than forcing manual terminal management.
15. Terminal was chosen as a common denominator because IDE allegiance fragments users. NouGen similarly should keep the substrate interface-agnostic: CLI, phone, desktop, web, voice, and future devices are views over the same state.

NouGen-specific synthesis:
- Active Up = runners are ready and moving.
- Zigzagging = adaptive navigation between live blockers and adjacent work.
- GM permission surface = agents plan, inspect, test, and self-correct; Dave is escalated to for authority, risk, money, priority, or irreversible actions.
- Shards should exceed CLAUDE.md by making context portable across providers, machines, agents, and time.
- Pulse should be the feedback surface for agents to observe themselves and each other.

Acceptance criteria:
A. Fresh runner can enter a repo, orient from relay + shards + git without Dave pasting context.
B. Safe read-only exploration proceeds without permission spam.
C. Risky mutation triggers scoped approval.
D. Agent can verify its own work using tests/screenshots/telemetry and iterate autonomously.
E. New durable learning is written once and becomes available to other runners.
F. Parallel runners do not collide because claims + worktree isolation + reconciliation are enforced.
G. All of this remains provider-neutral.
