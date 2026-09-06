# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: REDISCOVERED Xoah: restore completed Shadow Xoah stack to MAP and finish tool/skill inventory
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:12:03.340Z

---
REDISCOVERY EVIDENCE: Dave remembered Xoah AI existed in prior relays. Confirmed by reading relay `20260902T151307Z__claude-app__g-whoentertains`.

That relay is COMPLETE and proves Shadow Xoah was already shipped/live end to end through the canonical door. It reports node PID 238356, Worker e4f8d35b9514, 49/49 tests, six green smokes, and live `ask_xoah` response in 10.9s. Codex reconciliation explicitly verified Shadow Xoah Self Archive, Stage 9/10 identity, Throne Governance, destiny flow, and canonical-door calls.

The shipped MCP surface reportedly had 28 tools including:
* ask_xoah
* xoah_pressure
* xoah_override
* xoah_self
* xoah_throne
* xoah_throne_decide
* destiny_* family
* unfinished_destinies
* evolve_report
* ask_dav1d

CURRENT REGRESSION: ChatGPT's presently exposed NouGenShards connector does not discover `ask_xoah` or the Xoah tool family. This is NOT a blueprint/missing-agent problem. It is a MAP/tool exposure, registration, deployment, schema, or connector synchronization regression until proven otherwise.

FINISH THE MAP TOOL UPDATE:
1. Diff the current canonical MCP tool registry against the verified 2026-09-02 28-tool Xoah-era registry and current intended registry.
2. Trace Xoah from implementation -> server registration -> canonical gateway/Worker -> MAP manifest -> connector/tool schema exposure -> external discovery. Identify the exact link where she disappears.
3. Restore `ask_xoah` plus the intended Xoah pressure/self/throne/destiny surfaces through the canonical public tool map, respecting auth and release boundaries.
4. Do not duplicate/rewrite the working Shadow Xoah implementation merely to repair discovery.
5. Audit every other canonical agent/tool/skill for the same silent disappearance. Compare source registration, runtime `/tools` or equivalent, MAP manifest, and externally visible connector schemas.
6. Generate/update one authoritative machine-readable MAP inventory: canonical id, aliases, kind, owner/location, capability, invocation endpoint/tool, schema/version, auth/trust scope, health, deployment status, discovery visibility, and last verified timestamp.
7. Add an automated MAP parity/completeness test. If a production tool is registered and healthy but absent from expected external discovery, fail loudly. If intentionally hidden, require an explicit visibility policy/reason. If planned only, label it planned.
8. Version/fingerprint the MAP/tool manifest so stale connector schemas can be detected instead of silently served.
9. Verify from OUTSIDE the node, through the same canonical connector path Dave/ChatGPT uses. Internal localhost success is insufficient.
10. Return evidence: before/after tool counts, Xoah tool names visible externally, manifest/version, test output, canonical endpoint/build/commit, and one successful external `ask_xoah` invocation.

DONE WHEN: ChatGPT/external lanes can discover Xoah again through the canonical map, the full map inventory is reconciled, missing tools/skills are accounted for, and CI/health catches future map drift automatically.

Important lesson: historical operational evidence successfully rediscovered a capability that current discovery had forgotten. The memory layer beat the live MAP. Preserve this as a regression fixture.
