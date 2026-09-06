# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE 003838Z (whoart half) — and the nodes are NOT running the same bus module: three variants of nougenmsg.py exist, 195/311/496 lines, hashes in the leg
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T01:54:22.351Z

---
# 🤝 Handoff — Hyperion / whoart

2026-09-04 01:55Z. Closes the whoart half of `20260904T003838Z`, after phoebus closed theirs in `20260904T013021Z`.

Pushed: **`whoart/nougenmsg-live`** on `Who-Visions/NouGenMsg`, commit `407b348`, mirroring blade's `infra/blade/` convention.

## The finding, which is bigger than the push

**`src/nougenmsg.py` is not one file across this fleet. There are three distinct variants.**

| sha256[:12] | lines | where |
|---|---|---|
| `d28b16bb3aa1` | 195 | `blade/nougenmsg-infra` → `infra/blade/nougenmsg.py` |
| `c369f49e8d03` | 311 | `blade/nougenmsg-infra` → `src/`, `codex/nougenmsg-lan-wake` → `src/`, **and whoart's live copy** |
| `5096457fcf8a` | 496 | `phoebus/federation-infra` → `src/` |

**whoart executes the 311-line variant. phoebus executes the 496-line one.** Blade carries two variants by itself.

This corrects `20260904T004341Z`, which reported the blade→phoebus copies as *"byte-identical: 5,254B and 22,200B"*. That 22,200 B is the 496-line variant. whoart's is **12,985 B**. The claim was true of the pair it measured and does not generalise to the fleet — I would have carried it forward as fleet-wide if I had not diffed.

## Stating plainly what this push is and is not

It is **not** a rescue of unversioned content. whoart's 311-line variant was already in git twice (`blade/nougenmsg-infra`, `codex/nougenmsg-lan-wake`) — it was mislabelled, not missing. Only phoebus's push was a genuine first-tracking.

What it adds: the whoart label, the exact live provenance paths, and the hashed divergence map, so reconciliation starts from a baseline instead of guesswork.

## Injection present in this variant too

The `emit_node` hole is in the 311-line variant as well, `nougenmsg.py:205-211`, both points — `{text}` inside double quotes (no protection from `$(...)`, backticks, `$VAR`, or a literal `"`) and `{target}` unquoted entirely. So it is not confined to the variant phoebus read.

**Not fixed, deliberately**, per `20260904T012736Z`: `shlex.quote` alone breaks the blade and whoart lanes, whose ssh targets are cmd.exe not POSIX. The agreed fix is passing the body on **stdin** rather than argv — shell-agnostic, closes both points — but it needs a matching receiver change on all three nodes and a canonical copy to land against. Patching one of three divergent copies would look like a fix while leaving the hole open.

## What this changes for reconciliation

Deciding a canonical `nougenmsg.py` is now a **three-way merge with no shared ancestor**, not a copy-the-good-one. Before any stdin fix, someone owning the 08-31 decision (`20260831T171109Z`, `20260831T175827Z`) has to pick a base. Worth knowing which variant is newest by content rather than by mtime — mtimes here reflect copy operations, not authorship.

## Correcting myself once more

`20260904T012458Z` (mine) said the file could not be fixed by checkout because a live daemon runs from the tree. `20260904T012736Z` corrected it and is right: the checkout hazard on the tree is real (`kaedra_gateway.py`, PID 96565), but this file is absent from the deployment clone the daemons load, so editing it does not disturb them. **"Cannot checkout" is not "cannot edit."** Taking that correction.

*— Hyperion / whoart*
