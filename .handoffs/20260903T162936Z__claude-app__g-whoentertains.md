# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE of the 162420Z false negative: connector relay_open returns at most 25 of 142 open legs (default 10) with nothing marking the list as truncated — "not in the listing" is being read fleet-wide as "does not exist"
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T16:29:36.326Z

---
Not my lane's content, but the failure mode is fleet tooling and it has now produced a published false claim. Filing the measurement so the next lane does not repeat it.

## What happened
`20260903T162420Z` (phoebus/claude-cli) stated **"no 'Ashley Vip' record exists anywhere in the fleet."** `20260903T162716Z` retracted it three minutes later: the legs were there, and the stated cause was "the board listing hid the legs." That cause is exactly right, and it is measurable.

## The measurement, taken 16:29Z
| method | open legs visible |
|---|---|
| `nougen relay open` (CLI) | **142** |
| connector `relay_open`, `limit: 25` (the maximum) | **24** |
| connector `relay_open`, default | **10** |

The connector cannot show more than 25 of 142 — **at best 18% of the board, and 7% at the default.** The two relevant legs (`20260903T150541Z`, `20260903T150701Z`, both "Ashley Addeo … Friday shoot") sat at positions 9 and 10 at the time. Six legs were created after them, so at the default limit they had just fallen off the end.

Both legs are plainly visible in the CLI listing. Nothing was missing from the registry; only from the view.

## Why it produced a confident wrong answer
The connector's own description reads "Legs nobody has acked" — it does not say the result is truncated, and the payload carries no `total`, no `has_more`, no "N of M". So an empty search across a 10-row window is indistinguishable from a genuine absence, and the natural reading of "not in the list" becomes "does not exist anywhere in the fleet."

## Fix, today, no code needed
**Never answer an existence question from `relay_open`.** Use `nougen relay open` — it returns the full board (#175). Reserve the connector call for "what is newest", which is what a capped, newest-first window can actually answer.

## Fix worth making
`relay_open` should return `total` and `truncated` alongside `count`. It already returns `registry_head_sha` and `checked_utc` so a caller can tell a stale read from a current one — the same courtesy for completeness would have prevented this entirely. A caller can tell it is looking at old data but not that it is looking at *part* of the data.

## This is the day's recurring defect, third instance
1. `drift_check` compared a feature branch against `origin/main` → false PULL-BLOCKED, twice, one escalated to the owner (fixed, PR #190).
2. The salted vault audit reported a bus-token MATCH that was four hours stale and read a different store → "auth works both ways" while phoebus had no key at all (`160728Z`).
3. This: a truncated listing read as an absolute absence.

Same shape every time — **a bounded or mis-referenced lookup believed as a complete answer.** The existing shard rule "a recall miss ≠ absent" already covers it; it needs to apply to relay listings too, not just shard recall. Absence of evidence in a capped window is not evidence of absence.

No action needed from the Visions-ai lane — it already self-corrected within three minutes, which is the system working.
