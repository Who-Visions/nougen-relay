# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED legs 005442Z + 005214Z: relay-live now reads legs off the registry branch with a 3 s active poll (9 s create-to-visible measured); SessionEnd hook returns sub-second, index rebuild detached
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:13:59.680Z

---
## Latency (leg 20260903T005442Z)
Measured components on blade 2026-09-03 00:58Z to 01:12Z:
- connector -> origin/main commit: about 1 s (leg 010742Z created 01:07:42Z, commit 01:07:43Z).
- origin/main -> blade working tree: the relay daemon (NouGenRelay-main/tools/relay_daemon.py, heartbeat 200 s, CLI flag only, no env) copies legs via ls-tree/show. Its logs are 0 bytes and the 5-min watchdog task "NouGen Relay Watcher" last exited rc=3. Observed: legs created 00:44Z to 00:54Z all landed at 01:00:01Z. THIS was the latency, not the relay_live poll.
- git fetch floor: 1.9 to 2.3 s. ls-remote 1.8 s, no cheaper.

Shipped in tools/relay_live.py (tests/test_relay_live.py 7/7):
- reads leg ids and bodies straight off origin/<registry branch> after its own fetch (branch from NOUGEN_RELAY_BRANCH, else origin/HEAD, else main). Read-only, never writes the working tree, never claims. The relay daemon's copy is no longer on the critical path.
- adaptive cadence: NOUGEN_RELAY_LIVE_ACTIVE_S (3) held for NOUGEN_RELAY_LIVE_ACTIVE_WINDOW_S (600) after the last new leg, doubling back off to NOUGEN_RELAY_LIVE_INTERVAL_S (60). Fetch + rev-parse compare, ff-merge only when upstream moved.
- wake file NOUGEN_RELAY_LIVE_WAKE (~/.nougen/state/relay_live.wake); `relay_live.py --wake` touches it and a sleeping daemon passes within NOUGEN_RELAY_LIVE_WAKE_POLL_S (0.5). This is the seam for an event path (gateway route or Worker callback just touches the file).
- every delivered leg logs create_to_visible_s to ~/.nougen/state/relay_live.log (quiet mode prints only passes that delivered or errored).

Evidence: leg 20260903T011138Z created 01:11:38Z, delivered to the live Claude session 01:11:46Z = 9.0 s (the log line shows 3609.0 from a DST offset bug in the first build, fixed to calendar.timegm before the restart at 01:12:45Z). Daemon runs under logon task NouGenRelayLive, one process.

Not touched (out of scope by the leg): ownership, claiming, provenance, NouGenMsg auth.
Observations for the relay daemon owner: NouGenRelay clone is on pi-remix, 35 commits ahead of origin/pi-remix (the daemon never pushes; those are someone else's); daemon log 0 bytes since Aug 27.

## SessionEnd hook (leg 20260903T005214Z)
Root cause: `handoff rebuild-db` takes 25 s (748 records, work not import) inside a hook with a 20 s timeout, so the auto-stub path got cancelled. 386 stale .start markers confirm it.
Fix in tools/handoff_guard.py (tests/test_handoff_guard.py 4/4): stub written synchronously, marker cleaned, then rebuild-db spawned detached (DETACHED_PROCESS on Windows, start_new_session elsewhere). Git calls capped by NOUGEN_HOOK_GIT_TIMEOUT_S (5). Sessionstart sweeps markers older than NOUGEN_SESSION_MARKER_MAX_AGE_H (168). Measured auto-stub path under 1 s.

## Open ChatGPT legs left for their owners
005715Z (Ollama first-pass relay processor), 005813Z (compact-recall savings baseline), 010742Z (MCP scale destiny), 011001Z + 011138Z (Spas Jamaica case study 2). None are relay-live work.

War-game: NouGenShards-push-main/wargames/relay_live_latency.md.
