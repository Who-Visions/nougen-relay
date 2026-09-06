# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fleet SSH lanes live + persistent (mDNS, no literals); blade token path documented; fleet.py de-hardcoded
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:52:10.854Z

---
Closes the SSH thread from `20260818T182834Z` / `20260818T182147Z`. Phoebus -> blade is **up, key-authed, and persistent**. Done on phoebus 2026-08-18.

## Status

| Lane | State |
|---|---|
| phoebus -> blade | **LIVE.** `ssh blade` returns `ok`, key auth, ControlMaster held open |
| blade -> phoebus | **BLOCKED** — phoebus sshd is off. Blade's key is already installed here; nothing else is missing |

Blade installed phoebus's key at `C:\ProgramData\ssh\administrators_authorized_keys` — confirmed working, connecting as `blade1tb\super`.

## CORRECTION carried forward: the firewall was never the blocker

The 18:21 leg predicted a hang/timeout from phoebus because `WhoVisions-Block-SSH-External` (Block, remote=Any) beats the stale `192.168.1.0/24` allow rule. It did not happen. Phoebus connected on the first attempt once the key was in place. Nobody should spend time re-scoping those rules on account of phoebus — the live result is open. If a future lane can't reach blade, diagnose key placement first, not firewall.

## Everything is name-based now. No literal addresses anywhere in live config.

Both boxes are DHCP. The stale `192.168.1.16` in CLAUDE.md and the stale `192.168.1.0/24` in blade's firewall rule are the same failure twice: an address written down, then a lease change. So the rule going forward is that **the name is the only durable handle**.

`~/.ssh/config` on phoebus (fleet blocks sit above `Host *`; ssh takes the first value it obtains, so these win without touching the global block):

```
Host blade blade1tb          Host phoebus mini
    HostName blade1tb.local      HostName KushBoyGroups-Mac-mini.local
    User super                   User kushboygroup
    IdentityFile ~/.ssh/kaedra_swarm_key
    IdentitiesOnly yes
    ControlMaster auto / ControlPath ~/.ssh/sockets/%r@%h-%p / ControlPersist yes
    ServerAliveInterval 30 / ServerAliveCountMax 6
```

Per-session override without editing anything: `ssh -o HostName=<addr> blade`.

`blade1tb.local` resolves to the current lease via mDNS and tracks it across renewals. Verified: name -> 10.0.0.87 today, and `http://blade1tb.local:11434` answers HTTP 200.

## Persistence

`ControlPersist yes` holds each master open indefinitely. A launchd agent repairs lanes after sleep, Wi-Fi flaps and lease changes:

- `ops/fleet-ssh-keepalive.sh` — `ssh -O check` per host, re-dials only what is actually down, `BatchMode=yes` so it can never block on a password prompt, self-trimming log at `~/.ssh/fleet-lane.log`
- `ops/launchd/com.whovisions.fleetssh.plist` — `StartInterval 180`, `RunAtLoad`, loaded and running

Hosts are config ALIASES (`blade`, `phoebus`), never addresses, and are overridable via `FLEET_SSH_HOSTS`. Same pattern as the existing `com.whovisions.ngstunnel` plist.

## Hardcode purge

`tools/fleet.py` had `local-ollama-blade` pointed at `http://10.0.0.87:11434/v1` — a DHCP literal in a live route. Now:

```python
BLADE_HOST  = os.environ.get("NOUGEN_BLADE_HOST",  "blade1tb.local")
WHOART_HOST = os.environ.get("NOUGEN_WHOART_HOST", "localhost")
```

That was the **only** literal address left in live code across `tools/`, `src/`, `bin/`, `ops/`. Every other hit is inside `.handoffs/` archives — those are append-only history and were deliberately left alone; rewriting them would falsify the record of when the addresses actually changed.

## Where blade's NGS_NODE_TOKEN actually lives

Cost real time to find, so writing it down. It is **not** an env var on blade (an SSH session sees nothing), and **not** in `~/Watchtower/agent_secrets.db` — `keymaker_peel.load("NGS_NODE_TOKEN")` returns an empty list there.

It is in `C:\Users\super\.nougen\secrets\shards_secrets.db`, table `secrets`, columns `id, secret_key, secret_value, last_rotated`. Note the schema differs from the sibling CSV ledger (`id, secret_key, fingerprint_sha256_12, encrypted, last_rotated`) — the DB column is `secret_value`, not `encrypted`. Reading the CSV's column names and assuming the DB matches is the trap.

Retrieve with `keymaker_peel.unwrap(secret_value)` from `~/.nougen/bin`. Measured: 359 raw chars, **1** DPAPI layer, 43 chars plaintext. `last_rotated` reads 2026-08-14 18:22:14 — note this does **not** match the "secret rotated" event recorded in `20260818T023345Z`, so either that rotation happened at the Cloudflare/Space edge rather than in blade's vault, or the ledger was not updated. Worth reconciling.

Verified working: `POST https://shards.nougenai.com/search` with `X-NGS-Token` -> **HTTP 200**.

Quoting note for anyone scripting against blade: its SSH shell is `cmd.exe` and nested quotes get mangled. Both `powershell -EncodedCommand <utf16le-b64>` and `python -c "import base64;exec(base64.b64decode('<b64>'))"` pass through cleanly. Plain nested quotes do not.

## ASK — phoebus needs Remote Login on for the return direction

Password-gated, so no agent should flip it:

```
System Settings -> General -> Sharing -> Remote Login
```

Blade's key is already in `/Users/kushboygroup/.ssh/authorized_keys` (content-verified). Phoebus host fingerprints for blade to pin instead of TOFU:

```
ED25519  SHA256:203Aq4Yu8B9b7Hnc0twjbw51Mm1dTPjWbYmPkL54LNQ
RSA      SHA256:ng0xlrKzs7DXv0DpV1bu8SqUcYHE/d4I+r3gxgZo6/c
ECDSA    SHA256:QwhGCAzfOKM9n0es4R1M5H3swMID8/5402yoTNfWTtE
```

## Open, unrelated to SSH

- HF Space `nougenai/NouGenShards` is **503** — `Initialization step 'hf-mount' failed`. It is the `nougen-shard-failover` worker's PRIMARY origin, so every public NGS hostname is currently being served by blade's fallback.
- Blade reports `public_ready: false` and `hud_auth_configured: false` while serving every public hostname. Phoebus has HUD auth set and reports `public_ready: true`.
- The failover worker has no phoebus origin, and all three of phoebus's tunnel hostnames (`ngs`, `mcp`, `kaedra`) now resolve through the worker — so phoebus has no public route at all. Adding it as a third fallback needs a new tunnel route plus DNS; `wrangler` is not installed on phoebus.

No secrets in this leg — paths, fingerprints and public key halves only.
