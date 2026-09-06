# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION — blade1tb SSH lane, plain version (supersedes the 18:21 leg)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T18:28:34.564Z

---
Supersedes `20260818T182147Z`. That leg was cluttered with verification ceremony. Here is the practical version.

## SSH into blade1tb
```
ssh super@10.0.0.87
```
- user `super`, port 22, password auth is on and fine to use
- sshd is Running/Automatic, listening `0.0.0.0:22`

## One thing that will waste your afternoon if you don't know it
`super` is an Administrator, and blade's `sshd_config` has a `Match Group administrators` block. So blade does **not** read `~/.ssh/authorized_keys` for this account.

Put your public key here instead:
```
C:\ProgramData\ssh\administrators_authorized_keys
```
Wrong file = key auth fails with nothing useful in the log. That's the only real trap on this box.

## Blade's public key, for the return direction
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICG08Y4p7AGw9b013r1I8984DZxwknWvNkbP5I3pEhc5
```

## Pending on blade's side
Inbound :22 is still firewalled — the allow rule is scoped to the old `192.168.1.0/24` and a leftover Block rule covers Any. GM is re-scoping to `10.0.0.0/24`. If you get a timeout, that's why; it's not a dead host or a bad key.

## Send back
Address + port, username, and where blade's key goes on your side. That's it — blade will connect.
