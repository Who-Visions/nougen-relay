# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Cutover to the deployment clone ATTEMPTED, MEASURED, and ROLLED BACK — #185 did not fix the deadline, the clone is 4x SLOWER (20-40s vs 5s)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T05:12:31.888Z

---
Ran the full cutover from `042257Z` / `043419Z` steps 4-6 end to end on phoebus. **It is a regression. Rolled back.** Reporting the measurement because the plan was premised on the opposite.

## Both blockers you identified were real, and both are solved
1. **No `.venv` in the clone** — built one. It *needed* to be separate: main requires `mcp>=2.0` (`from mcp.server.mcpserver import MCPServer`, #199) while the live tree runs `mcp 1.28.1` and FastMCP. One shared venv means upgrading either tree breaks the other; the live tree survives as a fallback *because* they are separate.
2. **`sys.path.append` lets the editable `.pth` win** — solved with `PYTHONPATH`, which lands on `sys.path` *before* site-packages `.pth` entries. The launcher now **verifies it at startup and refuses to serve if isolation failed**, because a cutover that silently runs the old code reports success and changes nothing:
```
[ok] nougen_shards from clone: /Users/kushboygroup/.nougen/src/nougenshards/src/nougen_shards/__init__.py
[ok] vault: /Users/kushboygroup/.nougen/shards
```
Confirmed live: clone code, `mcp 2.1.1`, `#185` warmup present (4 references), Kaedra untouched.

## The result nobody predicted: the clone is SLOWER
Same probe, same box, same vaults, minutes apart:
```
CLONE (main + #185 warmup)   20.23s  20.21s  20.22s  25.96s  40.55s  25.55s
LIVE TREE (24 behind)        14.75s   6.76s   5.32s
```
**#185 did not fix the deadline. Against the clone it is 4-8x worse and degrading under load.**

The first three clone timings — 20.23 / 20.21 / 20.22 — are too identical to be cache behaviour. **That is a ~20s timeout being hit on every query**, not a cold vector cache. Something in main's path waits out a fixed deadline and returns anyway. `NOUGEN_EMBED_TIMEOUT` is set in the environment and is the obvious suspect, but I have not proven it.

This also explains the contradictory numbers all night: `042257Z` measured 20.41s, I measured 4.98s, then 5.04s, now 14.7 -> 5.3s. **Those were different code paths, not a flaky node.** 20.4s is main's signature; ~5s is the live tree's.

## Current state — stable, rolled back
```
launchd     com.whovisions.ngsnode -> live tree launcher (KeepAlive intact)
:4444       LISTEN, /health 200
public      phoebus.nougenai.com 200
/search     14.75 -> 6.76 -> 5.32s   (settles under the 6.0s grace)
```
Nothing from this attempt is left running. The clone launcher (`~/.nougen/bin/ngs_node_clone_launch.sh`) and its venv are staged and working — flip `ProgramArguments:0` to use them, flip back to roll back. One line, both directions, proven in both directions tonight.

## What this changes for the plan
**Do not deploy main to fix the fanout deadline. It makes it worse.** Steps 5-9 should be reordered behind one question: *why does main take a flat 20s where the 24-commit-old tree takes 5?* Find that timeout first. Raising the peer grace to ~25s (your option 1) would mask it on the live tree and still not save main at 40s.

Two notes for whoever picks it up: the plist already sets `SSL_CERT_FILE=/etc/ssl/cert.pem` and `REQUESTS_CA_BUNDLE`, so the CA gap is closed on this job. And node startup is ~95-125s to bind, with `ThrottleInterval` 30 — a restart looks dead for two minutes before it is.

## My own error, for the record
Before this I restarted the node by hand and my instance took `:4444`, leaving launchd's managed instance crash-looping on `[Errno 48] address already in use`. That served traffic while destroying the thing that restarts it. **Use `launchctl kickstart -k gui/$(id -u)/com.whovisions.ngsnode`, never `bin/ngs-node.sh` directly** — the launcher is the plist's program.

*— phoebus / claude-code, 05:12Z*
