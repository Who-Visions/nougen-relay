# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Expose next generation NouGen tools for closed loop agency
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T23:37:30.685Z

---
Full proposal for expanding the NouGen connector surface.

Objective: move NouGen from strong memory plus handoff into closed loop agency where the fleet can observe reality, reason, act safely, verify consequences, and preserve the lesson.

Proposed tool families and concrete tools:

MEMORY
1. repo_scan
Structured repository overview without shell access. Return files, languages, manifests, entry points, changed files, public interfaces, test layout, docs drift candidates.
2. repo_read / repo_grep
Targeted code retrieval across NouGen repos. Exact symbol search, semantic code search, config lookup, dependency refs, endpoint definitions. Bridge Shards memory to executable truth.
3. shards_related
Given a shard id, return causal neighbors: what preceded it, failures that produced it, relay that implemented it, later correction shards, likely code embodiment.
4. shard_from_diff
When a commit lands, extract the durable lesson automatically: what changed, why, what failed, what condition made the fix necessary.

MOTION
5. repo_diff
Show what actually changed between commits, branches, tags, or timestamps.
6. repo_status
Branch, dirty state, HEAD, ahead/behind, recent commits, failing checks.
7. fleet_activity
Not just claims. Derive what each machine actually did over the last N minutes/hours from relay events, commits, tests, tracker activity, and logs.
8. fleet_compare
Compare what two or more lanes believe about the same system state and resolve disagreement against repository/runtime truth. Example: ChatGPT thinks endpoint=A, Claude thinks endpoint=B, repo truth=A.

ACTION
9. tests_run
Safe scoped test execution. Specific test, package, repo, smoke suite. Return command, exit code, failures, duration, artifacts.
10. command_run
Heavily sandboxed allowlisted execution with scoped working directory, timeout, output caps, and secret protections.
11. relay_from_failure
Given a failed test, traceback, service health event, or incident trace, generate an actionable relay with evidence, suspected cause, affected surfaces, prior shards, and done-when criteria.
12. readme_sync
Dynamic documentation compiler. Scan repo truth, relays, shards, commits, releases. Detect README drift, propose/update auto-owned sections, preserve human-owned narrative, emit provenance.

VERIFICATION
13. service_health
Unified health surface for Blade, Shards gateway, Relay, Tracker, Rhea, Kaedra, Dav1d, MCP, public endpoints, backing stores.
14. logs_query
Search logs across machines/services by time, correlation id, request id, error signature, endpoint, provider, or agent.
15. incident_trace
Given a failure or relay id, assemble the causal timeline: request entered here, agent called this, timeout occurred there, fallback fired, shard captured, fix landed here.
16. verify_relay
Before marking a relay done, verify its success condition against repo state, tests, endpoint health, logs, or runtime evidence. "Fixed" must mean proven, not claimed.
17. docs_drift
Answer the narrow question: what public documentation is now false? Example README says 25 tools while connector exposes 29, renamed endpoint, changed install flow, stale env var.
18. public_surface_audit
Sweep every public NouGen repo and inspect what outsiders see: READMEs, install instructions, URLs, package metadata, licenses, examples, badges, APIs, stale references.

HISTORY / RELEASES
19. changelog_build
Generate changelog entries from verified code changes plus relays and shards. Inputs could include since, until, repo, release, public_only. Separate features, fixes, architecture changes, breaking changes, known issues, recoveries.
20. release_snapshot
Freeze component state at a milestone: commit, tool count, APIs, schemas, architecture, tests, relevant shards, relays, tracker metrics.

Desired operating model:
observe -> reason -> act -> verify -> remember

Expanded architecture:
MEMORY: shards_recall, shards_search, ask_griot, repo_read, repo_grep, shards_related
MOTION: relay_create, relay_read, relay_claim_list, repo_diff, repo_status, fleet_activity, fleet_compare
REALITY: repo_scan, service_health, logs_query, incident_trace
ACTION: command_run, tests_run, relay_from_failure, readme_sync
VERIFICATION: verify_relay, docs_drift, public_surface_audit
HISTORY: changelog_build, release_snapshot, shard_from_diff

Critical design principle: memory must be able to look at reality and prove itself. Repository source/config/tests/live interfaces outrank remembered claims for hard technical facts. Shards preserve why and history. Relays preserve operational motion. Changelog preserves transitions. README preserves current public truth.

Target user experience: when asked "what are they doing?", NouGen should answer with evidence such as: Claude changed 4 files, Dav1d modified this route, two tests failed, Kaedra found the April implementation, second patch passed, this shard records why, README is now stale in two sections, here is the exact delta.

Done when: fleet evaluates the proposal, maps each tool to existing infrastructure where possible, identifies the smallest high leverage first wave, and returns an implementation plan rather than spawning redundant endpoints.
