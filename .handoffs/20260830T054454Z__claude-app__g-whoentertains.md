# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Tunnel: 9 duplicate connectors reaped, node proven healthy (5ms local) — but blade still intermittent; the Windows SERVICE is the true tunnel owner, last leaked instance must go
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T05:44:54.449Z

---
**Continues** `20260830T053312Z`. GM approved the reap; executed.

## Done
- Killed 8 leaked `tunnel run --token` connectors (PIDs 3360, 13728, 30640, 20108, 55100, 46416, 56272, 36552) — all confirmed unchanged and still the same leaked command line immediately before termination.
- Stopped the duplicate managed connector `5468` cleanly via `tools/tunnel_lane.ps1 -Action stop` (pidfile-aware) rather than a raw kill. Confirmed: `tunnel_lane.ps1` resolves secret `CLOUDFLARED_NGS_TUNNEL_TOKEN` — the **same NGS tunnel**, so it was a genuine duplicate, not a separate lane.

## Decisive new evidence: the node is NOT the problem
`http://127.0.0.1:8765/health` (bypasses the tunnel entirely): **200 in 0.0056s / 0.0073s / 0.0065s**, 3 for 3.

The NGS node is perfectly healthy at single-digit milliseconds. **The saturated-blade hypothesis is dead** — the `24,523s CPU` note in `gateway_probe.py` does not describe current state. 100% of the fault is in the tunnel/connector path.

## Still intermittent after the reap
`https://blade.nougenai.com/health` x5: `000(25s), 000(25s), 200(14.4s), 000(25s), 000(25s)`. Better than never succeeding, still ~20% and slow.

## Root owner identified — this changes the target
```
SERVICE_NAME: cloudflared   START_TYPE: 2 AUTO_START
BINARY_PATH_NAME: "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel run --token <REDACTED>
```
**The Windows service `Cloudflared` (PID 23828, up since 13:37) is itself a connector for this tunnel, and auto-restarts.** It is the intended single owner. Every `start_grid.py` spawn was a duplicate stacked on top of a service that was already serving — and the guard's entire job was to detect it and stand down. Failing open is what produced the pile.

This also means my earlier "keep 58544" instruction was **wrong**: 58544 is the last leaked instance, not the survivor. Correct end state is the service alone.

## BLOCKED — needs GM (outside the prior approval, which named 8 other PIDs)
```
taskkill /PID 58544 /F
```
Then, to force fresh connector registration now that duplicates are gone (stale registrations from the killed instances may still be draining):
```
powershell -Command "Restart-Service Cloudflared"
```
Keep `23828` (the service itself) and `44592` (`tools/bin` quick tunnel → 127.0.0.1:4444, unrelated).

**Done-when**: `blade.nougenai.com/health` returns 200 consistently and fast, and `shards_search` returns real hits instead of `(no matches)`.

## Note for the start_grid.py lane owner
The patched guard (fails closed, matches resolved `ExecutablePath` + `tunnel\s+run`) now correctly counts the **service's** connector too, so a rerun will stand down instead of stacking. That is the intended behaviour — the service is the owner.
