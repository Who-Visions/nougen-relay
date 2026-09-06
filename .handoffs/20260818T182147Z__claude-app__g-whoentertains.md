# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Phoebus &lt;-&gt; blade1tb bilateral SSH: blade's lane details + firewall blocker, need phoebus's lane back
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:21:47.893Z

---
## Situation
GM wants bilateral SSH between **phoebus** and **blade1tb**. Below is blade's side, probed live 2026-08-18 (not from docs — CLAUDE.md's SSH facts are stale, see Blocker).

## Blade1tb inbound lane (verified live)

| Field | Value |
|---|---|
| Host | `BLADE1TB` |
| User | `super` |
| Address | **`10.0.0.87`** (Wi-Fi, DHCP — re-verify per session) |
| Port | `22` |
| sshd | Running, StartType Automatic, listening `0.0.0.0:22` |
| Auth | `PubkeyAuthentication yes`, `PasswordAuthentication yes` |

`ssh super@10.0.0.87`

## ⛔ BLOCKER — inbound 22 is currently closed. Do not attempt yet.

Two firewall problems, both on blade, both needing GM's hand (I am not touching his own security controls unasked):

1. `WhoVisions-SSH-LAN-Only` **allows only `192.168.1.0/24`** — but blade now lives on `10.0.0.87`. The allow rule is scoped to a subnet this machine left. Same stale value as the CLAUDE.md docs (`192.168.1.16`), so this is one stale fact with two symptoms.
2. `WhoVisions-Block-SSH-External` is **Block, remote=Any, port 22**, and in Windows Firewall **Block beats Allow**. So inbound 22 is closed to every source regardless of subnet.

Until GM re-scopes those, a connection from phoebus will hang and time out — **that is a firewall result, not a dead host or a bad key.** Diagnose in that order.

## ⚠️ GOTCHA — the #1 cause of silent Windows key-auth failure

`super` **is an Administrator** on blade. `sshd_config` carries a `Match Group administrators` block, so blade does **NOT** read `~/.ssh/authorized_keys` for this account.

Phoebus's public key must be installed at:
```
C:\ProgramData\ssh\administrators_authorized_keys
```
Putting it in `C:\Users\super\.ssh\authorized_keys` will fail silently with no useful log line. That file also needs its ACLs restricted to Administrators + SYSTEM or sshd refuses it.

## Host key verification
Blade's host key fingerprints are ACL-locked and need elevation to read; I did not fabricate them. GM can produce them with an elevated shell:
```
ssh-keygen -lf C:\ProgramData\ssh\ssh_host_ed25519_key.pub
```
Until then phoebus is trusting-on-first-use. Compare before accepting.

## Blade's public key, for the return direction
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICG08Y4p7AGw9b013r1I8984DZxwknWvNkbP5I3pEhc5
```
(`~/.ssh/id_ed25519.pub`. Trailing comment is a stock `your_email@example.com` placeholder — cosmetic, harmless.)

## ASK — phoebus, send back your lane so blade can SSH to you
1. Reachable **address + port** on the LAN (blade is on `10.0.0.0/24`; it already trusts `10.0.0.178` and `10.0.0.88`).
2. **Username** to connect as.
3. Is sshd up, and which auth methods are enabled?
4. Your **host key fingerprint**, so blade verifies instead of blind-TOFU.
5. Where blade's public key above should be installed on your side.
6. Any firewall/subnet scoping of your own — state it up front so we don't repeat blade's mistake.

## Done when
Both directions authenticate by key, each side has verified the other's host key fingerprint, and neither is relying on password auth.

No secrets in this leg: public keys and fingerprints only. Nobody should ever relay a private key or password — send public halves and install them locally.
