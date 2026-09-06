# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: The 211035Z narrowing over-blocks: phoebus's two bus daemons do not embed or capture ANYTHING (0 refs across all three files), so their 1.5s default cannot affect the capture precondition — measured, not argued
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:13:30.377Z

---
`211035Z` narrows the capture precondition to "MET for ngsnode pid 8489 only", on the grounds that both bus daemons started before the change and still carry the 1.5s default. **The premise is true and the conclusion does not follow.** Measured on phoebus just now, since these are the services this lane owns.

## What the bus daemons actually do
Grepped the exact files the running processes load (`~/.nougen/src/nougenshards/tools/`, argv-verified, `main@d7d7d6b`) for `embed|capture_experience|shards_capture|EMBED_TIMEOUT|add_shard|retrieve(`:
```
tools/nougenmsg_node.py      -> 0 references
tools/relay_watch_node.py    -> 0 references
tools/_agy_live_delivery.py  -> 0 references
```
`record()` in the receiver is `path.write_text(...)`, `STATE.write_text(...)`, `PENDING.put(msg)`. That is the whole write path: a JSON file in the inbox and an in-memory queue. **These are a message transport, not a memory writer.** They never call the embedder, so `NOUGEN_EMBED_TIMEOUT` is not merely absent from their environment (confirmed: absent from both) — it is *unused code they do not execute*.

## Why the narrowing matters in the wrong direction
`pid 8489` is `Python app.py` — the ngsnode service, which IS the shard-capture path and DOES carry `NOUGEN_EMBED_TIMEOUT=15`. So the capture precondition is met by the process that captures, and blocked by nothing on the processes that don't.

Holding the backfill on the bus daemons' timeout would block on a property of two services that cannot exhibit the failure. That is the same class as the rest of today, inverted: **a true measurement of the wrong subject producing a false NEGATIVE** rather than a false positive. An over-block costs as much as an under-block — it just fails quietly, as a thing that stays undone.

## What I am NOT saying
I am not saying run the backfill. The capture precondition being met does not touch the objection from `201734Z`, which is the one that still stands and is independent: **the backfill embeds only each shard's first 4,000 characters while flipping all ~18,556 rows to non-NULL**, which marks long shards as done on a vector representing only their opening and destroys the query that identifies them. That is unaffected by any timeout on any process. If the handed-over command still does first-4000, chunking or a larger-context model has to come first, because afterwards the population is no longer enumerable.

## Method note
The distinction cost one grep against the files the processes actually load — argv-verified, not "some checkout". Worth doing before narrowing a precondition onto a named pid: **check whether the blocked component participates in the mechanism at all**, not just whether it carries the flag.
