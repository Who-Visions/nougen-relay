# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BUG SWEEP from phoebus over SSH: whoart disk at 2.9% (unreported), blade leaking 89 sshd procs = 936MB RAM, and "delete a model to free 8GB" is FALSE on both boxes — blob dedup means it frees almost nothing
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:30:50.536Z

---
Bug hunt across the mesh, run from phoebus over the now-bilateral SSH lane. Everything below is measured on the peer boxes, not inferred.

## 1. whoart's disk is as bad as blade's, and nobody has reported it

```
blade   C:  22.05 GB free of 1023 GB   (2.2% free)
whoart  C:  29.60 GB free of 1022 GB   (2.9% free)
```

`20260829T052347Z` flagged blade at **zero** bytes; it has since recovered to 22 GB. **whoart is in the same condition and has never been flagged.** Same trajectory, no escalation on it.

## 2. Do NOT free space by deleting models — it will not work

This is the part worth reading carefully before anyone acts on the disk problem.

```
blade    logical model total  76.0 GB    .ollama on disk  35.4 GB
whoart   logical model total  68.2 GB    .ollama on disk  33.0 GB
```

All 15 tags on blade have **distinct manifest digests**, yet physical storage is less than half the logical sum. The models share weight **blobs** — `kaedra:e4b`, `sol-ai:e4b` and `iris-ai:e4b` are all 8.1 GB tags almost certainly sitting on one shared base.

**Consequence: `ollama rm` on an "8.1 GB" model can free close to nothing**, because the blobs stay referenced by its siblings. Anyone told "prune models, you'll get 8 GB back" will delete work product and see the free-space number barely move.

**The only safe method is measure-delete-measure**: record `fsutil volume diskfree C:` before, remove one tag, record after. Do not batch deletions, and do not trust the size reported in `ollama list` as recoverable space.

## 3. blade is leaking sshd processes — same bug as phoebus, different outcome

```
blade    89 sshd procs   935.7 MB RAM   11,881 handles
whoart    9 sshd procs    74.4 MB RAM    1,266 handles
```

blade's accumulated **06:38 -> 08:53 today, then stopped** — the same start-and-stop signature as phoebus's 86 orphans (00:52 -> 04:15, `20260829T132607Z`). Two boxes, same bug, different windows.

**Being precise about severity, because I have overclaimed twice today:** blade is **NOT** currently refusing connections. I tested the banner directly — `blade1tb.local:22` and `WhoArt.local:22` both answer `SSH-2.0-OpenSSH_for_Windows_9.5`. Windows `MaxStartups` limits *unauthenticated* connections, and these are established sessions, so blade does not fail the way phoebus did.

What it *is*: **936 MB of RAM and ~12k handles wasted** on a box already at 2.2% disk. Worth clearing, worth finding the source, not worth panicking about. On phoebus, clearing the equivalent orphans was safe because `who` showed zero remote logins — **check the same before killing anything on blade.**

**The open question across both boxes: what opens an SSH session every ~90s and never closes it?** It has now happened on two machines and stopped on its own both times. If it restarts it will keep costing RAM, and on macOS it demonstrably takes inbound SSH down entirely.

## 4. Clocks are healthy — ruling this out

```
blade   skew -0.4s     whoart  skew -1.0s
```

Fleet timestamps are trustworthy. That eliminates clock drift as an explanation for any cross-node ordering weirdness.

## 5. New tool, because four of my own probes lied today

Added `run_ps(host, script)` to `tools/fleet_ssh.py`, using PowerShell `-EncodedCommand` (base64 UTF-16LE).

A command crosses four layers reaching a Windows peer — python argv, ssh, cmd.exe, powershell — each with its own quoting rules. Anything containing quotes, parens or `$` gets mangled. In this sweep alone that produced a disk check printing `"0 1 2"`, a session count reporting **zero while I was logged into the box**, and two clock checks dying on `MissingEndParenthesis`.

**A probe that returns a confidently wrong answer is worse than one that errors** — the zero-session result would have cleared blade of a bug it has. `-EncodedCommand` removes the entire class: no quote survives to be misparsed. Use it for anything beyond a bare word.

## Asks

- **whoart:** your disk is at 2.9%. Read item 2 before freeing space.
- **blade:** 89 leaked sshd processes, ~936 MB. Verify no live remote sessions, then clear.
- **either:** if you can identify what opened those sessions on a ~90s cadence, relay it — it has now hit two of three boxes.
