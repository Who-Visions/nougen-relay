# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGenRelay: main red on 3 real defects, fix verified locally in PR #38 — but PR-triggered CI creates zero check-runs (needs Dave)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T08:20:16.238Z

---
Same sweep as NouGenShards, applied to Who-Visions/NouGenRelay. Different outcome: the fix is done and verified, but it **cannot merge**, and the reason needs Dave.

## main is genuinely red — 3 real defects, not a runner artifact

Reproduced on a **clean clone in a fresh venv, no GitHub Actions involved**, so none of this is environmental:

- **ruff: 28 errors** — 13 `F401` unused-import, 9 `E741` ambiguous name `l`, 3 `F541`, 2 `E401`, 1 `F841`. Static analysis; fails anywhere, for anyone.
- **`test_cli_dedup.py::test_embed_lane_down_passthrough`** — asserted the old `"dedup check skipped"` wording. The code was upgraded to degrade to token-overlap and *announce* it. Test stale, source right.
- **`test_relay_daemon.py::test_racing_starts_produce_exactly_one_winner`** — 6 racers print `WON`/`REFUSED`, harness read exactly one line each. `relay_daemon` prints `WARN using fallback watchtower root` at **import** wherever `~/Watchtower` is absent — including a CI runner — so `readline()` ate the warning and scored every racer as neither. The lock was always correct; the harness read the wrong line.

## PR #38 — verified, rebased, blocked

Clean clone: **ruff clean, 349 passed, 1 skipped, 0 failed.**

Worth noting the E741 renames were not mechanical: the first pass left four references to `l` in `core.py`'s lease printer, which ruff then caught as `F821 undefined-name`. Fixed.

## Correction to a partial fix already on main

Another lane patched the same dedup test on main while I was working. **It does not fix the failure and main is still red on it** (verified against `a1ee1330` by running main's own test file on main's own code).

They relaxed the banner to `"skipped" OR "token-overlap"` — fine as far as it goes — but left `assert len(records(repo)) == 2` untouched, and *that* is the failing assertion. With the lane down, dedup catches the second identical goal at similarity `1.000`, exits 0 printing `duplicate leg already exists`, and writes no second record. So `records == 1`.

Also: an `or` assertion passes under either mode and therefore cannot tell you which mode ran — and making the mode visible is exactly why the code changed. #38 asserts the degrade explicitly, asserts the duplicate is reported, then asserts a **different** leg still lands while the lane is down. That preserves the intent that actually matters: a degraded dependency must not gate new work. Reporting an exact duplicate is not gating.

## THE BLOCKER — for Dave, nobody else should touch it

**PR #38 gets ZERO check-runs.** Not queued, not waiting, not failed — zero created, across two pushes plus an empty re-trigger commit several minutes apart.

Meanwhile, measured in the same window:
- pushes to NouGenRelay `main` **do** queue and run CI (08:12, 08:13, 08:14, 08:17, 08:19)
- NouGenShards CI ran fine throughout
- PR-triggered runs **used to work here** today (`fix/dedup-degraded-mode`, `codex/supersession-aware-auto-sharding`, others)
- `ci.yml` has a bare `pull_request:` trigger, so workflow config is not the cause

So something changed recently that stops `pull_request`-triggered runs specifically while push-to-`main` still works. That lives in **repo Settings → Actions → General** (approval requirements / workflow permissions) or a spending-limit interaction.

I am not touching repo settings and not touching anything that spends money. Flagging only.

**I also want to correct my own earlier message:** I used "NouGenShards ran dozens of jobs" as counter-evidence against whoart's billing theory. Actions are not globally stopped — that part holds — but "jobs did not start" was not simply wrong either. Both observations were partly right, and the truth is narrower than either: PR-event runs specifically are not being created.

## Fleet state

- blade: relay daemon paused (reversible, one line) so it stops landing claim commits on `main` while fixes are in flight. Keeping it paused a while longer — main is still moving and #38 has been rebased once already.
- whoart: holds the 18 stale draft handoff PRs, instructed to check each rather than bulk-close — in NouGenShards tonight one "obviously stale" handoff PR would have reverted a newer record.
- #14 and #25 parked until main is green; no value reviewing against a red baseline. whoart's #25 verification (356 passed, fencing token, 2m→4s batch cat-file) is noted and will not be re-derived.
