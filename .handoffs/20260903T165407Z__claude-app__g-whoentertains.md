# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HANDOFF v2 phoebus (supersedes 151443Z): an auth incident and three merges happened AFTER that handoff — main@d7d7d6b, phoebus verified on the running process, 2 owner items open
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T16:54:07.439Z

---
Supersedes handoff `151443Z`, which was written at 15:14Z and is now materially wrong — a live security incident and four merges happened after it. If you read that leg, read this one instead.

## What changed since `151443Z`

**A live auth incident, opened and closed (leg `161552Z`, corrected by `161830Z`).** phoebus's receiver served `auth=open` on `0.0.0.0:8766` for ~37 minutes (15:35–16:12Z), accepting unauthenticated POSTs. Cause was two-part: `NOUGEN_AGY_MSG_TOKEN` alone stopped resolving from the vault (the other three keys resolved fine — not a broken vault), and a backwards-compat rule `if not token: accept` could not distinguish NEVER PROVISIONED from PROVISIONED-AND-LOST. Fail-open in the one component whose job is to gate. Blade independently had the identical rule.

**A second, older hole found while verifying the first: `GET /pop` was unauthenticated and DESTRUCTIVE.** Every gate ever built — auth, judge, owner-origin, dedup — lived in `do_POST`. `do_GET` had no check at all, and `/pop` drains the queue. Proven on a provisioned node: two authenticated messages queued, an unauthenticated `GET /pop` returned both bodies and left the queue empty. Reachable off-machine (the sibling node fetched it over the LAN and got 200). Nobody had asked what could be taken OUT.

**Four merges to `main`, all deployed and verified here:**
- `#191` `dcd87fd` — suppress child console windows so a hidden scheduled task stays hidden
- `#192` `c5cee18` — auth latch (`NOUGEN_AGY_MSG_AUTH=required` means "a token WAS deployed here", so a vault miss REFUSES rather than opens) + `/pop` behind the same gate as `/msg`
- `#194` `4ee34e9` — runtime build id: `sha256[:12]` of the file the process actually loaded
- `#195` `d7d7d6b` — build id moved OFF the unauthenticated `/status` onto the authenticated response

## Phoebus state, measured not assumed (16:55Z)
Deployment clone `~/.nougen/src/nougenshards` at `main@d7d7d6b`, 0 behind. Daemons reloaded from it; the RUNNING process reports build `46f8f7acdcb3` on its authenticated response, equal to canonical — verified on the process, not inferred from disk. Unauthenticated `POST /msg` 401, unauthenticated `GET /pop` 401, `/health` and `/status` 200 for liveness with **no build id leaking by value** across any open surface. Latch set in both plists AND now load-bearing in code. `NOUGEN_WAKE_DISABLED=1` still set: phoebus remains a no-wake node by decision. One benign `ConnectionResetError` in the logs from a probe landing mid-restart; nothing since. Worktrees cleaned to the live checkout only.

## OPEN — owner decision, nobody should guess
**The bus token mutated twice in four hours and neither node did it.** It went ABSENT on phoebus and CHANGED on blade between 11:56Z and 16:10Z. Ruled out on both sides: no store divergence (phoebus has exactly one store, 105 rows, `VAULT_DIR`/`DB_PATH` both resolve there, `find_legacy_stores()` empty; blade has three stores but `get_secret` demonstrably read the canonical one both times), same pinned salt, neither session wrote the key. Blade withdrew its "silent rotation" claim on a good technicality — converging its tooling overwrote the instrument that produced the 11:56Z reading, so that measurement is no longer reproducible. Status is UNRESOLVED, not "explained". Do not invent a cause.

## OPEN — fleet-wide, filed at `163250Z`
`relay_open` returns at most 25 of **146** open legs and its `count` field reports the PAGE, not the board, with no truncation marker. Every "no such leg exists" conclusion drawn from a listing today is unsound — including two of mine. Positives from a listing are still sound; only negatives are broken. Until fixed: never conclude absence from `relay_open`; use the CLI or count `.handoffs/*.json` directly.

## Sequenced next, and it is NOT phoebus's
Blade builds `BUILD-MISMATCH` into `tools/drift_check.py` on top of `#194`/`#195`, treating `"unknown"` as CANNOT-DETERMINE / exit 2 per the contract, and clears its own E731 lambdas from `#189` while in that neighbourhood. Two files, two owners — we got concurrent edits wrong twice today and stopped.

## The pattern, which matters more than any single fix
**Eight times today an instrument confidently reported something untrue**: a stale git ref, a stale deployed tool, a process reading a different clone, a stale secret audit, an inert env-var latch, a truncated listing presented as complete, a disk hash standing in for a running process, and a verified 401 on ONE surface reported as a property of the whole receiver. Every one looked like success. Every correction came from someone RE-DERIVING the claim rather than reading it — three times a peer's independent re-run changed the outcome. Working rule for whoever picks this up: **verify the thing, not its proxy**, and prefer proof (behaviour) over self-report over metadata heuristics. Durable versions are in shards; recall those rather than re-reading these ledgers.
