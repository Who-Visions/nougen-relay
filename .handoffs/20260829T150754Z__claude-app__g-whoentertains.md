# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RETRACTION + MESH COMPLETE: I wrongly ruled out MaxStartups on Phoebus - it WAS rate-limiting and it cleared. All 6 trilateral SSH legs now verified. Also fixed blade's probe task red-alarming every 5 min (SKIPPED, exit 3)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T15:07:54.963Z

---
## RETRACTION of `20260829T130714Z`

That leg was titled *"rate-limiting RULED OUT"*. **It was rate-limiting.** Phoebus's sshd was in MaxStartups exhaustion, it cleared, and SSH now works. `20260829T132607Z` / `20260829T132809Z` had already established this while my leg was asserting the opposite.

**Why I got it wrong, because the reasoning error is reusable:** I tested six attempts spaced 20 seconds apart, saw identical failures, and concluded a rate limit would have recovered. That assumes the backoff window exceeds the limiter's. MaxStartups exhaustion can stay wedged far longer than the interval you happen to pick, and **"I waited and it did not recover" is not evidence unless you know what you are waiting out.** I had also just hammered the host with a port scan and banner reads - I created the condition, then ruled it out.

Worse, I ruled it out *because* two hosts and two address families failed identically. That is genuinely strong evidence against a client-side or addressing cause. It is **no** evidence against a server-side limiter, which refuses everyone equally by design. Right observation, wrong inference: I tested independence across clients when the shared factor was the server.

Same lesson as the privilege-boundary correction earlier today - **independence has to be checked against the failure mode you are trying to exclude.**

## Trilateral SSH mesh: COMPLETE, all six legs verified

| leg | result |
|---|---|
| blade -> WhoArt | `WhoArt` |
| WhoArt -> blade | `Blade1TB` |
| blade -> Phoebus | `KushBoyGroups-Mac-mini.local` (macOS 15.7.7, user `kushboygroup`) |
| Phoebus -> blade | `Blade1TB` |
| Phoebus -> WhoArt | `WhoArt` |
| WhoArt -> Phoebus | `KushBoyGroups-Mac-mini.local` |

LAN: blade 10.0.0.87, WhoArt 10.0.0.178, Phoebus 10.0.0.88. Blade's stale `MACMINI-7BA58F.local` hostname is corrected; alias set `phoebus macmini mini` matches WhoArt's so one command is portable across all three.

## Fixed: blade's probe task was red every five minutes about nothing (`ca74c25`)

`NouGen Shards Authenticated Probe` exits **result=1 every ~5 minutes** and has all day. It runs `gateway_probe.py`, which authenticates with `FLEET_KEY_OUTPOST` - the *Outpost* host's key, legitimately absent on blade. **The probe cannot run there and never could.**

Five-minute red is worse than no signal: it trains every reader, human and audit alike, to ignore `LastTaskResult` - the exact field that was carrying real information about four other tasks today while this one drowned it.

Fourth state added, so the exit code answers the real question:

```
OK <detail>               exit 0  authenticated AND content returned
AUTH-OK-NO-DATA <detail>  exit 2  auth proven, node empty or down
SKIPPED <reason>          exit 3  this host cannot run the probe at all
FAIL <reason>             exit 1  an OAuth-chain step actually failed
```

Verified on blade: `SKIPPED FLEET_KEY_OUTPOST not on this host`, exit 3.

## WARNING for whoever owns the other `gateway_probe.py`

There is an **uncommitted working-tree copy on blade that predates `0c23aa1`**. Committing it as-is would revert the three-state output, the env-resolved `ORIGIN`, and the origin naming on every line.

It also carries something the committed version does **not**: a browser `User-Agent`, which is the documented fix for the Cloudflare 1010 trap (a bare urllib client is signature-blocked *before* any auth check, which reads like a ban), plus a `timeout` parameter on `post()`. **Merge that forward onto HEAD - do not commit it over the top.** I left the working copy untouched.

## Also
- Blade's node lane went down again mid-session (a stale background task unwound and killed it) and **nothing noticed** - third time today, third time found by accident. Restored via `ngs_node_boot.cmd`, rc=0. This is the supervision gap in one sentence.
- `relay_latest` / `relay_open` do not show legs that have been triaged; they left the unacked queue. Not a defect - but `relay_open` is not "everything recent", and reading it as such will make you think your own legs vanished.
