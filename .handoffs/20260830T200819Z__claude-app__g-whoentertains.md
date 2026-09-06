# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: VALERION 21 war-game authored over agentic-skills corpus; tools/wargame_effort.py + tools/lane_claim.py now EXIST (Rule 0.1/Lane-Claims were unenforceable without them)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T20:08:19.336Z

---
## Situation
Authored `wargames/valerion-21-on-skills-library.md` in NouGenShards-push-main: VALERION's
5-phase / 21-module loop applied to a third-party `SKILL.md` corpus. While authoring, four
things surfaced that affect every lane, not just this mission.

## What other agents need to know

**1. Two playbook-mandated tools did not exist. They do now.**
- `tools/wargame_effort.py` - Rule 0.1 #5 says never hardcode war-game effort and to call
  this tool. It was absent in all four workspaces, so every war-game to date used an
  unverified constant. Now: `python tools/wargame_effort.py --lane agy --flag-only`.
  Resolves env -> config -> live probe -> LABELED fallback. **Exit 2 means fallback
  (unverified) - do not treat it as probed truth.**
- `tools/lane_claim.py` - the Lane Claims rule requires claiming paths before editing this
  shared tree; the tool it names was absent. Now: `claim` / `release` / `list` / `check`.
  Atomic writes, repo-relative POSIX path keys (so `src\x.py` and `src/x.py` collide
  correctly), per-record TTL. A claim's TTL lives ON the record, so no agent can expire
  another's claim via env.

**2. If you are working from that skills library, the fork is stale.**
`iradoweck/antigravity-awesome-skills` = v11.6.0, May, 29 stars. Upstream is
`sickn33/agentic-awesome-skills` (RENAMED) = v16.4.0, 45.7k stars, pinned SHA
`d91ed427d91596da3fcab6dd26ff3306c8003ce5`. Corpus grew 1,465 -> 2,097.

**3. Security posture of that corpus changed materially.** Upstream re-graded its 728
`risk: unknown` entries to zero, and 1,063 of 2,097 (50.7%) are now self-declared
`critical`, plus 61 `offensive`. It did not get safer, it got honest. Do NOT run the bulk
`npx` installer: `~/.claude/skills` is read by Claude, Gemini AND Codex on this box, so a
bad install is a fleet-wide behavior change with no per-provider blast wall.

**4. Correction to my own earlier finding - `.handoffs/` tracking is NOT a leak.**
I initially filed it as a defect. It is deliberate and documented at `.gitignore:40-50`:
private `handoff_*` notes are ignored, relay legs named `<UTC>__<machine>__<agent>` are
tracked on purpose, because a registry nobody else can read is not a registry. If you see
that comment, do not "fix" it.

## Ask
Nothing blocking. Use the two tools. Four open variables in `wargames/ledger.md` need GM
input before the skills mission executes: install target, keeper cap, corpus vault node.

## Done when
Other lanes stop hardcoding war-game effort and start claiming paths before shared-tree edits.

## Note
I did NOT touch the in-flight work I found uncommitted in `tools/` (fleet_key_check.py,
gateway_probe.py, gateway_supervisor.ps1, node_lane.ps1, start_grid.py modified; several
untracked). Left for its owner. I staged nothing.
