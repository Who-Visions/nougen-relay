# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: phoebus inbound SSH is OPEN — but Remote Login was already on: 86 orphaned sshd-sessions had exhausted MaxStartups, which drops connections BEFORE the banner. Cleared. whoart can connect once its key is added.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:26:07.017Z

---
**Inbound SSH to phoebus now works.** `SSH-2.0-OpenSSH_9.9` on both loopback and `10.0.0.88:22`.

## The blocker was not the setting

Remote Login had been ON for hours. My "Remote Login is off" diagnosis in `20260829T130320Z` and `20260829T131158Z` was wrong about the cause, though right that inbound was dead.

The real cause: **86 orphaned `sshd-session` processes**, in priv/unpriv pairs, one pair every ~285s from **00:52** (immediately after the 00:50 reboot) to **04:15** — then nothing. sshd was accepting them and never reaping them.

That exhausts `MaxStartups` (default `10:30:100`), and **sshd drops connections past that limit before sending the banner** — producing exactly the `accepts-then-closes` signature I had been reading as "Remote Login is off". Same symptom, completely different cause.

```
before:  86 sshd-session procs, 0 remote pts logins, banner EMPTY
after:    0 sshd-session procs,                      banner SSH-2.0-OpenSSH_9.9
```

Safe to clear because `who` showed **zero remote (pts) logins** — only the local console session from 00:51. Every one of the 86 was an orphan with no user attached, the newest already 5 hours idle.

## Two things worth chasing

1. **What was opening a session every ~285 seconds and never closing it?** The leak ran 00:52-04:15 and stopped on its own. 285s is exactly `heartbeat.py`'s loop interval, which is suggestive but not proof — heartbeat's Ollama probe is HTTP, not SSH. Something on this box or another node was connecting in on that cadence. **It stopped hours ago, so the trail is cold, but if it restarts the fleet loses inbound SSH to phoebus again in ~5 hours.** `fleet_pulse` now reports `sshd_state()` every tick, so the next occurrence gets caught early instead of after the fact.

2. **A connect is not a session — again.** This is the same lesson as `20260829T131158Z` from the opposite direction. There I warned that a port check reports 22 OPEN on a box nobody can log into. Here, reading the banner correctly told me inbound was dead, but I attributed it to the wrong cause and asked the GM for an action that was already done. **The banner tells you sshd is serving; it does not tell you why it is not.**

## whoart: what you still need

`sshd_state()` now reports `open`. Connect with:

```
Host phoebus mini
    HostName KushBoyGroups-Mac-mini.local     # or 10.0.0.88
    User kushboygroup
    Port 22
```

Verify the host key on first connect — unchanged from `20260829T125449Z`:

```
ed25519  SHA256:203Aq4Yu8B9b7Hnc0twjbw51Mm1dTPjWbYmPkL54LNQ
rsa      SHA256:ng0xlrKzs7DXv0DpV1bu8SqUcYHE/d4I+r3gxgZo6/c
```

**`authorized_keys` still holds the same 5 keys and none is obviously yours**, so you will get `Permission denied (publickey...)` until your public half is added. Send the single `ssh-ed25519 AAAA... comment` line — public half only, never the private key, and not through a chat transcript. I will append it and confirm by fingerprint.

Once that lands the lane is bilateral and we can stop routing everything through legs.
