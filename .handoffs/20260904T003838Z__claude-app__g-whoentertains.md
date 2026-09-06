# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: BLADE + PHOEBUS: push your NouGenMsg branches to github.com/Who-Visions/NouGenMsg — Dave's instruction, node branches already exist and are ~6h stale
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:38:38.476Z

---
# 🤝 Handoff — for blade and phoebus

Filed by claude-app / g-whoentertains (super-1a) at 2026-09-04 00:38Z. **This is Dave's instruction, relayed — not my request.**

## The ask

Push your local NouGenMsg work up to **https://github.com/Who-Visions/NouGenMsg** (private).

## What is already there

The per-node branch convention exists and both your lanes have one:

```
blade/nougenmsg-infra      3d96727d  2026-09-03T18:53:46Z  "Add lane infrastructure snapshot"
phoebus/federation-infra   c49b929a  2026-09-03T18:53:43Z  "Add lane infrastructure snapshot"
codex/nougenmsg-lan-wake   1331234e  2026-09-03T18:51:56Z  "Add Codex NouGenMsg lane baseline"   <- repo default branch
```

All three are ~6 hours stale as of this leg, and all three read as one-shot snapshot commits. Anything either of you has done on NouGenMsg since ~18:53Z today is local-only and invisible to the other nodes and to Dave.

**blade** — push to `blade/nougenmsg-infra`, or a new `blade/<topic>` branch if your current work does not belong on the infra snapshot.

**phoebus** — push to `phoebus/federation-infra`, or a new `phoebus/<topic>` branch on the same reasoning. Note this is a *different repo* from the ngsnode checkout you said you are deliberately holding on branch `node-too` with `mcp<2` pinned; holding that one back does not block pushing NouGenMsg work.

Note the repo default is `codex/nougenmsg-lan-wake`, not `main`, so a bare `git push -u origin HEAD` from a fresh clone will not do what you expect — name the branch explicitly.

## Why it matters beyond tidiness

The msgnode auth gap, the bus-token work and the transport findings from tonight all live in this repo's territory. Two things from the last few hours make unpushed local work a real risk rather than a housekeeping nit:

1. **Relay truth path** — an existing captured finding says only GitHub `Who-Visions/NouGenRelay` main is canonical and node-local relay writes never reach it. Same shape applies here: work that exists only on a node's disk is invisible to every other lane, however real it is locally.
2. **Silent shard loss is unresolved** (legs 20260904T003437Z, 20260904T003624Z). Capture is dropping writes intermittently — confirmed absent from all nine phoebus vaults, with one success at 00:02:08Z proving the path is not dead, just unreliable. **While that is open, git is the trustworthy durable store and shards is not.** Anything you would otherwise rely on a capture to preserve should be a pushed commit.

## Done when

Both node branches show commits newer than 2026-09-03T18:53Z, or a lane states plainly that it has nothing local to push — which is a valid answer and worth saying out loud rather than leaving silent.

## Still open from earlier, unrelated to this ask

**blade**: 20260904T003624Z needs blade to run the same read-only vault grep phoebus ran. `shards_capture` writes through blade's gateway, so phoebus can only prove absence from phoebus's disk. Until blade greps its own DBs for `%claude.exe%`, `%green CI run%` and `%claim about a SHA%`, the three lost writes could be sitting on blade written-but-unsearchable — the exact hypothesis that grep was meant to exclude. Confirmed absent from phoebus; global status unknown.
