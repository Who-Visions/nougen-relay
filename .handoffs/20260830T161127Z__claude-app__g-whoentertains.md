# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TRUE ROOT CAUSE, supersedes all prior: blade C: drive is 100% FULL (0GB of 952GB). SQLite disk I/O errors, node crash-loop, and my "unbounded query cost" finding are ALL symptoms of this
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T16:11:27.346Z

---
**Supersedes `20260830T080424Z` and every earlier root cause in this incident, including my own most recent one.**

## Measured
```
C: free=0GB  size=952.74GB  pct_free=0%
```
`Get-CimInstance Win32_LogicalDisk` on blade1tb. The drive is at **literally zero bytes free**.

## What this explains
`space_sync_daemon.py` has been crash-looping since ~06:18 with:
```
sqlite3.OperationalError: disk I/O error     (core.py:128, PRAGMA journal_mode=WAL)
OSError: [Errno 28] No space left on device  (even the logger cannot flush)
```
A full disk makes SQLite fail every WAL write, which makes the node fail, which makes the pump crash and self-restart every 60s forever. My own shell commands hit the same wall (`sed: couldn't flush stdout`, `head: write error`) — I should have recognised that signal when it first appeared instead of treating it as a shell quirk.

**Retracting my previous conclusion**: I reported "unbounded query cost — a single broad recall can pin the node" as the deepest fragility. The CPU-burn and health-flapping I measured were real observations, but they are **downstream of a disk that cannot accept writes**, not an independent defect. The query-cost hardening is still worth doing, but it is not what broke this.

## Also distinguish two faults that look alike in that log
- `OSError: [Errno 28] No space left on device` → **blade's local C: drive**, this incident.
- `HTTP 502: Bad Gateway` on `/sync/push` → the **remote HF Space** being unreachable, a separate problem. Do not conflate them; GM asked exactly this question and the answer is both, independently.

## Space map so far (~81GB of 952GB accounted for)
| GB | Path | Disposition |
|---|---|---|
| 33.43 | `~/.ollama` | GM's models, re-pullable but in daily use |
| 16.57 | `~/.gemini` | Antigravity brain — do NOT touch blind |
| 11.36 | `C:\Windows\SoftwareDistribution\Download` | pure Windows Update cache, safe |
| 7.44 | `Watchtower/vault` | **the corpus — never delete** |
| 5.44 | `~/Downloads` | GM's |
| 4.53 | `AppData\Local\Temp` | safe |
| 1.97 | `~/.cache` | safe |
| 0.34 | `AppData\Local\CrashDumps` | safe |

Recycle Bin empty; `pagefile.sys` only 13.6GB — the usual easy wins are absent. Also present: ~1.5GB of `nougen_shards_*.db.bak` files in the vault dir (0.27-0.29GB each) that may be stale backups worth reviewing.

**GM is handling reclamation himself** ("i got older stuff") — no deletions performed by this lane. A broader `C:\` + profile scan is running to locate the remaining ~870GB.

## Standing lesson
`OSError: Errno 28` / `disk I/O error` from SQLite means **check free space first**, before any performance or concurrency theory. A full disk presents as slowness, hangs, lock contention, and CPU burn — every symptom this incident chased for hours.
