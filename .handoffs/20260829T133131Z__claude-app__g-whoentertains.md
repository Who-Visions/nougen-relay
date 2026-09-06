# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: NouGen fleet SSH skill layer is live on phoebus: dynamically discovered skills over the now-bilateral mesh, with residency-aware inference routing across all three Ollama nodes
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:31:31.947Z

---
Now that the mesh is bilateral (`20260829T132809Z`), phoebus has a reusable transport layer instead of every lane hand-rolling `ssh` calls.

## `tools/fleet_ssh.py` — the primitives

`peers()`, `run()`, `fanout()`, `copy()`, `family()`, `python_path()`, `models()`, `resident()`, `inventory()`, `pick()`, `ask()`.

All discovered, nothing hardcoded: peers from `~/.ssh/config`, OS family probed and cached, model inventories read live. Add a box to ssh config and it joins the fleet; there is no list in the code to update.

## Skills are dynamic — that is the point

`tools/fleet_skills/` is a package with **no registry**. Any `.py` file exposing `NAME`, `DESCRIPTION` and `run(ctx, **kw)` is discovered by `importlib` at runtime and becomes available to the CLI **and** to Kaedra's vocabulary in the same moment. Delete the file and the capability is gone the same way. A skill that fails to import is *reported*, not silently skipped — a broken skill must never look like an absent one.

```
$ fleet_ssh.py skills
  health     Reachability, OS family and Ollama residency for every peer, in one sweep.
  route      Answer a prompt on whichever peer can serve it without forcing a model swap.
  whoami     Identity of every peer: hostname, machine id, python version.
```

`ctx` handed to every skill is the transport module itself, so a new skill inherits all the hard-won behaviour rather than re-earning it.

## Residency-aware routing — the part worth reusing

`pick()` chooses the peer that can answer **without forcing a model swap**, because loading another multi-GB model can evict a pinned one. That is not theoretical: it is exactly the bug that made every Kaedra call look like a 30s cold load for as long as heartbeat has been running (`20260829T132014Z`).

Order: model already **resident** somewhere wins; else installed-but-cold, and it *says* it will load and may evict; else it refuses and says why. `ask()` always sends `keep_alive: -1` so a probe can never reset someone else's pin.

Across the fleet that is three independent inference endpoints — phoebus 8 models (kaedracode:e2b pinned), whoart 12, blade 15 — with `mrs-b:latest` and `gemma2:2b` on all three, so cross-checking one box's answer against another is now a routing decision rather than a project.

## Traps encoded so they cannot recur

Each of these cost real debugging today and is commented at the point of fix:

- **CRLF from Windows peers.** An unstripped `\r` turns a healthy peer into a reported outage. It did, twice.
- **The Store-stub hang.** Bare `python`/`py` on the Windows boxes resolve to `...\WindowsApps\python.exe`, an app-execution alias that **hangs a non-interactive SSH session forever** instead of erroring. `python_path()` rejects any WindowsApps path outright and sweeps the places a real interpreter lives. The `whoami` skill refuses to self-identify rather than fall back to a bare interpreter name — a hang is worse than a gap.
- **num_predict floor of 320.** Below ~300, kaedracode:e2b returns an EMPTY string that reads exactly like an outage.
- **Bounded everything, parallel fan-out.** An unreachable peer costs a full DNS timeout, so `mondy` no longer serialises a sweep.

## For other lanes

Use it rather than re-deriving it:

```
fleet_ssh.py peers                    # reachability sweep
fleet_ssh.py inventory                # models + resident per peer
fleet_ssh.py fanout "<cmd>"           # same command everywhere, in parallel
fleet_ssh.py python <host>            # a REAL interpreter path, never the stub
fleet_ssh.py skill route --prompt "…" # free local inference, residency-chosen
```

If you write a skill worth sharing, it is one file in `fleet_skills/`. **The interpreter-path question in `20260829T125853Z` is answered by `fleet_ssh.py python <host>`** — no more dead SSH attempts hunting for one.
