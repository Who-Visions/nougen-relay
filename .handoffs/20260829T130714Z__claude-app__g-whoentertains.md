# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus SSH: rate-limiting RULED OUT. Accept-then-close at kex from both hosts, both address families, after backoff - sshd is refusing before it sends a banner. Needs hands on the Mac, nothing remote will fix it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:07:14.404Z

---
Amends `20260829T130540Z`, which listed sshd rate-limiting (`MaxStartups`) as a live hypothesis. **It is excluded.**

## Test matrix, all after a backoff window
| attempt | result |
|---|---|
| blade -> `10.0.0.88` forced IPv4 | `Connection closed by 10.0.0.88 port 22` |
| blade -> name, `AddressFamily=any` (resolved IPv6 link-local `fe80::1847:6ef3:6914:4232`) | `Connection closed by fe80::... port 22` |
| WhoArt -> `10.0.0.88` | `Connection closed by 10.0.0.88 port 22` |

**Two source hosts, both address families, spaced attempts after backoff, identical failure.** TCP completes; sshd then closes before sending its identification banner.

## What this rules out
- **Rate-limiting** - it would recover after backoff. It does not.
- **Addressing / mDNS / IPv6** - both families fail identically. (The Mac does advertise an IPv6 link-local over mDNS, and blade's config sets `AddressFamily inet`, so that was a reasonable suspect. It is not the cause.)
- **Keys, `authorized_keys`, `sshd` user config** - the close happens at `kex_exchange_identification`, before authentication is ever attempted. Nothing on the client side reaches far enough to matter.
- **The host being down** - it resolves, pings, and accepts TCP on 22.

## What is left
Accept-then-close before banner points at the listener being held while the service behind it refuses: Remote Login toggled off with the socket still bound, an `AllowUsers`/`DenyUsers` or `hosts.deny` rule, an MDM or security product intercepting, or a broken/failing sshd (full disk, bad host keys).

**No remote action can fix this.** It needs someone at the Mac:
1. System Settings -> General -> Sharing -> **Remote Login** (off, then on).
2. System Settings -> Network -> **Firewall** (allow incoming for Remote Login).
3. If both look right: `sudo launchctl print system/com.openssh.sshd` and `log show --predicate 'process == "sshd"' --last 10m` will say which of the above it is in one line.

Everything on the blade and WhoArt side is ready: correct hostname, correct user, ed25519 keys present. The moment inbound works, both directions are a five-minute job.

blade <-> WhoArt remains **verified bidirectional** and is unaffected.
