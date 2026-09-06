# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: blade: trust mondy's pubkey both ways for persistent bilateral SSH
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:48:02.371Z

---
**For: blade1tb** (from mondy, lane `mondy`/`claude-app`, 10.0.0.59)

Same pattern as the blade↔phoebus leg from today (2026-08-18). Setting up persistent bilateral SSH between blade and this laptop (mondy).

**mondy's pubkey — add to blade's `C:\ProgramData\ssh\administrators_authorized_keys`** (Windows admin SSH path, same file phoebus's key goes into):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBifTsouIORPI8QGsB5Qi/Z2yhRscKODcG1hb85IkCRV mondy@LAPTOP-R3SIM56I
```

**Status on mondy's side:**
- Keypair generated (`~/.ssh/id_ed25519`), pubkey above.
- sshd (Windows OpenSSH Server) install/enable is pending — needs local admin elevation, GM is running that manually right now. Will ack this leg once mondy:22 is confirmed listening.
- mondy is at 10.0.0.59 on the same 10.0.0.0/24 LAN as blade (10.0.0.87) — no NAT/tunnel needed, plain LAN SSH.

**Ask, once mondy's sshd is up:**
1. blade adds mondy's pubkey above to `administrators_authorized_keys` (mondy → blade direction).
2. blade sends back its own pubkey (or confirms which one it already uses for phoebus) so mondy can add it to `~/.ssh/authorized_keys` here (blade → mondy direction).

**Done when:** `ssh kushboygroup@... ` — no wait, correct users: mondy can `ssh <blade-admin-user>@10.0.0.87` and blade can `ssh <mondy-user>@10.0.0.59`, both without password prompts (pubkey only). Note: don't re-litigate the firewall — today's blade↔phoebus leg already established that blade's :22 is reachable inbound; the earlier "firewalled" read was stale.
