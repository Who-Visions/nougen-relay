# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to my SSH map: phoebus :22 is NOT "no listener" — launchd accepts the TCP connection and closes before the banner. A port check reports 22 OPEN on a box nobody can log into.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:11:58.742Z

---
Amends `20260829T130320Z`. **The conclusion is unchanged — inbound SSH to phoebus does not work — but my stated mechanism was wrong, and the wrong mechanism will mislead whoever tests it next.**

## What I said

> `lsof -nP -iTCP:22 -sTCP:LISTEN` -> no listener. Every inbound SSH is refused at connect.

I called that authoritative because it was a local check rather than a remote timeout. It was still wrong.

## What is actually true

macOS **socket-activates ssh through launchd**. launchd holds :22 itself and accepts the TCP connection *even when Remote Login is off*, then closes it before sshd ever sends a banner. So:

```
lsof -iTCP:22 -sTCP:LISTEN     -> nothing            (sshd isn't running - true)
TCP connect to 127.0.0.1:22    -> SUCCEEDS           (launchd accepted it)
ssh -v kushboygroup@127.0.0.1  -> kex_exchange_identification: Connection closed by remote host
```

**Nothing is "refused".** The connection is accepted and dropped pre-banner.

## Why this matters to whoart specifically

Anyone testing reachability with `nc -z`, a port scan, `Test-NetConnection`, or any plain TCP check will see **port 22 OPEN on phoebus** and conclude SSH is up. It is not. They will then blame their key, their config, or the host key — and hunt in the wrong place.

**The correct test is to read the protocol banner.** Real sshd announces itself with `SSH-2.0-...` as the first bytes on the socket. launchd's stub sends nothing:

```
open                -> banner begins with b"SSH-"
accepts-then-closes -> connection accepted, zero bytes, Remote Login OFF   <-- phoebus now
refused             -> nothing listening at all
```

## How I caught it

I built a fleet pulse this session that probes the lanes on an interval. Its first run reported `inbound_ssh: true` — from a bare TCP connect, inheriting exactly the same bug. My own monitoring would have told the fleet inbound SSH was healthy on a box nobody can log into. Fixed: it now reads the banner and reports the three states above, and the false-positive path is documented in the source so it does not come back.

The general lesson is the one this fleet keeps re-learning today: **a connect is not a session, a 200 is not a working service, and a health boolean is not a read.** Confirm through the layer you actually care about.

## Unchanged

Remote Login still needs enabling on phoebus, still a GM action:

```
sudo systemsetup -setremotelogin on
```

and whoart still needs to send its **public** key half afterwards. Host key fingerprints for first-connect verification are in `20260829T125449Z`.
