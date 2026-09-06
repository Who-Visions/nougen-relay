# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to incident 120029Z: blade's relay lane was never blind — wrong clone was measured; the owner ruling it asked for is NOT needed. pi-remix is active work, do not discard
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T15:24:45.059Z

---
Correction from phoebus (claude-app), measured on blade1tb over SSH 2026-09-03 15:20-15:27Z. Leg `20260903T120029Z` asked the owner for a destructive-change ruling on a premise that does not hold. Filing loudly per the relay rule that a wrong "X is blocked" costs the next node an afternoon.

## What 120029Z claimed
- blade's NouGenRelay clone is PULL-BLOCKED, HEAD not an ancestor of origin/main
- 34 modified tracked files of unknown ownership
- **blade's relay-watch has been blind ~16h** (last successful pull 2026-09-02 19:46 EDT)
- owner ruling needed on whether those files may be committed / stashed / discarded

## What is actually true
**The measured clone is not the one the daemon runs from.** Blade has two:

| clone | branch | role | state |
|---|---|---|---|
| `Watchtower/NouGen/NouGenRelay` | `pi-remix` | dev worktree | 44 ahead / 3911 behind `origin/main`; 15 modified tracked, 1145 dirty total |
| `Watchtower/NouGen/NouGenRelay-main` | `claude/daemon-hardening` | **the running daemon** | HEAD `3d229578` @ 2026-09-03T15:02Z; **1** modified tracked, 2 dirty total |

The live process is `NouGenRelay-main\tools\relay_daemon.py --daemon`, PID 156924, up since 2026-09-02 23:12 EDT. Nothing runs from the `pi-remix` clone.

Evidence the lane is current, not blind:
- `NouGenRelay-main` HEAD commit is itself `relay: publish 20260903T150200Z__blade1tb__antigravity.md (canonical publish from blade1tb)` — a publish at 15:02Z, ~15 min before this check
- newest `.handoffs` entries: `150200Z`, `150138Z`, `145726Z` — all today
- NouGenMsg delivering live: ping at 11:07 EDT carries `delivered_live: true`, `delivered_to: [d27c5fc5-…]`; `--peers` shows 1 live cc-msg pipe
- a fresh check-in from phoebus landed on that same pipe at 15:24Z

**"HEAD not an ancestor of origin/main" was never a defect.** `pi-remix` is a feature branch with upstream `origin/pi-remix` (ahead 35, i.e. pushed). A feature branch not fast-forwarding onto main is its normal shape. The tool that reported PULL-BLOCKED compared a feature branch against `main` — worth fixing in `drift_check.py` before that row is trusted: it must resolve the branch's own upstream, not assume `main`.

## The one thing that IS live and must not be discarded
`pi-remix` is **not** abandoned work of unknown ownership. Two files carry today's mtimes:
- `src/nougen_relay/core.py` — 2026-09-03 10:23 EDT
- `tools/relay_daemon.py` — 2026-09-03 10:24 EDT

i.e. edited ~2h AFTER 120029Z was filed. The other four modified source files (`cli.py`, `relay_dedup.py`, `test_cli_dedup.py`, `test_scope_overlap.py`) are from 2026-08-29 10:48. Working-tree diff is +412/-34 across 6 source files — a coherent dedup / scope-overlap change, not junk. The remaining modified tracked entries are runtime churn: 6 `.handoffs/*.json`, `.relay/wake.signal`, `logs/combined.log`, `logs/error.log`.

**Do not reset or discard that tree.** The correct disposition is to commit it to `pi-remix` (which already has an upstream), and it needs blade's confirmation of authorship, not an owner ruling.

## Net effect on the board
- Open item 3 in handoff `151443Z` ("OWNER DECISION — blade's relay clone is PULL-BLOCKED") is **withdrawn**. No owner input is required. Owner item 4 (the owner-origin token) still stands.
- `~16h blind` should not be carried into any later ledger.

## Two follow-ups, not blockers
1. **Duplicate publisher risk:** two `relay_live.py --daemon --quiet` processes run from `NouGenShards-push-main`, PID 346776 (`.venv` python) and PID 97724 (system Python311), both started 2026-09-03 01:16 EDT. Same script, same source tree, two interpreters. Asked blade whether that is intentional; if not, one should be retired.
2. **Secret exposure on blade:** a cloudflared tunnel token is visible in full in a process command line (`tools\bin\cloudflared.exe tunnel run --token …`, PID 172012, running since 2026-08-31). Process command lines are readable by any local process. Value not reproduced here or anywhere. Recommend moving it to a credentials file or the Keymaker vault and restarting that tunnel.

## Asked blade directly (pipe `d27c5fc5`, 15:24Z)
1. status of PR #189 — phoebus unblocked it at 15:15Z, `NOUGEN_WAKE_DISABLED=1` is the constraint-3 answer
2. are the 10:23/10:24 EDT `pi-remix` edits blade's
3. is the double `relay_live.py` intentional
