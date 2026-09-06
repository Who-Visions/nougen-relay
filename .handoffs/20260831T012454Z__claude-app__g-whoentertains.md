# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: relay daemon now probe-verifies before acking - dav1d proposes read-only probes, daemon runs whitelisted ones, prose can no longer close an execution-shaped leg
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T01:24:54.512Z

---
# Daemon elevation: probe-grounded verification (GM order 2026-08-31)

**What was broken:** `verify_execution` had the local model grade PROSE against the triaged one-liner. A fleet-lane essay restating a diagnosis acked leg `20260830T234325Z` as "dispatch verified" - on a leg that asked for a fix. Verification never touched live state.

**What changed** (`NouGenRelay-main/tools/relay_daemon.py`, the running copy):
- New `dav1d_probe_verify`: dav1d proposes up to `NOUGEN_DAEMON_PROBE_MAX` read-only probes (argv lists), the daemon filters them through a hard whitelist (`gh api` GET-only, `git` read subcommands, `curl` GET-only, no shell ever), runs survivors, then dav1d judges ONLY the probe outputs. Every error path fails closed - unprobeable completion claims stay open.
- Legs whose goal/done-when demands change (fix/patch/deploy/rotate/... - `NOUGEN_DAEMON_CHANGE_MARKERS`) can never be acked off a fleet answer. Pure question legs still get fleet answers, labeled `fleet-answer`.
- Verdicts verify against the leg's own done-when section, not just the triage line.
- Ack notes now carry the probe trail (argv + exit codes), cap raised to `NOUGEN_DAEMON_ACK_NOTE_MAX` (1000) - every ack is re-runnable by a human.

**Evidence:** `tests/test_daemon_verify.py` - 15 tests passing, incl. a regression test replaying the exact 2026-08-30 hollow ack (prose restating a diagnosis must NOT verify). Daemon restarted on patched code: old PID 4548 killed, new PID 139064 up, `--status` shows ollama alive with dav1d:e2b loaded. Backup at `tools/relay_daemon.py.bak-20260831T00` (in NouGenRelay clone) and war-game at `NouGenShards-push-main/wargames/relay-daemon-verifiable.md`.

**Still open (not this leg):** the connector's 1000-entry contents-API cap (worker patch or .handoffs rotation) - connector readers are still blind to legs after 08-29T12:00Z. Full pytest suite run in progress; new-test file green.

**Done when (this leg):** next daemon acks in the registry carry `probe-verified:` trails; no further prose-only acks on execution-shaped legs.
