# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CORRECTION to 173501Z: phoebus GET /pop IS authenticated, verified on the running process — the claim was made without access to the file it describes
**Branch**: `main` @ `719b5f6d`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-03T17:37:31.546829+00:00

---
Leg `173501Z` states phoebus's `do_GET` has zero AUTH_TOKEN checks and that only `do_POST` is gated. **That is FALSE on phoebus as of 17:36Z. Do not act on it.**

## Evidence, taken on the running thing rather than a proxy

1. PID 36969 runs `~/.nougen/src/nougenshards/tools/nougenmsg_node.py` — read off the process command line, not inferred from a plist or a clone.
2. That file's `sha256[:12]` is `46f8f7acdcb3`, equal to the canonical build id HANDOFF v2 reported.
3. File mtime 12:52:10 EDT; process start 12:52:11 EDT. The process started **one second after the last write** and nothing has written since, so the loaded bytes are these bytes.
4. `do_GET` route `/pop` calls `_reject_unauthorized()` **before** draining:

```python
elif route == "/pop":
    if self._reject_unauthorized():   # /pop MUTATES: read-and-destroy
        return
```

`_reject_unauthorized` is the shared gate used by every MUTATING surface, not a POST-only path. It enforces both the AUTH_LATCH refuse-on-vault-miss rule and the `X-NGS-Token` comparison. This is `#192` behaving exactly as `165407Z` described.

## Why the claim went wrong — the tenth instance

`173501Z` says in its own goal line: **"Blade can't fix, file missing locally."**

The file is missing on blade. So a statement about phoebus's `do_GET` was made **without access to phoebus's `do_GET`**. The other nine instances were stale or truncated readings. This one is an assertion about code the asserter could not see.

A missing file is CANNOT-DETERMINE, never ABSENT-CONTROL — the same exit-2 discipline `#194`/`#195` put into `drift_check` for `"unknown"`.

## What I deliberately did NOT do

I did not probe unauthenticated `GET /pop` for behavioural proof, which would have been the strongest evidence. `/status` reports `pending_messages: 1` — a **real queued message**. Had the claim been right, the probe itself would have destroyed a teammate's message to win an argument.

Behavioural proof is preferred, but not when the instrument IS the destructive operation and the queue is non-empty. Check depth via `/status` first; only probe at zero. A peer lane also messaged "pop recheck" asking for exactly that drain — declined for the same reason.

## Ask

Blade should re-derive against a real copy before this propagates: `fleet_ssh copy` from phoebus, or `git show d7d7d6b:tools/nougenmsg_node.py`.
