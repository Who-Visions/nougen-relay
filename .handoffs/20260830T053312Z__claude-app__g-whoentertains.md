# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Tunnel leak STOPPED at source: start_grid.py guard now fails CLOSED and matches the exact binary (live-verified counting 9 leaked connectors); killing the 8 duplicates still needs GM
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T05:33:12.920Z

---
**Continues** `20260830T051459Z`. GM confirmed no lane is working `tools/start_grid.py`; verified independently — `relay_claim_list` shows no claim on it (only an unrelated relay-daemon leg), so I took it.

## Patched: `_start_tunnel_if_needed()` in `tools/start_grid.py`
Two defects fixed:

1. **Fails CLOSED instead of open.** Was `except Exception: already = False` → spawn anyway. The probe's own failure mode is a saturated box, which is precisely when another connector is the worst response: each extra instance loads the machine further, slowing the next probe into the same timeout. That loop leaked 9 connectors, one every ~7 min. Now it returns without spawning and says so. A missing tunnel is visible and recoverable; a silent pile-up is not.
2. **Matches the exact binary, not the bare image name.** `tasklist /FI "IMAGENAME eq cloudflared.exe"` was satisfied by the unrelated `tools/bin` quick tunnel, so the guard could also fail the *other* way and suppress a genuinely needed start. Now compares resolved `ExecutablePath` and requires a `tunnel\s+run` command line.

Probe timeout is env-resolvable (`NOUGEN_TUNNEL_PROBE_TIMEOUT_S`, default 20) rather than the old inline `15` — Rule 0.2.

**Security note for reviewers**: the new probe reads `CommandLine`, which contains `--token <JWT>`. It counts matches and returns an integer only — it never prints or returns the command line, because this function's output goes to `ngs_node.log`.

## Verified live, not just compiled
- `py_compile`: OK
- Ran the new probe against real process state: returns **9** — exactly the 9 leaked `--token` connectors, correctly excluding `36172` (`tools/bin` quick tunnel → :4444) and `5468` (`tunnel --no-autoupdate run`). The guard now trips, so **no further duplicates can stack**.

Left untouched: the unrelated uncommitted REPO fail-loud change already in that file (14 lines, another lane's, not reverted). Not committed — staging is the file owner's call, and a sweep commit would pull in their work.

## STILL BLOCKED — needs GM
The patch stops new leaks but does **not** clear the 9 already running. Until they are reaped, blade keeps round-robining onto wedged connectors and `shards_search` keeps returning `(no matches)` from the Space replica:
```
taskkill /PID 3360 /F & taskkill /PID 13728 /F & taskkill /PID 30640 /F & taskkill /PID 20108 /F & taskkill /PID 55100 /F & taskkill /PID 46416 /F & taskkill /PID 56272 /F & taskkill /PID 36552 /F
```
Keep `58544` (newest connector), `23828` (Windows Service), `5468`, `36172`. Harness gates process termination; not worked around.

**Done-when**: `curl https://blade.nougenai.com/health` stops hanging, and `shards_search` returns real hits instead of `(no matches)`.
