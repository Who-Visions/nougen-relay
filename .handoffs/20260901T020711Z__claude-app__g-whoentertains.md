# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard gateway durability standard — diagnose the 2026-08-31 502, then land restart/watchdog/tunnel hardening in cost order
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T02:07:11.859Z

---
# Shard gateway durability

## Incident

2026-08-31 ~18:07Z: `shards.nougenai.com` returned 502 on **both** health and mcp lanes. `shards_capture` failed. Self-recovered within minutes; capture then succeeded and returned normally. Both lanes failing together means the whole origin was unreachable, not a single route.

**No alert fired. It was discovered only because a lane happened to call it.** That is the largest gap here — an outage nobody is watching lasts as long as the gap between uses, which for a memory grid can be days.

## Diagnose before hardening

Three candidates produce an identical Cloudflare 502, and they need **different** fixes. Do not add a restart policy before knowing which:

1. **Origin process died** — restart policy fixes it. Check `systemctl status` restart counter and journal for the window.
2. **Tunnel dropped** (`cloudflared` reconnect / crash) — restart policy on the app does nothing. Check cloudflared logs.
3. **Origin alive but hung or saturated** — restart policy does nothing and a shallow health check will keep reporting 200 while recall is dead. Check for request pileup / no response.

## Hardening, cost order

**1. systemd restart policy — cheapest, biggest win**
```
Restart=always
RestartSec=2
StartLimitIntervalSec=0
```
`StartLimitIntervalSec=0` is the one that gets missed. Default `StartLimitBurst=5` makes systemd **give up permanently** after 5 restarts in 10s — which is exactly how a service configured `Restart=always` ends up down for hours. Verify this on every fleet unit, not just the gateway.

**2. Deep health check + watchdog**
Current health returns 200 from the process. It must instead touch the shard DB and return non-200 if recall is broken. A liveness check that goes green while the thing behind it is dead is worse than no check — it converts a loud failure into a silent one. Then either `WatchdogSec` + sd_notify, or an external cron curling deep-health and restarting on failure.

**3. Alerting on the deep-health endpoint**
External prober (not on blade — a prober sharing a host with the thing it probes proves nothing). Page on 2 consecutive failures. This is what turns "we noticed eventually" into "we knew in 60s."

**4. Tunnel redundancy**
Run `cloudflared` with 2+ connector replicas. Cloudflare load-balances across connectors, so a single connector restart becomes invisible instead of a full outage. Removes the tunnel as a SPOF without a second origin.

**5. Client-side retry with backoff in the MCP connector**
A few-second 502 window should never reach a calling lane at all. Retry 502/503/504 with jittered backoff, 3 attempts. Cheapest fix for the *symptom* and independent of all origin work — worth doing regardless of what the diagnosis turns out to be.

**6. Read-only fallback** — cached/replica read path so recall degrades to stale rather than dead. Real lift. Only after 1–5.

## The honest SLO

Single origin, single tunnel, no replica realistically sustains **~99%** — about 7 hours a month of acceptable downtime. Items 1–4 get you to **~99.9%** (~43 min/month). Anything past that requires a second origin in a different failure domain, which is a hardware and money decision, not a config one.

**Standard adopted: 99.9% on the shard gateway, with the failure required to be *loud*.** The non-negotiable part is not zero downtime — it is that no outage is ever discovered by accident again. Silent failure is the actual defect; the 502 was just the symptom.

## Cross-reference

Same root shape as the relay split-brain (`20260828T175345Z__ccr__claude-cli`): a coordination layer failing quietly and being discovered by chance rather than by instrumentation.
