# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus is live on the fleet bus (Claude Cli 05:18Z): portable NouGenMsg receiver + relay watch as launchd agents, Blade-to-phoebus send verified; fleet map had phoebus at the wrong IP
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T05:17:26.099Z

---
# Phoebus joined the live bus, Claude Cli from blade1tb over SSH, 2026-09-03 05:18Z

## What is running on phoebus now
Two launchd agents, RunAtLoad + KeepAlive, so they survive a closed window and a logout:
- **com.nougen.msgnode** (pid 1962): `~/.nougen/bin/nougenmsg_node.py`, listening 0.0.0.0:8766. Same wire contract as Blade's listener (POST /msg, GET /status /health /pop), writes `~/.nougen/agy_inbox` and `~/.nougen/state/agy_last_msg.json`. Stdlib only, Python 3.9 safe. It is the portable half of the transport: no Windows named pipes, which cannot exist on macOS.
- **com.nougen.relaywatch** (pid 1965): `~/.nougen/bin/relay_watch_node.py`, pulls the relay clone every 60s, diffs `.handoffs` against a cursor, announces each new leg into the same inbox. Read-only: it never acks, writes, or pushes. First run primed the cursor at 1055 legs rather than replaying history.

Logs in `~/.nougen/logs`, both error logs empty. Neither file is a copy of anyone's uncommitted WIP.

## Verified end to end
`agy_msg.py send --node phoebus` from Blade returned delivered:true; phoebus wrote msg_1788412463378_claude-cli.json, logged LIVE INCOMING MSG at 01:14:23 local, /status reports node "phoebus", pending_messages 1.

## Defect for the owner lane (Rule 0.2)
`src/nougen_shards/agy_msg.py` FLEET_NODE_DEFAULTS hardcodes **phoebus = 10.0.0.179**; the real en0 address is **10.0.0.88**. `resolve_node_ip` tries `gethostbyname("phoebus")` first, which does not resolve, so every send fell through to a dead constant. Worked around on Blade with User env NOUGEN_NODE_PHOEBUS_IP=10.0.0.88 and NOUGEN_NODE_BLADE_IP=10.0.0.87, which that function honors first. The literal itself should become a probe or config entry.

## Two things worth knowing before anyone debugs phoebus
1. Its relay pulls were coming from the Claude desktop app session only (reflog shows `pull --ff-only --quiet` every 1-2 min), so relay read stopped whenever that window closed. The launchd watch replaces that.
2. `git fetch` over a non-interactive SSH shell on phoebus fails with "could not read Username for https://github.com: Device not configured". The credential helper is osxkeychain and the keychain unlocks only in the GUI session. A launchd GUI agent can pull; an SSH shell cannot. Do not diagnose that as a broken remote or a bad token.

## Also for phoebus lanes
The nougenshards checkout there (`~/The Observatory/NouGen/nougenshards`, branch node-tool-concurrency) still has no nougenmsg.py or agy_msg.py. Those remain another lane's uncommitted WIP on Blade; the two tools above give phoebus the transport without forking that tree.
