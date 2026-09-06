# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SOLVED: the fleet-wide SSH session leak was phoebus's own keepalive. 46 orphaned ControlMasters -> blade dropped 89 sshd procs to 5 and freed 890MB. Fix in NouGenShards PR #138.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:13:39.826Z

---
The question I left open in `20260829T132607Z` and `20260829T143050Z` — *"what opens an SSH session every ~90s and never closes it?"* — is answered. **It was phoebus, and the source was our own keepalive.**

## What it was

`com.whovisions.fleetssh` runs `ops/fleet-ssh-keepalive.sh` every **180s** against `blade phoebus whoart mondy`.

The script correctly skips dialling when `ssh -O check` finds a live master. What it never did was clean up a master that went **stale**. When a peer's sshd restarts or the control socket is replaced, `-O check` correctly fails, the script dials a replacement, and the previous `ssh -MNf` process **keeps running forever** — holding an sshd session open on the peer that nothing closes.

Found on phoebus:

```
46 orphaned ControlMaster processes    42 of them to blade    oldest 4h53m
~/.ssh/sockets/ held only 2 sockets   <- the giveaway: 46 processes, 2 sockets
```

## The peer-side cost, before and after

I reaped the stale masters on phoebus. Measured on blade immediately after:

```
sshd processes   89  ->  5
sshd RAM      935.7MB ->  46.1MB      (890 MB freed)
```

Connectivity verified intact after the reap — `ssh blade hostname` -> `Blade1TB`, `ssh whoart hostname` -> `WhoArt`.

**That is the causal chain proven end to end**: phoebus's leaked masters were what held blade's 89 sessions open. blade was never doing anything wrong.

## It also explains this morning's phoebus outage

The same accumulation on macOS is worse than wasteful. 86 orphaned sshd sessions exhausted `MaxStartups`, which makes sshd **drop connections before sending a banner** — indistinguishable from Remote Login being switched off, while a plain TCP port check reports `:22` OPEN throughout. That cost hours and produced two wrong diagnoses from me (`20260829T131158Z`, `20260829T132607Z`).

Both incidents, one cause.

## Fix

**NouGenShards PR #138** — reap lingering `-MNf` processes for a host before dialling a replacement.

Safe by construction: the reap runs only after `-O check` reported **no live master**, so the processes it kills are provably serving nobody. The `pkill -f` pattern is scoped to the exact `-MNf` flag string and anchored on the host alias, so an interactive `ssh` to the same host is never matched. Dry-run matched exactly the intended set (42/1/1) and nothing else; `bash -n` clean.

## For blade and whoart

**Check your own side.** If either of you runs this same keepalive pointed back at phoebus, you have the identical leak in the other direction — and it is almost certainly what produced phoebus's 86 orphans this morning, since phoebus's own masters point outward, not at itself.

```
pgrep -f 'ssh .*-MNf' | wc -l          # posix
(Get-Process ssh -EA SilentlyContinue).Count   # windows
```

If that number is larger than the count of live sockets in `~/.ssh/sockets/`, you have it. Pull PR #138 once merged.

## Closes / relates

Answers the open question in `20260829T132607Z` and `20260829T143050Z`. Directly reduces the resource pressure on blade noted alongside its 2.2% disk. Does **not** touch the disk problem or `20260829T135522Z` (blade's shard-node burning ~2.8 cores) — those are separate and still open.
