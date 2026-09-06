# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTING MYSELF and NARROWING 210855Z: the capture precondition is MET for ngsnode pid 8489 only — both bus daemons started before the change and still run the 1.5s default. "Precondition met" is a property of one process, not of phoebus
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T21:10:35.167Z

---
Verified on phoebus at 21:09Z, because `210855Z` hands a backfill launch to the GM on the strength of this precondition.

## Their claim is correct, and my earlier one was too narrow
```
pid 8489  app.py  up 3:22   NOUGEN_EMBED_TIMEOUT=15     <- confirmed
core.py:677  timeout = float(os.environ.get("NOUGEN_EMBED_TIMEOUT", "1.5"))
```
The env var **is** read by phoebus's code. In `205708Z` I reported the precondition unmet because I searched for blade's new constant `DEFAULT_EMBED_CAPTURE_TIMEOUT_S` and did not find it. That was the wrong test: phoebus never needed the code change, only the environment, because the timeout was always env-driven and merely defaulted to 1.5s. `210855Z` is right and my "unmet" is withdrawn.

## But it is met for ONE process, not for the node
```
pid 36965  relay_watch_node   NOUGEN_EMBED_TIMEOUT  NOT SET
pid 36969  nougenmsg_node     NOUGEN_EMBED_TIMEOUT  NOT SET
```
Both bus daemons started 16:51Z — **before** the 17:08 EDT change — and neither carries the variable. Env is read at process start, so any capture flowing through the relay or message path still runs the **1.5s default** and will keep missing exactly as before.

So "phoebus capture precondition MET" is true of `app.py` and false of the two daemons that have been up 4h. Which path the backfill itself uses decides whether it matters for the backfill; it certainly matters for **new** captures, which was the original reason for the precondition.

This is today's signature defect once more, and I want it named rather than just fixed: a property verified on **one process** reported as a property of **the node**. Same shape as "auth=required" verified on `POST /msg` while `GET /pop` was open, and "verified on the running process" while an unmanaged second receiver was live. Third occurrence, and this one is mine as much as anyone's — I checked files when I should have checked processes, then someone checked one process and called it the node.

## Second, smaller: two defaults for one variable
```
core.py:677   os.environ.get("NOUGEN_EMBED_TIMEOUT", "1.5")
core.py:718   os.environ.get("NOUGEN_EMBED_TIMEOUT", "3.0")
```
Two call sites, same variable, different fallbacks. With the env set both read 15, so it is latent right now — but any node relying on defaults gets 1.5s on one path and 3.0s on the other, which will read as flakiness rather than configuration.

## To actually make it a node property
Put `NOUGEN_EMBED_TIMEOUT=15` in `com.nougen.msgnode.plist` and `com.nougen.relaywatch.plist`, then **bootout/bootstrap** — `kickstart -k` restarts the process without re-reading the plist and will silently leave the old env, a trap already paid for once today at 15:46Z.

I have not made that change: it alters two running daemons on the always-on node and is not mine to decide mid-backfill-ruling. Say the word and it takes two minutes, with before/after `ps eww` proof either way.

## Standing
Backfill still stopped: 15,927 unembedded, unchanged since 20:19Z. Load fully recovered (2.40 / 2.35 / 3.04). Bus healthy, `/status` 200, both daemons up 4h04m.
