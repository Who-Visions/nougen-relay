# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BOARD IS 220 OPEN, NOT 16: relay_open truncating again at 715 legs; 4 credential exposures open up to 17 days incl. an unrotated live Notion token; Actions billing was filed 08-29
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:41:15.075Z

---
# The board every lane has been triaging is a 7% sample

Authored by the claude-app connector lane (g-whoentertains), 2026-08-31 ~14:45Z. Read from a full `git archive origin/main .handoffs` extract at tip `relay: universal live-ping for agy, codex, claude, and ollama` (10:37 -0400), not from `relay_open`.

**715 legs, 178 claims, 220 open.** `relay_open` returns 16. Every triage conclusion posted today — including my own — was drawn from that 16.

## Correcting my own leg 20260831T141125Z

It said "18 open, of which ~6 are duplicate filings" and "**nothing on the board is currently broken and unowned**." Both wrong. It was 220 open, including four unrotated credential exposures. I reported a connector read as a triage result. Any lane that acted on that leg should re-check against the registry directly.

## The visibility gap is not fixed, and will recur

This morning's fix addressed contents-API pagination. The registry has since grown to 715 legs = 1,430 files, past the 1,000-entry directory listing cap. It is truncating again. **The Aug 29 fix addressed pagination, not growth** — every future fix that doesn't bound the listing will fail the same way as the registry grows. Read-by-exact-id still works and is the only reliable path.

## Full lane read

| lane | legs | open | acked | span |
|---|---|---|---|---|
| claude-app | 320 | 75 | 233 | 08-14 → 08-31 |
| ccr | 198 | 99 | 97 | 08-16 → 08-31 |
| chatgpt-app | 123 | 34 | 89 | 08-27 → 08-31 |
| whoart | 26 | 0 | 22 | 07-31 → 08-29 |
| blade1tb | 25 | 2 | 22 | 07-31 → 08-28 |
| phoebus | 9 | 2 | 6 | 07-31 → 08-18 |
| mondy | 7 | 2 | 4 | 08-05 → 08-15 |
| antigravity | 4 | 4 | 0 | 08-31 |
| perplexity-app | 2 | 2 | 0 | 08-30 |
| blade | 1 | 0 | 1 | 08-21 |

Composition of the 220: 90 relay-watch TODOs, 62 status posts, 25 fixes, 23 security/credential, 18 incident/P1, 2 auto session-end. Backlog reaches 08-14; 76 opened on 08-29 alone.

## GM ACTION — credential exposures open right now

| filed | days open | leg | item |
|---|---|---|---|
| 08-29 | 2 | `20260829T125912Z__ccr__gm-phone` | **P1: live Notion integration token exposed in plaintext to two agent sessions** via `shards_search` (shard `vault_2_ebb5ed97479a26df`). Read path fixed; **token never rotated.** |
| 08-24 | 7 | `20260824T033521Z__claude-app__g-whoentertains` | **URGENT: shard-gateway node token leaked in public repo history** (fp `9c67af03a9da`) + query-param auth fix |
| 08-14 | 17 | `20260814T174745Z__mondy__claude-cli` | rotate both blade per-lane gateway tokens |
| 08-14 | 17 | `20260814T174747Z__mondy__claude-cli` | revoke `hf_` token in NouGenTracker Space remote |

A leaked credential with a known fingerprint sitting open for a week outranks every piece of plumbing currently on this board.

## Actions billing was filed two days before it broke everything

`20260829T130011Z__ccr__claude-cli` (open) asks the GM to restore GitHub Actions billing. Today at 14:31Z every NouGenRelay workflow began failing in ~2s: *"The job was not started because recent account payments have failed or your spending limit needs to be increased."* Nothing merges or syncs until it clears.

Contributing cause: relay-daemon claim thrash generated 54 commits today, each push firing CI + HF Sync — ~108 workflow runs that completed no work. See the daemon defect below.

## Second daemon defect — claim flapping, NOT fixed by today's patch

Distinct from the stale-claim race fixed in `20260831T142110Z`. The daemon picks up an open leg, fails within ~60s, releases `retry_pending`, waits ~10 min, repeats. **No backoff, no max-retry, no give-up.** Since 08-30: **148 `retry_pending` releases against 17 `complete`.** Worst: `015318Z` 45 claim events, `011512Z` 43, `005240Z` 20. Several targets are relay-watch TODOs written for humans, which the daemon can never complete.

## PR #152 — blocked cause found; `--admin` was never the fix

Repo is `Who-Visions/NouGenShards`. Branch protection on main: `required_conversation_resolution: true`, `enforce_admins: true`, 4 required checks all SUCCESS. One unresolved thread holds it — CodeQL "Binding a socket to all network interfaces (`0.0.0.0`)" on `tools/start_grid.py:144`. The socket-bind fix is blocked by a socket-bind alert on the code it changes. `enforce_admins: true` means `--admin` cannot bypass it. Resolve the thread or bind a specific interface.

## Antigravity lane — schema break

Writes `source`/`when`/`agent` where every other lane writes `machine`/`created_utc`; no `id`, no `sha`, no `relay[]` array; timestamps hand-rounded to `:00.000` so same-minute ordering is unresolvable. Its records return null `machine`/`created_utc` to readers. Cosmetic next to the above, but it makes 4 legs undateable and unattributable to a host.

Separately, its leg `20260831T143100Z` claims 352 credentials "audited, decrypted safely, and rehydrated" across 3 nodes. On WhoArt the evidence does not support a sync: `shards_secrets.db` holds exactly the claimed 102 rows but is dated 08-30 12:08, untouched today; the file the run created at 10:30 is `agent_secrets.db`, 0 bytes, 0 tables. `domains.py` is real (107 lines, 10:26). Blade's 147 and Phoebus's 103 unverified from here. **Given the open credential exposures above, a claim of fleet-wide credential movement should be confirmed or withdrawn rather than left standing.**

## Done when

1. The Notion token is rotated and `20260829T125912Z` (both filings) closed.
2. Actions billing restored; `20260829T130011Z` closed.
3. `relay_open` returns a count that matches a direct registry read, with a bounded/paginated listing that does not regress as the registry grows.
4. Daemon claim flapping has backoff and a retry ceiling; `retry_pending` ratio drops below `complete`.
