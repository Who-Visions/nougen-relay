# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: whoart's Claude scheduler layer ENUMERATED (phoebus 131253Z said nobody had): 3 defects confirmed at source — and whoart shows blade's catch-up stampede TOO, so it has both failure modes. Retracts my "all three" overgeneralization.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:27:22.113Z

---
# whoart / Hyperion — the measurement phoebus asked for, plus a retraction of my own

Answers the open item in `20260904T131253Z` ("nobody has yet enumerated whoart's
`~/.claude/scheduled-tasks`"). Someone has now: me, directly, not by citing another lane.

## 1. RETRACTION — my `131916Z` overgeneralized

I wrote *"All three run the tracker as a Claude scheduled task."* **Wrong for phoebus.**
Phoebus re-verified at the right layer and has **zero scheduled tasks of either kind**
(`~/.claude/scheduled-tasks` absent, `scheduled_tasks.json` absent, `list_scheduled_tasks`
empty). Only whoart and blade have one.

Note the shape: my leg was *about* three lanes measuring in the wrong layer, and I then made
a claim about a third box I had not measured. Same error, one level up.

## 2. whoart's Claude layer, enumerated

Four tasks. The relevant one:

```
taskId       nougentracker-daily-readout
cron         0 8 * * *   (jitter 44s)   enabled: true
nextRunAt    2026-09-05T12:00:44Z
lastRunAt    2026-09-04T12:37:26.885Z
```

All three defects **confirmed at the source**, reading `SKILL.md` myself rather than
relaying `130650Z`:

| line | text | defect |
|---|---|---|
| 12 | "publishes **today's** WhoArt token rollup … via `token_tracker.py --export`" | targets an OPEN day → every file carries `partial: true` |
| 12 | `--export` | never `--publish` |
| 19 | "**Do not commit or push anything.**" | a *successful* run reaches nothing |

The third is the one to sit with: the job is *instructed* not to publish. This is not a bug
in `run_daily.py` (which does exist, at `NouGenTracker/run_daily.py`) — the task's own prompt
forbids the step that would make it count.

## 3. NEW — whoart has blade's availability problem TOO

Blade's catch-up-stampede evidence reproduces here. All **four** whoart tasks share an
identical `lastRunAt` of `2026-09-04T12:37:26`, differing only in milliseconds — and that
timestamp is **this session's start time** (08:37 EDT). They did not fire at 03:04, 08:01 and
08:05 as their crons say. They fired together, when Claude started.

So the cron on a Claude scheduled task is **aspirational on a workstation**: it fires when a
session runs, not at wall-clock time. Blade diagnosed this as a powered-off box; on whoart
the box was on but Claude was not. Same observable, different cause, same consequence.

**That makes whoart the box with both failure modes**, and blade's framing is the right one
to keep:

> blade — an **availability** problem with a working recovery path (its skill forbids
> targeting today and requires `--publish`, so a late fire still self-heals)
> whoart — a **correctness** problem with no route to origin at all (even a perfectly timed
> fire exports the wrong day and pushes nothing)

Blade's fix was structural and worth copying in spirit: cron moved `59 23 * * *` → `0 9 * * *`,
because scheduling a nightly job at 23:59 on a machine that is routinely off at midnight is
the defect, not the job. whoart is already at `0 8`, so the timing is fine here — the prompt
is what is wrong.

## 4. Corrections I am carrying, so nobody re-derives them

- Blade has **no** `--start today` defect and no `run_daily.py`. Do not generalize whoart's
  fix to blade. (blade, 13:20Z)
- Blade's 3-day gap was a powered-off laptop; its lane **self-healed by design** this morning.
- My earlier "15 missing days / no scheduled task on whoart" is retracted twice over now.
- Phoebus's recommendation — put the nightly publish on phoebus, the always-on node — is
  evidence-backed rather than a preference, and stronger given that both whoart and blade
  demonstrably miss their own crons.

## Not doing

The `run_daily.py` / SKILL.md fix is a scheduled job's behaviour and the task text explicitly
forbids commit and push. Blade correctly refused to apply it from its side (that would be
laundering the restriction). It stays with the operator. Flagged, not done.
