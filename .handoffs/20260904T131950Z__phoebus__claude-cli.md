# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Applying whoart's regen caveat to phoebus found two defects: NOUGEN_MACHINE unset here silently forks a 4th machine series, and the guard against that is structurally incapable of firing (NouGenTracker PR #24, 994 tests). Hard precondition on the schedule move
**Branch**: `main` @ `9f4e5806`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T13:19:50.052918+00:00

---
Verified whoart's `130650Z` from source rather than accepting blade's relay of it — it is accurate, and my open item on whoart is closed. Then I applied whoart's own regeneration warning to my box and it caught something.

## Closing my open item

`130650Z` is real and thorough. Whoart's Claude task `nougentracker-daily-readout` exists and was broken three ways — targets `date.today()` (an open day, so `partial: true` floors), uses `--export` and never `--publish` (**a successful run reaches nothing**), and had stopped firing. Five days published, `226a573`, counter `cfae0dd41682` matching blade and phoebus. My "whoart has nothing to fire" is superseded, not merely unsupported. Their point stands over mine: the fix was never "install a task", it was that the task was lying about coverage.

## Applying whoart's caveat to phoebus found a live defect — in the flag, then in the guard

Whoart warned that regenerating an aged daily silently loses data. So I checked my own published series for the floors that would tempt someone to regenerate: **34 days, 33 clean, and `2026-09-03` published with `partial: true`.**

I re-exported that day (closed, one day old, inside blade's ~27-30 day transcript cliff, so safe by whoart's rule). The result looked like a clean no-op — identical invocations, identical totals, byte-identical file.

**It was not a no-op. It was an export to a different machine.**

```
Exported 1 day(s) for kushboygroups-mac-mini-local -> dailies/kushboygroups-mac-mini-local/
```

`NOUGEN_MACHINE` is unset on phoebus — absent from `.env` and the environment — so `fleet_dailies.resolve_machine()` fell back to the hostname and **created a fourth machine series** beside blade1tb / phoebus / whoart. `dailies/phoebus/2026-09-03.json` was never touched, which is exactly why it looked identical. I caught it only by checking `generated_at`; the "byte-identical, therefore verified" reading I nearly published was a no-op wearing a confirmation.

Stray directory removed. No published data touched. Working tree clean.

## The guard for this exists, is wired, and cannot fire

`unintroduced_machine_warning()` is written for exactly this and IS called at `token_tracker.py:2886`. It printed nothing. Reason:

```python
_paths   = _fd.export_days(ALL_INVOCATIONS)          # creates dailies/<machine>/
_warn    = _fd.unintroduced_machine_warning(_machine) # then reads that directory
```

It returns `None` when `machine in known`, and `known_machines()` reads the dailies dir — which by then contains the directory the export just made. **The safeguard is structurally incapable of triggering.** Proven both ways:

```
name with NO directory   -> "'kushboygroups-mac-mini-local' has never published dailies here…"
name WITH a directory    -> None        <- what the call site always sees
```

Its own docstring says it "stops one box from being counted twice under two names" and calls a split identity "wrong in the direction that looks plausible, which is the worst direction to be wrong in." It has been providing none of that.

**Fixed: WhoVisions/NouGenTracker PR #24.** `known_machines()` sampled before the export and passed in; optional param, so no other caller changes. **994 tests pass** (4 new, 990 existing), including one that fails against the old ordering.

## This is a hard precondition on the schedule move

Blade and I both recommended moving the nightly publish to phoebus, and both declined to install it. Add this to that decision:

> **`NOUGEN_MACHINE=phoebus` must be set in the same change.** Without it a scheduled publish here writes to a phantom machine — and before PR #24, it would have done so with no warning at all.

That is the config gap #24 makes visible rather than fixes. Still not installing the schedule: cadence, `--fleet` ownership, and disabling blade's `daily-token-report` in the same change (blade's point, and correct — two boxes publishing one day is the mixed-cohort case step 3a says to stop on) belong to the `130106Z` lane.

## Standing question I cannot answer from here

`partial: true` on phoebus `2026-09-03` is still unexplained. `fleet_dailies.py:597` sets `"partial": day >= today` at export time, so a closed day re-exported today should be `False` — but I never actually re-exported it, so I have no evidence either way. Whoever picks this up should re-run it **with `NOUGEN_MACHINE=phoebus`** and see whether the flag clears. If `partial` can stick on a complete day, it is a false signal that invites exactly the destructive regeneration whoart warned about — that would make it the more important half of this whole thread.

*— phoebus / claude-cli*
