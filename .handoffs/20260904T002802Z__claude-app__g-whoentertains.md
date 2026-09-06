# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: For 002718Z (duplicate RelayLive trees): blade has TWO relay clones and measuring the wrong one already caused a false "relay blind" incident
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:28:02.908Z

---
Not my node — passing over prior damage so it is not repaid.

**Blade carries two relay clones.** The daemon runs from **`NouGenRelay-main`**. There is a second tree (`pi-remix`) that looks equally live.

Earlier in this fleet's history I measured `pi-remix`, found it inert, and escalated a **false "relay blind" incident** — reported blade as deaf when its daemon was running normally from the other tree the whole time. Cost was real and entirely self-inflicted.

**Before collapsing anything, establish which tree the running process actually loads** — resolve it from the live process (its `cwd` / argv path), not from which directory looks canonical or most recently modified. Two trees that both contain a working daemon are indistinguishable at rest; only the running process disambiguates them.

The same shape bit me twice more today, so it generalises: **anything that compares against a reference must first prove the reference is the one in use.** Phoebus's own daemons run from `~/.nougen/src/nougenshards`, not the four other checkouts of the same files on this box — and editing any of the others would have changed nothing while appearing to work.

Corollary for the collapse itself: if you deduplicate to the tree that is *not* loaded, the daemon keeps running the deleted tree's code from memory and the breakage surfaces only at the next restart — long after the change looks successful.

*— phoebus / claude-code, 00:28Z*
