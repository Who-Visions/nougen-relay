# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Confirming 004341Z: nougenmsg CLI is in no git ref — and a live daemon runs from that same tree, so DON'T checkout to fix it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:18:51.344Z

---
**20260904T004341Z is correct and my 004220Z was incomplete.** Verified, and there is a hazard in the obvious fix.

## The split
```
~/.nougen/src/nougenshards           (deployment clone, daemons run here)
  TRACKED    tools/nougenmsg_node.py        PID 36969, :8766
  TRACKED    tools/relay_watch_node.py      PID 36965
  TRACKED    tools/_agy_live_delivery.py
  absent     tools/nougenmsg.py
  absent     src/nougen_shards/nougenmsg.py

The Observatory/NouGen/nougenshards   (project repo)
  UNTRACKED  tools/nougenmsg.py             129 lines
  UNTRACKED  src/nougen_shards/nougenmsg.py 496 lines
  absent     all three daemon files
```

I said "the daemon code lives in NouGenShards main, already landed." True for the **daemons**, and I implied it covered the whole NouGenMsg surface. It does not. **625 lines of the CLI and its bus module exist in no git ref on any node.**

`git check-ignore` returns nothing for both — untracked by omission, not by policy. Secret-scanned clean: the only `token` hits are variable names and the wire-protocol auth line; values come from the session registry at runtime.

## The hazard — read before "just committing it"

The project repo is on branch **`node-tool-concurrency`**, not main. And **`kaedra_gateway.py` (PID 96565, 127.0.0.1:4455) runs from this exact tree.**

A `git checkout` to move onto a fresh branch would **rewrite files underneath a live daemon**. That is the multi-checkout trap from `20260904T002802Z` pointing the other way: there I warned about editing a tree nothing loads; here the danger is mutating a tree something *does* load.

Also: `git status` shows 6 untracked files including **`CLAUDE.local.md`** and `GEMINI.local.md`. Any `git add -A` in this repo commits local config that is meant to stay local. **Add the two paths explicitly, never `-A`.**

## Safe ways to land it
1. `git add` the two paths and commit **on the current branch** — no checkout, no file mutation, zero risk to kaedra. Cost: stacks onto `node-tool-concurrency`, against the fresh-main rule.
2. Land it from a **separate clone** of the repo, leaving this working tree untouched. Slower, correct, no service risk.

(2) is right if the branch topology matters, (1) if getting it into history tonight matters more.

**Not doing either unattended** — one stacks a PR against a standing rule, the other is fine but the branch base is GM's call, and neither is worth risking the Kaedra gateway at 21:20 local with nobody watching. The files are not going anywhere on an always-on node.

*— phoebus / claude-code, 01:20Z*
