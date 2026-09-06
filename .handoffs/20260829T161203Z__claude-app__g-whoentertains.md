# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE, MEASURED: the relay listing is blind past 1000 files. GitHub Contents API caps at 1000 entries, .handoffs has 1180, filenames sort chronologically - so the NEWEST ~90 legs are invisible to every provider
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T16:12:03.082Z

---
## The connector is not delayed. It is blind, and it gets blinder with every leg.

`relay_latest` has been returning `20260829T120008Z__ccr__gm-phone` for hours while legs kept landing. Measured against the live API:

```
GET /repos/Who-Visions/NouGenRelay/contents/.handoffs?ref=main
  -> returns exactly 1000 entries
  -> last entry: 20260829T120008Z__ccr__gm-phone.json
```

**That is the exact leg `relay_latest` keeps serving.** Not a coincidence - it is the cutoff.

- **GitHub's Contents API truncates a directory listing at 1,000 entries**, alphabetically, with no error and no `truncated` flag.
- `.handoffs/` currently holds **1,180 entries** (587 legs x `.json` + `.md`, plus `claims/`).
- Leg filenames are timestamp-prefixed, so **alphabetical order IS chronological order**.
- Therefore the newest **~180 entries (~90 legs)** fall past the cap and are invisible to every listing call.

## Why it looked like a sync delay
- **Writes land fine** - `PUT` by path, no listing involved. Every leg written today is in `origin/main`; the newest commit touching `.handoffs/` is 16:06:36Z.
- **Reads by exact id work fine** - `relay_read` on any of the "missing" legs returns full content, including triage notes added by other lanes.
- **Only listings are blind.** `relay_latest` and `relay_open` cannot see past entry 1000.

So the data is all there and perfectly healthy. The index into it stops at noon.

## Blast radius
**Every provider, equally.** Claude, ChatGPT, Codex, Gemini all read through the same connector. Nobody has seen a new leg since 12:00:08Z. This is why ChatGPT appears to be "missing everything" - it is, and so is everyone else, including me.

**It is self-worsening.** Every leg written pushes the horizon further into the past. It crossed 1,000 sometime around midday today and will never recover on its own.

**It silently poisons the triage loop.** `relay_open` is "legs nobody has acked". A leg past the cap can never appear there, so it can never be picked up - it is not queued, it is erased from the queue's point of view while sitting intact on disk.

## Fixes, in order of correctness
1. **Use the Git Trees API instead of Contents.** `GET /git/trees/{sha}?recursive=1` returns up to 100,000 entries and sets an explicit `truncated` boolean - so it both scales and *tells you* when it did not fit. The Contents API's silence is the actual defect here; a listing that truncates without saying so is the same unreadable-reads-as-absent failure this fleet has hit six other ways today.
2. **Shrink the directory.** Two options, both of which change paths and therefore break `relay_read` on anything moved:
   - Move leg bodies to `.handoffs/bodies/` - halves the count to ~590 immediately.
   - Archive by month, `.handoffs/2026-07/` etc.

   **I have NOT done either.** Restructuring a registry that four providers read by exact path is a scope-changing action on shared state, and it would trade a listing outage for a read outage. GM call.

## Note on this very leg
It will be written successfully and **will not appear in any listing** until the cap is fixed. Reachable only by id: `20260829T160000Z`-ish, `__claude-app__g-whoentertains`. Anyone relying on `relay_latest` to find it will not.

Credit: the GM spotted the symptom - "connector not showing all relays upstream synced, ChatGPT is missing seeing everything" - and was right that it was a blocker rather than a delay.
