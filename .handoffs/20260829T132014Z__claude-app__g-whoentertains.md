# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of Kaedra's ~30s "cold load": heartbeat.py evicted the pinned model every 285s by probing a DIFFERENT one. Fixed. Also RETRACTING my claim that heartbeat was wedged — it was not.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:20:14.845Z

---
Two corrections and one real fix, all on phoebus.

## RETRACTION: heartbeat.py was never wedged

In `20260829T131519Z` I said `com.whovisions.heartbeat` was "alive and has not written a log line since 2026-08-22" and suggested retiring it. **Wrong.** I checked `heartbeat_stdout.log` — launchd's stdout, which the script never writes to. Its actual log is `system_check.log`: **written 09:15 today, 4.4 MB, current.** It has been running correctly the whole time.

That is the fifth time today I drew a conclusion from a single surface without a second read. Same failure shape as the `kaedra_ask` "stripping" claim and the shard write-loss P1. Ignore the retire-it suggestion.

## But it WAS quietly breaking Kaedra — this is the real find

`heartbeat.query_e2b()` probed Ollama every 285 seconds with **`gemma4:e2b`**, while the Kaedra gateway pins **`kaedracode:e2b`** resident via `keep_alive: -1`. Verified on the live box:

```
/api/ps  -> kaedracode:e2b   6.9GB   expires_at 2318-12-09   (i.e. pinned)
/api/tags-> gemma4:e2b is installed
```

Two multi-GB models, one box. **Every heartbeat tick forced a second load that evicted the pinned one**, so the next Kaedra caller paid a full cold reload. That is the "~38s cold load" in the `kaedra_ask` tool description and the ~30s I measured repeatedly today — **not an inherent Kaedra property. A monitor was degrading the thing it monitored, every 4.75 minutes, for as long as both have been running.**

**Fixed** (`heartbeat.py`, backup at `heartbeat.py.bak`):
- probes **whichever model is already resident** (via `/api/ps`), falling back to the old default only if none is loaded — so it never forces a swap, and its latency figure now measures the path real callers actually use
- sends `keep_alive: -1` so the probe cannot reset the pin
- `num_predict` 5 -> 320. At 5, kaedracode:e2b returns an **empty string** (the ~250-290 token preamble), which the old code reported as `DEGRADED` — **it has been reporting a healthy model as degraded**
- `check_port` timeout 0.1s -> 1.0s; 0.1s is under the accept budget of a busy box and produced false OFFLINE

Verified after restart: `resident_model() -> kaedracode:e2b`, `query_e2b() -> NOMINAL`. No eviction.

**Anyone tuning Kaedra latency should re-measure now** — the baseline just changed, and earlier numbers were contaminated.

## fleet_pulse is confirmed working end to end

Kaedra genuinely drives SSH. From the live log:

```
~ CHANGED public.kaedra.nougenai.com: 0 -> 200
~ CHANGED public.mcp.nougenai.com: 0 -> 200
~ CHANGED public.ngs.nougenai.com: 0 -> 200
kaedra: PROBE blade hostname -> Blade1TB
```

She chose a peer and a probe, it executed over SSH, and the output came back to her.

Three defects it exposed **in itself** on first run, all fixed:
1. Every https probe returned 0 — `CERTIFICATE_VERIFY_FAILED`. That interpreter has certifi installed but does not use it, so **the monitor was manufacturing three public outages**. Now uses a certifi-backed context with a verified `curl` fallback. Verification is never disabled.
2. After that fix: **403** on all three, because Cloudflare rejects the default `Python-urllib` agent. Healthy endpoints reporting forbidden. Now identifies as `nougen-fleet-pulse/1.0` -> 200.
3. `eval_count=500` with an empty body — my own truncation guard firing correctly. `num_predict` raised to 900; a tick that runs out of rounds now makes one final probe-free call so the log always ends in an actionable verdict instead of echoing a raw `PROBE` line.

## The pattern, stated once

Five times today a green-looking signal lied: `shards_status`, `coverage.recall_trustworthy`, my `lsof` port check, my own HTTPS prober, and my read of the wrong log file. **A connect is not a session, a 200 is not a working service, a health boolean is not a read, and a quiet log file is not a quiet process.** Every one of these is now commented at the point of fix so the next lane does not re-derive it.
