# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Tunnel root cause: start_grid.py duplicate-guard FAILS OPEN, leaking a cloudflared every ~7min (10 stacked); blade round-robins onto wedged connectors — cleanup blocked, needs GM
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T05:14:59.505Z

---
**Continues** the tunnel work after `20260830T045719Z` (BLADE_TIMEOUT_MS fix). blade's edge-unreachability is now root-caused.

## Symptom
`https://blade.nougenai.com/mcp/` answers **401 in ~0.2s**, but `https://blade.nougenai.com/health` **hangs 20s+ (http=000)** on the same host, same moment. Split behaviour on one hostname = requests are being distributed across multiple tunnel connectors, some wedged.

## Cause: ten stacked cloudflared instances
`tasklist` shows **12 cloudflared processes**. Nine are identical `"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel run --token <REDACTED>`, spawned on a regular cadence:
`15:41, 15:48, 22:48, 22:55, 23:02, 23:09, 23:18, 23:24, 23:45` — roughly every 7 minutes.

All run the **same tunnel token**, so Cloudflare sees many connector sets for one tunnel and load-balances across them. Requests landing on a wedged instance hang; ones landing on a live instance return instantly. That is the split behaviour above, and it is why the Worker (edge→origin) consistently stalled while my local probes sometimes succeeded.

## The leak: a fail-OPEN guard
`tools/start_grid.py` → `_start_tunnel_if_needed()`:
```python
out = subprocess.run(["tasklist", ...], capture_output=True, text=True, timeout=15).stdout
already = exe_name.lower() in out.lower()
except Exception as e:
    print(f"tunnel probe failed ({type(e).__name__}); assuming not running")
    already = False        # <-- fails OPEN
```
On a saturated box the 15s `tasklist` times out, the guard assumes no tunnel is running, and stacks another connector — which loads the machine further and makes the next probe slower still. **Self-feeding loop**, matching the ~7-minute cadence exactly. The repo's own `gateway_probe.py` comment records blade at **24,523s CPU**, so the saturation precondition is documented.

The guard has a second latent flaw: it matches on the **exe name only** (`cloudflared.exe`), so the unrelated `tools/bin/cloudflared.exe` quick tunnel satisfies it — meaning it can also fail the other way and skip a genuinely needed start.

## Fix — BLOCKED, needs GM (harness gated process termination)
Kill the 8 older leaked duplicates, keep the newest (`58544`):
```
taskkill /PID 3360 /F & taskkill /PID 13728 /F & taskkill /PID 30640 /F & taskkill /PID 20108 /F & taskkill /PID 55100 /F & taskkill /PID 46416 /F & taskkill /PID 56272 /F & taskkill /PID 36552 /F
```
**Do NOT kill**: `23828` (Windows Service), `5468` (`tunnel --no-autoupdate run`, managed by `tunnel_lane.ps1`'s pidfile), `36172` (`tools/bin/cloudflared.exe` quick tunnel → `127.0.0.1:4444`, a different service).

Then verify: `curl -m 20 -o /dev/null -w "%{http_code} %{time_total}\n" https://blade.nougenai.com/health` should stop hanging, and `shards_search` should return **real hits** instead of `(no matches)` once blade serves again.

## Code fix — NOT APPLIED, lane conflict
`tools/start_grid.py` is in another lane's uncommitted set (`M tools/start_grid.py` per the session-start handoff), so per the share-the-field rule I did not touch it. **Lane owner**: make the guard fail **CLOSED** (on probe failure, do not spawn), and match on the resolved full exe path rather than the bare name. `tunnel_lane.ps1` already models the right pattern with a pidfile guard (`"tunnel already running (pid $running)"; break`).

## Note
`tunnel_lane.ps1` and `whoart_tunnel.ps1` were both cleared as the leak source — the former guards correctly via pidfile, the latter manages SSH tunnels and spawns no cloudflared. Scheduled tasks were also cleared: all three NouGen tasks are logon-triggered with **no repetition interval**.
