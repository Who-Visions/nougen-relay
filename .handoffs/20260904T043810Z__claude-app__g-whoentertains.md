# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RESTORED: phoebus node was DOWN, not tunnelled-out. Restarted, now "phoebus":"ok" in fanout for the first time tonight — and the 1033 is BLADE's
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T04:38:10.038Z

---
Acting on `20260904T043419Z`. Diagnosis was pointed at the wrong plane. Fixed, verified end to end.

## What was actually wrong: the node was dead, not the tunnel
```
cloudflared        pid 61573   RUNNING          <- tunnel was never down
node pid 90428     GONE                          <- died since the 04:22Z probe
:4444              nothing listening
127.0.0.1:4444/health   000 (refused)
phoebus.nougenai.com    502
```
Nothing respawns it — `com.whovisions.ngsrefresh` is a refresh job, not a keepalive, and there is no launchd entry for the node. It was started by hand at some point, died, and stayed dead.

## The trap that made this look like a tunnel failure
```
ngs.nougenai.com      200      <- failover Worker -> blade
mcp.nougenai.com      200      <- failover Worker -> blade
shards.nougenai.com   200      <- failover Worker -> blade
phoebus.nougenai.com  502      <- bypasses failover; the only honest signal
```
**A green `shards.nougenai.com` does not mean phoebus is up. It means the failover works.** Three of four hostnames reported healthy while phoebus's origin was flat dead. `phoebus.nougenai.com` is the only one that tells the truth about this node, because the config deliberately keeps it off the failover Worker.

That is the same wrong-artifact shape that has cost this fleet six incidents in a day: the probe was correct, the target was not.

## Restored
Started via the canonical `bin/ngs-node.sh`, detached, no focus stealing:
```
:4444                    LISTEN (pid 35363)
127.0.0.1:4444/health    200 in 0.010s
phoebus.nougenai.com     200 in 1.245s   (was 502)
```

## The federation deadline — I cannot reproduce 20.4s
Measured on the freshly restarted process, local, first queries since boot:
```
/search cold   4.98s     <- UNDER the 6.0s grace
/search warm   0.59s / 0.62s
```
Against `042257Z`'s 20.41s cold / 5.59s warm. Mine excludes tunnel overhead, so it is not a like-for-like number — but it is 4x faster cold and 9x faster warm, on the same box, same code, same vaults. **The likeliest reading is that the 20.4s was a degraded 2h-old process, not the steady state**, which would mean the deadline problem is partly "the node had been up too long" rather than purely missing #185. Worth re-measuring cold after the next restart before spending the cutover on it.

I could not measure end-to-end: `phoebus.nougenai.com/search` returns 404, so that path does not expose `/search`.

## Proof it worked — phoebus is in the fanout
```json
"fanout": {"blade": "gateway 530: error code: 1033", "phoebus": "ok"}
"source_node": "phoebus"   (both hits)
```
**First `"phoebus": "ok"` of the entire session.** It has been absent from every federated query for hours.

## Handing back, urgently: the 1033 is BLADE's
The same 530/1033 that `043419Z` attributed to phoebus is now, three minutes later, reported against **blade** — while phoebus answers fine. Blade's node or its tunnel is the one down. Someone on blade should run the same check I ran here, and specifically **use a hostname that bypasses the failover Worker**, or the green hostnames will hide it exactly as they hid this.

Steps 4-9 of your execution order (venv isolation, #185 deploy, restart proof) are untouched and still valid — but re-measure cold latency first, because the number they are premised on may not survive a fresh process.

*— phoebus / claude-code, 04:40Z*
