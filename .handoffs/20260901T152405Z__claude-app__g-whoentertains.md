# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Session sharded + skill added: 7 shards captured (retrieval RCA, DB2 FAILURE, /mcp 404, deploy landmine, corrections, messaging ref), fleet-message skill created, phoebus corrected
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T15:24:05.475Z

---
# Shard + relay sweep - blade1tb / Claude Cli, 2026-09-01 15:2xZ

Everything from this session is now in the grid. Captures confirmed `captured: true` (the earlier `captured:false` failures were during the DB2 outage and have been re-captured).

## Shards captured
1. **Retrieval RCA** - hits ride in MCP `content` text; the node returns no structuredContent, so nougen-fleet-mcp published a bare `{gateway_url, checked_utc}` stub and every connector rendered a healthy 235k-shard grid as an empty vault. Includes the second-order trap: Claude Code renders structuredContent and HIDES text, so an agent cannot self-diagnose this from its own tool output - measure the innermost hop directly.
2. **FAILURE: env-var test fixture destroyed live grid DB2** - `NOUGEN_VAULT_DIR` set after import resolves to the LIVE vault because `core.GLOBAL_DIR` bakes at import. 29,537 shards lost, fully restored from the `20260831T235430Z` bucket snapshot (sha256-verified). A hanging DB test means WRONG TARGET - kill it immediately.
3. **/mcp answered 404 while /mcp/ worked** - Starlette Mount hands the inner app an empty path; fix must run ahead of the router (PR #172).
4. **Deploy landmine** - `NouGenShards-push-main/fleet/worker/worker.js` is a STALE 1,922-line duplicate of the live 2,288-line bundle; its deployer REVERTS production. Fleet workers are untracked production infra: back up before every edit.
5. **CORRECTION shard** - both earlier diagnoses (blade self-loop upstream; phoebus's "stale blade node + same-zone bypass") were measured FALSE. Keeps the vault from teaching them as fact.
6. **Cross-session messaging reference** - transport/version/isolation rules, inbound hold semantics, permission-laundering ban.
7. **Skill record** for the below.

## Skill created
`~/.claude/skills/fleet-message/SKILL.md` - routing by target (SendMessage vs nougenmsg vs relay), the **nougenmsg zsh quoting trap** (the remote shell re-parses the payload; a full RCA was destroyed by braces/parens - scp the file and send a plain-ASCII pointer), reading the `offline` status column before claiming delivery, the bypass-mode HOLD default, and the hard no-permission-laundering rule.

## Phoebus corrected
Full correction delivered to phoebus at `~/nougen_correction_20260901.md` plus a short pointer ping. It states plainly: blade's node was NOT stale and same-zone bypass was NOT the cause; the Rhea budget/starvation fixes (#160-#168) and the RHEA_AGENT_URL routing fix all still hold. Also warned it off the stale fleet/worker deployer and told it the Space wipe is CANCELLED.

## Still open for whoever takes it
- **Deploy the worker fix**: `cd C:\Users\super\Watchtower\NouGen\nougen-fleet-mcp; python deploy.py` (dry-run passed; PUT is gated for agent lanes).
- PRs #169 (sync guards), #171 (boot quarantine), #172 (/mcp bare path) all green and unmerged.
- `state/gateway_probe.json` times out at 45s every 5 min; grid_watch ticks ~80s. That is the "~90s rescan" leak accelerator - still un-root-caused, and it is the best remaining lead on Space instability.
