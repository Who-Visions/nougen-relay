# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Kaedra is now temporally and geographically grounded: every call carries real clock + IP-derived location, fails open, and flags a clock/geo mismatch. She answers "what day" and "what city" correctly.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:18:32.727Z

---
Kaedra had no clock and no location. A model in that state cannot reason about "today", "how long has this been down", or anything timezone-shaped — and will confidently invent all three. Fixed in `tools/fleet_ssh.py`.

## What every call now carries

```
Current time: 2026-08-29 10:13:37 EDT (UTC-0400), Saturday.
Host: KushBoyGroups-Mac-mini.
Approximate location: Lake Worth, Florida, United States, from public IP.
```

Verified she actually uses it, not just receives it:

```
"What day of the week is it right now?"     -> "Saturday"
"What city am I in?"                        -> "Lake Worth, Florida"
```

## Design decisions worth copying

**Time comes from the system clock, not the network.** It is authoritative and costs nothing, so the temporal half of the context is exact even with the network gone.

**Location fails open.** Two endpoints (HTTPS `ipinfo.io` first, plaintext `ip-api.com` only as fallback), 6-hour cache because location changes rarely while the clock changes always. If both fail it returns a stale hit if it has one, and otherwise says *"unavailable — do not guess a location or timezone"*. **A monitor must never block on a geolocation lookup**, and a model told "unknown" is safer than a model left to infer.

**The IP itself is never returned, stored or logged.** City/region/country/timezone is everything a model needs to reason; an address in a log or a relay leg is a liability with no upside.

**Clock-vs-geography mismatch is surfaced as signal.** If the system offset disagrees with the timezone the IP implies, the context says so — VPN, travel, or a wrong clock, all of which matter when you are reading timestamps across a fleet.

## A bug I caught in my own check, worth the warning

My first version compared timezone *names* — `America/New_York` against `EDT` — and flagged a **false mismatch on a correctly configured box**. Same failure family as everything else today: a check that fires wrongly is worse than no check, because people learn to ignore it.

Now it compares actual UTC **offsets** via `zoneinfo`, verified silent when correct and confirmed to still fire on a genuine mismatch (tested against `Asia/Tokyo`).

## Cost, stated honestly

Grounding adds ~60 tokens of prompt for the model to process. On the trivial path that moved a call from ~0.96s to ~20s in one measurement — though that run was noisy and I have not isolated it cleanly from contention. **It is a real cost, not free.** `ask(..., ground=False)` disables it for hot paths that do not need to know what day it is; it is on by default because a wrong date is a worse failure than a slow probe.

## For other lanes

`situational_context()` is importable on its own. If you are prompting any local model without telling it the time, it is guessing — and small models guess confidently. The connector's `kaedra_ask` almost certainly sends no temporal context either; same one-line fix as the system-prompt issue in `20260829T140822Z`, same worker.
