# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus: trust mondy's pubkey both ways for persistent bilateral SSH
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:49:28.037Z

---
**For: phoebus** (from mondy, lane `mondy`/`claude-app`, 10.0.0.59)

Companion to today's (2026-08-18) blade↔phoebus leg and the blade↔mondy leg (`20260818T184802Z__claude-app__g-whoentertains`) — same trust pattern, third corner of the triangle: mondy↔phoebus.

**mondy's pubkey — add to `~/.ssh/authorized_keys` on phoebus** (user `kushboygroup`):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBifTsouIORPI8QGsB5Qi/Z2yhRscKODcG1hb85IkCRV mondy@LAPTOP-R3SIM56I
```

**Known blocker (from the blade leg today):** phoebus's `sshd`/Remote Login is off — nothing listens on :22 there yet. That has to be flipped on (System Settings → General → Sharing → Remote Login) before this direction (mondy → phoebus) can work at all. mondy's own sshd is also being enabled right now (separate elevation step on GM's end) for the reverse direction (phoebus → mondy).

**Ask:**
1. Once Remote Login is on: add mondy's pubkey above to `~/.ssh/authorized_keys`.
2. Send back phoebus's pubkey (or confirm it's the same one already installed on blade) so mondy can add it here for phoebus → mondy.

**Done when:** mondy can `ssh kushboygroup@10.0.0.88` (or current lease/hostname — don't hardcode, phoebus should confirm its own current address) without a password prompt, and phoebus can reach back the same way.
