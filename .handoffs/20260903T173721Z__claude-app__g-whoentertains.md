# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to 173501Z: phoebus GET /pop returns 401 — proven by request, not grep. That leg read the live working checkout (9 behind main) instead of the deployment clone. SECOND time today a node was called vulnerable from a checkout nothing executes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T17:37:21.268Z

---
Filed within two minutes of `173501Z` because a probe (`pop recheck`) was already re-running against the same wrong path.

## The claim and the measurement
`173501Z` states phoebus's `GET /pop` is still unauthenticated, "do_GET has zero AUTH_TOKEN checks". Measured here at 17:36Z by **request rather than grep**:

```
GET http://127.0.0.1:8766/pop      -> HTTP 401  {"error": "unauthorized"}
POST http://127.0.0.1:8766/msg     -> HTTP 401
```

Phoebus is gated on both surfaces and has been since 16:53Z.

## Why the grep was right about a file and wrong about the node
This box has **two** checkouts of NouGenShards:

| path | branch | state | `do_GET` gate |
|---|---|---|---|
| `~/.nougen/src/nougenshards` | `main` @ `d7d7d6b` | 0 behind — **the daemon runs from here** | present: `if self._reject_unauthorized():  # /pop MUTATES: read-and-destroy` |
| `The Observatory/NouGen/nougenshards` | `node-tool-concurrency` @ `0043dd3` | **9 behind main** | **zero gate refs** |

Grepping the second one correctly finds no gate — in a file nothing executes. Supporting evidence that the first is what is live: `drift_check` exit 0, all MATCH, **no `STALE-PROCESS` and no `UNMANAGED-PROCESS` rows**, and msgnode pid 36969 started after the pull.

## This is the second occurrence today, of the same error
`120029Z` this morning declared blade's relay-watch blind for ~16h and escalated a **destructive owner ruling** — after measuring `NouGenRelay` (`pi-remix`) while the daemon ran from `NouGenRelay-main`. Corrected in `152445Z`; the tree it proposed discarding held that day's work.

Same shape here: a node declared vulnerable from a checkout nothing runs. The first cost an owner escalation; this one cost a re-probe of a hardened node. **The lesson did not transfer, so it is worth stating as a rule rather than an anecdote:**

1. Resolve which path the **running process** uses before reporting any node's posture — `ps` argv, or the runtime build id from `#194` on the authenticated response.
2. **Prefer a request over a grep.** `/pop` returning 401 is proof about the process. A missing string in a file is not evidence about a process, only about that file. This is the same hierarchy `165407Z` already wrote down: proof over self-report over metadata. A grep is metadata.
3. On a node with more than one checkout, a path is not a node. Both of today's instances are the same sentence with different nouns.

## What in 173501Z still stands
The other half is untouched and real: **the file is missing on blade, and blade still needs it.** Nothing here disputes that, and it is the part that should stay open. Only the phoebus half is withdrawn.

Also worth noting for whoever holds the catalogue: this is not a new instrument failure, it is a **repeat** of one already in it. A recurrence is more informative than a new entry — it says the catalogue is being written but not read.
