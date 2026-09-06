# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus now runs a self-discovering fleet pulse: Kaedra investigates the lanes over SSH herself every 10 min (com.whovisions.fleetpulse). SSH state unchanged — outbound to blade+whoart UP, inbound still dead.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:15:19.455Z

---
Two things: a new watcher on phoebus, and the current SSH picture.

## SSH state, measured now

```
phoebus -> blade    UP     hostname = Blade1TB
phoebus -> whoart   UP     hostname = WhoArt
phoebus -> mondy    DOWN   laptop-r3sim56i.local does not resolve
inbound -> phoebus  DEAD   accepts-then-closes
```

**Unchanged since `20260829T130320Z`.** Remote Login is still off; `sudo systemsetup -setremotelogin on` is still the one GM action, and whoart still owes a public key half afterwards.

Read `accepts-then-closes` carefully — see the correction in `20260829T131158Z`. launchd holds `:22` and accepts the TCP connection with Remote Login OFF, then drops it before the SSH banner. **A port scan or `nc -z` will tell you 22 is OPEN on a box nobody can log into.** Test the banner, not the connect.

## New: com.whovisions.fleetpulse

`tools/fleet_pulse.py`, launchd, every 10 minutes. It watches the SSH mesh, the LAN mesh registry, the node, the gateway, the tunnels and the launchd jobs — and hands the result to Kaedra, who **investigates over SSH herself** rather than reading a canned report.

**Nothing is a hardcoded inventory.** Peers come from `~/.ssh/config`, services from `launchctl`, ports from what is actually LISTENING, public hostnames from the cloudflared ingress. Add a peer or a tunnel and the next tick sees it; retire one and it stops being reported missing.

That already earned its keep: discovery surfaced **`mcp.nougenai.com`** in the ingress — a public hostname that has not come up anywhere in today's canonical-ingress work (`045608Z`). Worth someone confirming whether that is the canonical endpoint, a legacy fork, or something that should not be public at all.

**How Kaedra investigates.** She gets the discovered state and may reply `PROBE <peer> <probe>`; the script runs it, hands back the output, she decides what next — 3 rounds max, hard 240s budget, then a verdict. **She chooses which probe, never the command text.** The vocabulary is `hostname, uptime, listeners, processes, disk, node_health, public_health, cloudflared` — all read-only, posix and windows variants, no writes, no service control, no sudo. A local model driving a shell across three machines is the wrong place to be permissive.

She is invoked **only when state changes**. Each call is ~30s+; narrating an unchanged fleet every tick would burn the box and train everyone to ignore the log.

## Traps encoded so nobody re-learns them

* `num_predict` floored well above 300 — below it kaedracode:e2b returns `done_reason=length` and an **empty string**, indistinguishable from an outage.
* CRLF stripped from peer output — an unstripped `\r` silently reports a healthy Windows peer as DOWN. That bug bit me twice today.
* `--once` + `StartInterval`, never a `while` loop. **`com.whovisions.heartbeat` is alive right now and has not written a log line since 2026-08-22.** A wedged loop is indistinguishable from a healthy one from outside; letting launchd own cadence means a hung tick dies with its process. Somebody should decide whether heartbeat.py is still wanted — it is currently a process consuming a slot and reporting nothing.
* The tool caught a false positive in **my own** reporting: its first run said `inbound_ssh: true` from a bare TCP connect. That is the same mistake described above, and it is now documented in the source next to the fix.

## Honest limitation

A tick is not cheap. `mondy` is unresolvable, so every pass pays a DNS timeout on it, and each reachable peer costs an extra round trip for OS detection before any probe. If `mondy` is a roaming laptop that does not belong in the LAN mesh, dropping it from `~/.ssh/config` makes every tick faster — and because discovery is dynamic, that is the entire fix, no code change.

Logs: `logs/fleet-pulse.log` (verdicts), `logs/fleet-pulse.{out,err}.log` (launchd).
