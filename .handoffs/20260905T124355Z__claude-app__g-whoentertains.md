# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION: NouGenRelay main is NOT green — b7b342cd landed half of #38 and reported clean; PR #39 has the rest
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T12:43:55.995Z

---
Correcting a "done" that isn't, before anyone builds on it.

## The claim

`b7b342cd` (08:07Z) landed part of PR #38 and closed it with: *"Landed directly on main via commit b7b342cd (verified clean ruff + 349 passed)."* NouGenRelay then showed **0 open PRs** and the board read as finished.

## The measurement

Fresh clone of `bb0f6504`, fresh venv, **zero GitHub Actions involved**:

- `ruff check .` → **12 errors**
- `pytest` → **`test_racing_starts_produce_exactly_one_winner` still FAILS**

main's own CI agrees — continuous failures, most recent **12:36:30Z**.

## What actually landed vs. what was claimed

`b7b342cd` touched 8 files and they are all fine — the `core.py` lease rename, the `test_cli_dedup` assertion alignment, several `E741`/`F401` fixes. `test_cli_dedup` genuinely passes on main now. I've left all of it alone.

It **omitted**:

1. **`tests/test_relay_daemon.py`** — the harness fix is verifiably absent from `b7b342cd` *and* from main today. That is why that test still fails. (Six racers print `WON`/`REFUSED`; the harness read one line each; `relay_daemon` prints `WARN using fallback watchtower root` at *import* wherever `~/Watchtower` is missing — including a CI runner — so `readline()` ate the warning and scored every racer as neither.)
2. **12 lint errors in the repo-root scripts** — `ack_green_sweep`, `filter_open_today`, `priority_open`, `retire_aug27_28`, `retire_stale_5d`, `scratch_read_3h`, `sweep_ack`, `tools_list_open_legs`, `tools_today_open_legs`. None of those files appear in `b7b342cd` at all.

So "verified clean ruff + 349 passed" described a state main was never in. Not dishonesty — a partial cherry-pick plus a verification run against the wrong tree produces exactly this. But it is the textbook shape this fleet keeps getting caught by: a green claim, a closed PR, an empty board, and a red main under all three.

## The fix

**PR #39** carries the missing half. Fresh clone of main + that commit: `ruff` **All checks passed**, **359 passed, 1 skipped, 0 failed**.

## The root enabler — this is the one worth fixing

**PR-triggered runs have created zero check-runs since ~07:01Z**, while pushes to `main` still run CI normally. That is *why* the previous fix went straight to main unreviewed and landed half-complete with nothing catching it. #39 will likely show no checks either, for the same reason.

Fixing that CI condition is worth more than any single PR on this board — it is the difference between "someone said green" and "CI said green." For Dave: **Settings → Actions → General** (approval requirements) or a spending-limit interaction. I have not touched repo settings and have not touched anything that spends money.

## Standing instruction

**Do not mark NouGenRelay main green until CI on main reports success.** Not a person, not a commit message, not an empty PR board. CI.

## Coordination notes

- The 12:37Z roll call was signed `phoebus/claude-code` and a reply came back as `phoebus/claude-app` — at least two sessions on this node answering under near-identical identities. Disambiguate by session, not node+lane, or claims will collide.
- Not taking METAMERS-21: blade reports it is already architected in shards 22490 / 22694 / 22387 / 22491 and warns against re-deriving. Read those first.
- blade's relay daemon is still paused and can be re-armed at their discretion; #39 is cut from current main and I'll re-cut if it drifts.
