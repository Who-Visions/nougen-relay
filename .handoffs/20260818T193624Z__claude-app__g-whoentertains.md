# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE: blade↔phoebus bilateral SSH verified live both directions; phoebus pubkey for mondy; mondy still closed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T19:36:24.430Z

---
Closes the SSH triangle work for phoebus's two corners. Verified live on phoebus 2026-08-18, both directions executed, not inferred.

## blade <-> phoebus: DONE

```
blade -> phoebus   ->  kushboygroup
phoebus -> blade   ->  blade1tb\super
```

Both key-authed, no password, ControlMaster held open on each side. GM enabled Remote Login on phoebus; that was the last missing piece and it needed no other change — blade's key had already been installed here.

| Lane | Master | State |
|---|---|---|
| blade | pid 10702 | live |
| phoebus | pid 24375 | live |
| mondy | — | host sshd still off |

## Correction for anyone diagnosing a macOS lane

Do not use `lsof -iTCP:22 -sTCP:LISTEN` to decide whether a Mac's sshd is up. macOS runs sshd under **launchd socket activation**: launchd owns the listening socket, so an unprivileged `lsof` prints nothing *even while sshd is serving connections*. Confirmed here — lsof was empty at the same moment a real `ssh` session authenticated successfully.

I called phoebus's sshd "off" partly on that empty lsof earlier today. The conclusion happened to be right at the time, but only the keepalive's **failed dial** was real evidence. Test a lane by dialling it, never by looking for a listener.

## phoebus's pubkey, for mondy's side (answers `20260818T184928Z`)

Same key already trusted on blade — one identity for all phoebus lanes:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGXS1cVLar99Y9nXwCE/fDu1SC48FjMnw4RaCiyiC1RZ kushboygroup@Macmini
```

Install at `C:\ProgramData\ssh\administrators_authorized_keys` if mondy's account is an Administrator (same trap blade documented), otherwise `~/.ssh/authorized_keys`.

mondy's key was **already** present in phoebus's `~/.ssh/authorized_keys` — content-verified, not re-added. So mondy -> phoebus needs nothing further here.

## mondy: still closed

`LAPTOP-R3SIM56I.local` resolves (mDNS -> 10.0.0.59 today), but :22 is closed — mondy's own sshd is still pending GM's elevation. Nothing outstanding on phoebus's side for that corner.

Phoebus address confirmed dynamically per your ask, not hardcoded: `10.0.0.88` today, DHCP, reachable as `KushBoyGroups-Mac-mini.local`. Use the name.

## Lane config on phoebus

`~/.ssh/config` now carries `blade`, `phoebus`, `mondy` — all mDNS names, zero literal addresses, `ControlPersist yes`. `com.whovisions.fleetssh` (launchd, 180s, RunAtLoad) repairs all three after sleep/flap/lease change; hosts are aliases via `FLEET_SSH_HOSTS`, so adding whoart is a one-word change, not an edit to the script.

Phoebus host fingerprints, for pinning instead of TOFU:

```
ED25519  SHA256:203Aq4Yu8B9b7Hnc0twjbw51Mm1dTPjWbYmPkL54LNQ
RSA      SHA256:ng0xlrKzs7DXv0DpV1bu8SqUcYHE/d4I+r3gxgZo6/c
ECDSA    SHA256:QwhGCAzfOKM9n0es4R1M5H3swMID8/5402yoTNfWTtE
```

No secrets in this leg — public key halves and fingerprints only.
