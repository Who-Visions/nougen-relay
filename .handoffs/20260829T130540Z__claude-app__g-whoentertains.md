# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Trilateral SSH mesh: blade-whoart is bidirectional and verified. Phoebus is UP at 10.0.0.88 but its sshd resets at kex for BOTH peers - needs hands on the Mac. Blade carried a STALE phoebus hostname, now fixed
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:05:40.324Z

---
## Goal
blade1tb, WhoArt and Phoebus all able to SSH each other, so any lane can reach any box.

## Live LAN map (probed, not remembered)
| host | address | evidence |
|---|---|---|
| blade1tb | 10.0.0.87 | local `arp -a` interface |
| WhoArt | 10.0.0.178 | SSH banner `OpenSSH_for_Windows_9.5`, `hostname` -> `WhoArt` |
| Phoebus | 10.0.0.88 | `KushBoyGroups-Mac-mini.local` resolves and pings, TCP :22 accepts |

## Status of all six legs
| leg | state |
|---|---|
| blade -> WhoArt | **WORKS** |
| WhoArt -> blade | **WORKS** (verified via nested ssh, returns `Blade1TB`) |
| blade -> Phoebus | **FAILS**: `kex_exchange_identification: Connection reset by peer` |
| WhoArt -> Phoebus | **FAILS**: `Connection closed by 10.0.0.88 port 22` |
| Phoebus -> blade | untestable until inbound works |
| Phoebus -> WhoArt | untestable until inbound works |

## Fixed: blade was carrying a STALE Phoebus hostname
Blade's `~/.ssh/config` had `HostName MACMINI-7BA58F.local`. That name no longer resolves - the Mac was renamed. **WhoArt's config already had the current name** (`KushBoyGroups-Mac-mini.local`), so blade sat unable to reach a host that was up the whole time.

This is the exact failure blade's own config header warns about, one level over: the header says never write a literal IP because leases rot, and mDNS names track the lease. True - but a NAME rots too when the machine is renamed, and nothing checked it. Corrected, alias set aligned with WhoArt's (`phoebus macmini mini`) so one command is portable between boxes. Backup at `~/.ssh/config.bak.<timestamp>`.

**Cross-check your own config against the live name before trusting it.** Two boxes disagreed about what this machine is called and only one was right.

## The remaining blocker is on Phoebus and needs hands
It is not a blade problem and not a key problem. **Both** peers are refused at `kex_exchange_identification` - before authentication is ever attempted - so no key or `authorized_keys` change on either side can fix it. TCP connects, then sshd drops the connection.

Likely, in order: macOS Remote Login off (or toggled off since the last successful session), the macOS firewall blocking incoming with no allow rule for sshd, or sshd rate-limiting (`MaxStartups`) - I did probe it repeatedly while identifying it, so a patient retry is running.

**GM / anyone at the Mac**: check System Settings -> General -> Sharing -> Remote Login, and System Settings -> Network -> Firewall. Once inbound works, the key exchange in both directions is a five-minute job and I will finish it.

## What is ready the moment Phoebus answers
- Blade's config now points at the correct name with the right user (`kushboygroup`).
- WhoArt's config already had a correct `phoebus macmini mini` block.
- Both boxes have ed25519 keys; only `authorized_keys` entries on the Mac are missing.

Note for whoever does it: on the Mac, keys go in `~/.ssh/authorized_keys` (unix path). On WhoArt, Windows OpenSSH uses `C:\Users\super\.ssh\authorized_keys`, and for an admin account `C:\ProgramData\ssh\administrators_authorized_keys` instead - putting an admin's key in the user file is the usual reason a Windows leg silently keeps failing.
