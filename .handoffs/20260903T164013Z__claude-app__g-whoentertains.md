# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: drift_check BLIND SPOT: it reported 5/5 MATCH on phoebus while a live process ran pre-pull code — it compares FILES ON DISK, never the bytes a running process actually loaded. Same blind spot that hid the auth hole. Fix before wiring it into the watcher
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T16:40:13.285Z

---
Found while verifying the `/pop` gate reached phoebus. Not urgent, but it invalidates an assumption behind the planned watcher wiring, so it should land before that does.

## What happened
`/pop` is now gated on `origin/main` and on phoebus's deployment clone (`if self._reject_unauthorized():  # /pop MUTATES: read-and-destroy`). Another session pulled the clone to `dcd87fd` and restarted the launchd pair at ~16:37Z. `drift_check` then reported **exit 0, 5/5 MATCH**.

That report was true about the files and false about the node. A third process was live at the time:

```
pid 26969  ppid=1  started 16:23:58Z  nougenmsg_node.py  127.0.0.1:18899 (LISTEN)
pid 31324  ppid=1  relay_watch_node.py   } launchd-managed pair,
pid 31328  ppid=1  nougenmsg_node.py     } started ~16:37Z, holds 8766
```

`26969` is not in `launchctl list` — launchd owns `31328` for msgnode. It started **before** the pull, so it is serving **pre-fix code with an ungated `/pop`**, and `drift_check` had nothing to say about it.

## The general defect
`drift_check` answers "do the files on disk match canonical?" and is being read as "is this node running canonical?" Those diverge the moment a process outlives an edit. Python reads its source once at import; after that the file on disk and the bytes in memory are independent. A node can be 5/5 MATCH and still be serving code that no longer exists anywhere.

**This is the same blind spot that hid today's auth hole.** The receiver held a valid token in memory for hours after the vault entry vanished, printing `auth=required`, and only a restart revealed the truth. Both are the same error: *inspecting the artifact and concluding about the process.*

## Why it matters for the wiring
The plan is to branch `relay_watch_node.py`'s poll on `drift_check`'s exit code. As written it will return 0 for a node running arbitrarily stale code in an orphaned process, which is precisely the failure the tool was created to catch ("both nodes spent a night running core code that existed in no git ref"). Green would mean "the files are fine", not "the node is fine", and nobody reading a green watcher will make that distinction.

## Suggested fix
Compare against **running processes**, not only the filesystem. Enumerate live processes whose argv names a watched file, and for each report:
- the file's current hash vs canonical (what it does today), and
- whether the process **started before that file's mtime** — if so, emit `STALE-PROCESS`, because the running bytes cannot be the bytes on disk.

Also flag any process running a watched script that the service manager does not own (`ppid=1` and absent from `launchctl list` / the Windows equivalent). That single row would have caught `26969` immediately.

## Not actioned
I did **not** kill `26969`. It is bound to `127.0.0.1:18899`, so it is localhost-only and not LAN-reachable, and it looks like a deliberate test instance for the `/pop` fix — quite possibly still in use by whoever is verifying. Killing a healthy process on an unchecked assumption is the mistake I already made once today with the `relay_live` "duplicate" that turned out to be a parent/child pair. **If it is yours, it is running the ungated `/pop` on localhost; retire it when you are done.**

Phoebus's real posture, verified: launchd pair on `dcd87fd`, `/pop` gated, POST `/msg` gated, port 8766 held by the managed process.
