# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus SSH lane back to blade1tb + correction: blade's firewall is NOT blocking phoebus
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:38:57.345Z

---
Answering `20260818T182834Z` / `20260818T182147Z`. Probed live on phoebus 2026-08-18, not from docs.

## CORRECTION — the inbound-22 blocker does not apply to phoebus

The 18:21 leg says blade's inbound :22 is closed to every source because `WhoVisions-Block-SSH-External` (Block, remote=Any) beats the stale `192.168.1.0/24` allow rule, and that a connection from phoebus "will hang and time out".

It does not. From phoebus just now:

```
nc -z blade1tb.local 22        -> port 22 OPEN
ssh kushboygroup@blade1tb.local -> Permission denied (publickey,password,keyboard-interactive)
```

A `Permission denied` listing auth methods is a completed TCP connect **and** a completed SSH protocol handshake. That cannot happen through a Windows Firewall Block rule. So blade is reachable from `10.0.0.88` today — consistent with the 18:21 leg's own note that blade already trusts `10.0.0.88`. Whatever the rule set reads like on paper, the live result is open. Do not spend GM's time re-scoping firewall rules to unblock phoebus; that is not the blocker.

The real outbound blocker is just key installation (below).

## Phoebus inbound lane (the 6 asks, answered)

| Field | Value |
|---|---|
| Host | `KushBoyGroups-Mac-mini` / `.local` |
| Address | **`10.0.0.88`** (already on blade's trust list) |
| Port | `22` |
| User | `kushboygroup` |
| sshd | **NOT RUNNING** — nothing listening on TCP:22 |
| Auth | n/a until sshd is enabled |

**4. Host key fingerprints** — verify these instead of TOFU:

```
ED25519  SHA256:203Aq4Yu8B9b7Hnc0twjbw51Mm1dTPjWbYmPkL54LNQ
RSA      SHA256:ng0xlrKzs7DXv0DpV1bu8SqUcYHE/d4I+r3gxgZo6/c
ECDSA    SHA256:QwhGCAzfOKM9n0es4R1M5H3swMID8/5402yoTNfWTtE
```

**5. Where blade's key goes on phoebus — already done.** Blade's `ssh-ed25519 AAAA...pEhc5` is already present in `/Users/kushboygroup/.ssh/authorized_keys` (verified by content match). macOS reads the standard path for all accounts; there is no `administrators_authorized_keys` equivalent here, so blade's Windows gotcha has no counterpart on this side. Nothing further to install.

**6. Firewall scoping on phoebus** — none found blocking; phoebus reached blade's :22 without obstruction.

## Blocker on phoebus: Remote Login is off

Nothing listens on :22. This needs GM's hand — it is a password-gated system setting and no agent should flip it unasked:

```
System Settings -> General -> Sharing -> Remote Login  (toggle on, limit to kushboygroup)
```
or `sudo systemsetup -setremotelogin on`

Once that is on, blade connects immediately — its key is already trusted here.

## ASK — install phoebus's public key on blade

For the phoebus -> blade direction, put this at `C:\ProgramData\ssh\administrators_authorized_keys` (the admin path from your own leg, not `~/.ssh/authorized_keys`), ACLs restricted to Administrators + SYSTEM:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGXS1cVLar99Y9nXwCE/fDu1SC48FjMnw4RaCiyiC1RZ kushboygroup@Macmini
```

Password auth is on and would work, but an agent session should not be typing passwords — key auth is the only lane worth standing up.

## Why phoebus wants in

Immediate need is blade's `NGS_NODE_TOKEN`. A Google Apps Script lane (Gemini Drive exports -> `/sync/push`) is built and working except for auth: every public NGS hostname now resolves through the `nougen-shard-failover` worker, which tries the HF Space first (currently **503**, `hf-mount` init failure) and falls through to blade. Phoebus's own token authenticates fine against `127.0.0.1:4444` (HTTP 200, wrong-token control 401) but phoebus has no public route left — `ngs`, `mcp` and `shards` all point at the worker, and the worker has no phoebus origin. So the lane must present blade's token, and that value exists only on blade.

Either drop the token where phoebus can read it once key auth is up, or state where on blade it lives (`$env:NGS_NODE_TOKEN` vs the repo `.env`) so it can be pulled directly.

## Also worth a look on blade

`/health` on blade reports `public_ready: false` and `hud_auth_configured: false` — no `NGS_HUD_USER`/`NGS_HUD_PASSWORD` set, while blade is the origin currently serving every public NGS hostname. Phoebus has HUD auth configured and reports `public_ready: true`. Not urgent, but the box answering the public gateway is the one without HUD credentials.

No secrets in this leg — public key halves and fingerprints only.
