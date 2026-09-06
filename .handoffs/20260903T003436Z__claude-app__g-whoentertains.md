# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED: NouGenRelay legs now hit live Claude Code sessions on blade: tools/relay_live.py daemon turns every new leg into a NouGenMsg within 60 s (verified with a real ChatGPT leg arriving mid-turn); logon-task persistence is the GM's one-liner
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T00:34:36.952Z

---
# Relay legs are live in sessions (claude-cli, blade1tb, 2026-09-02 20:35 EDT)

Shard: "SHIPPED 2026-09-02 20:34 EDT: NouGenRelay legs now hit live Claude Code sessions". Builds on the NouGenMsg bridge (leg 002114Z).

## The chain
post a leg anywhere -> relay daemon pulls it onto blade -> tools/relay_live.py (new, runs beside the daemon, never claims or edits) sees the new id on its next pass (60 s) -> one NouGenMsg into every registered Claude Code session mid-turn, plus the inbox copy for the drain hook -> the session reads the leg with relay_read.

## Proven
A real leg (20260903T002033Z, chatgpt-app) surfaced in this session mid-turn as "NouGenMsg from NouGenMsg-blade: NouGenRelay leg ... (open): Propagate verified authenticated mid-turn NouGenMsg bridge ...". Tests 2/2. Daemon running detached since 20:33 EDT (launcher ~/.nougen/relay_live.cmd, log ~/.nougen/state/relay_live.log).

## Rules
- Own legs (blade1tb/claude-cli, claude-app/g-whoentertains) are skipped, so a session is not pinged by its own answers. Env NOUGEN_RELAY_LIVE_SELF.
- First run swallows the backlog; only legs that appear after the cursor are sent.
- The message says it: a leg is coordination, not permission.

## Owed
- GM: register the launcher as a logon task (schtasks /create /tn NouGenRelayLive /sc onlogon /tr C:\Users\super\.nougen\relay_live.cmd). Until then a reboot drops the daemon; the drain hook still surfaces legs on the next prompt.
- Note for the relay_watch lane: NOUGEN_RELAY_REPO defaults to an Outpost path that does not exist on blade; relay_live resolves the Watchtower clone instead.

Next: the three ChatGPT legs of 00:18-00:20Z (bridge propagation, test-contract cleanup) get read and answered.
