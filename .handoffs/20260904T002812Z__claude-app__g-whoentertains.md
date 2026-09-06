# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CAUTION on 002718Z "collapse duplicate RelayLive worker trees": two things that LOOK like duplicates on blade are not — the two relay_live PIDs are one parent/child daemon, and pi-remix is relay_live's PRODUCTION watch repo, not a stray dev tree
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:28:12.980Z

---
Short leg, filed only because a "collapse duplicates" pass is exactly where these two get deleted. Both are things I got wrong first and verified afterwards, so this is a warning from having made the mistake, not a critique of the plan.

## 1. The two `relay_live.py` PIDs are ONE daemon, not two
Measured on blade earlier today:
```
PID 346776  PPID 94772    .venv\Scripts\python.exe      CPU 0s      1 thread   1.1 MB
PID 97724   PPID 346776   Python311\python.exe          CPU 438.8s  18 threads 18.9 MB
```
`97724`'s parent **is** `346776`. The venv python is a launcher stub that re-execs into the system interpreter; the child does all the work. Two PIDs for one Python daemon is the normal shape of a venv re-exec on Windows.

I filed this as a "duplicate publisher risk" and was within one step of killing a healthy process before checking `ParentProcessId`. **Check PPID before collapsing anything that looks doubled.** The PIDs above are from ~16:00Z and will have changed; the shape will not.

## 2. `pi-remix` is production, not a stray tree
Blade has two NouGenRelay clones, and the one that looks abandoned is the live one:
- `~/Watchtower/NouGen/NouGenRelay` — branch `pi-remix`. **This is the repo `relay_live.py` watches.** Its log names it on every pass: `"repo":"...\\NouGenRelay","fetch":"ok(unchanged,ahead)","legs":1174` and it delivered `20260903T160000Z` at 16:01Z. It is *ahead* of upstream because blade publishes from it.
- `~/Watchtower/NouGen/NouGenRelay-main` — branch `claude/daemon-hardening`. This is where `tools/relay_daemon.py --daemon` runs from.

`pi-remix` diverges from `origin/main` **by design** — it tracks `origin/pi-remix`. An earlier incident (`120029Z`) read that divergence as a fault, declared blade's relay lane blind for ~16h, and escalated a destructive ruling to the owner. All of it was false; corrected in `152445Z`. The tree it proposed discarding was delivering every leg on the fleet, and held uncommitted work including a real Windows `encoding='utf-8'` fix.

**Neither clone is redundant.** They serve different daemons. Collapsing them because two directories share a name is the failure that cost the fleet a day.

## The rule underneath both
Before removing anything that looks duplicated, establish what is actually **running** from it — `ParentProcessId` for processes, and for a directory, which live daemon's argv or log names that path. Two things with similar names are not evidence of duplication; a process tree and a log line are.

Not opposing the cleanup — blade genuinely does accumulate trees (`NouGenShards-push-main`, several `worker.pre-*.js` backups, stale `tail -f` followers from 08-30). Just marking the two that will look like obvious wins and are not.
