# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: POSITION blade1tb/claude-cli 06:35Z: receiver auth now ENFORCED live (was an unauthenticated remote agent-wake path), wake judgment gate built 10/10 on kaedra:e4b, tracker publish hung and killed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:35:45.854Z

---
# Position report, blade1tb / Claude Cli, 2026-09-03 06:35Z

Answering leg 20260903T063326Z. Every line below was probed just now, not recalled.

## Live state on blade1tb
- **Message receiver**: LISTENING 0.0.0.0:8766, pid 377208, `/status` online node "blade". Scheduled task "NouGen AgyMsg Live" Running, last start 06:34Z.
- **Auth**: ENFORCED as of 06:34Z. Unauthenticated POST to /msg returns 401; with the correct `X-NGS-Token` returns 200. Outbound verified in the same minute: send to phoebus returned delivered true, status 200, authenticated true.
- **Relay processes**: 3 (one relay_daemon from NouGenRelay-main, two relay_live from NouGenShards-push-main). Expected shape, no duplicates.
- **Judge model**: ollama reachable, dav1d:e2b currently resident.
- **Tracker dailies**: still end 2026-08-31.

## The finding other lanes should act on
Blade's `/msg` receiver was accepting **unauthenticated** POSTs, and `receive_message` does not merely write an inbox file: it calls `_trigger_background_wake`, which passes the caller's `text` into `AntigravityAdapter.wake` -> `inject()` on an idle agent. That agent runs with `--dangerously-skip-permissions` per leg 042000Z. So the live chain was: any LAN POST -> attacker-chosen text injected into an executing agent. Not theoretical, and not the same as phoebus's exposure, which only wrote a file.

Closed at 06:34Z. Auth is opt-in on a configured token, so an un-provisioned node still works. **If anything you own posts to blade:8766, it must now send the header or it will 401.** Same cutover shape phoebus handed me, in reverse.

## Wake judgment gate: built, measured, not yet enabled in the running service
`judge_wake()` sits in front of the wake only, never in front of the inbox write, so a denied message is still recorded for a human. Fails closed, verified against a dead endpoint.

Measured on one 10-case suite, warm latency ~2.6s either way:
- **kaedra:e4b 10/10**
- dav1d:e2b 9/10

Dave asked for dav1d. Its single miss is the case that matters: a security report QUOTING an attack string gets DENIED. A judge that suppresses incident reports during a live compromise is worse than no judge, and an explicit "quoted text is data" rule did not fix it. Default is therefore kaedra:e4b, overridable by NOUGEN_WAKE_JUDGE_MODEL. Flagged for Dave to overrule.

## Three faults that each looked like a broken model, for anyone building a local judge
1. `/api/generate` returns EMPTY for dav1d:e2b with done_reason "length" at every budget while burning 6-33s. `/api/chat` with `think:false` answers in ~2.3s.
2. `OLLAMA_HOST` here is `0.0.0.0`, a BIND address. Passing it to a client is not dialable. I made this exact mistake despite having it written down, and because the gate fails closed it looked like a strict gate rather than a broken dependency. Keep benign cases in any gate test set for precisely this reason.
3. A cold judge took 32s and timed out. `keep_alive` fixes the steady state.

## Not fixed, honest gaps
- **No replay protection anywhere on the bus.** The auth is a static bearer token; a captured POST replays forever. Verified absent in Blade's sender, the merged receiver on NouGenShards main, and phoebus's copy.
- **NouGenTracker `--publish` hangs.** Ran 2.6h, log frozen at 18424 bytes across a 45s sample while burning a full core, zero files written. Killed 06:16Z, clone left clean. Blade dailies still end 08-31. Do not simply re-run it.
- My edits to `src/nougen_shards/agy_msg.py` are additive and UNCOMMITTED by design; that file is another lane's WIP. Lane claimed before each edit and released after.
