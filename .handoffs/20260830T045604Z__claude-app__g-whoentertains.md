# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to leg 20260830T044908Z: that purge was INCOMPLETE — git grep only sees tracked files, and canon/metamers-protocol.md was untracked. Now finished; 'metamer' deliberately KEPT as technical vocabulary
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:56:04.327Z

---
## Correction

Leg `20260830T044908Z__claude-app__g-whoentertains` claimed the Valerion purge was complete. **It was not.** That sweep used `git grep`, which only searches **tracked file contents** — so it missed (a) every file whose *name* carried the drift and (b) all untracked/gitignored files. The canonical protocol document itself was in the blind spot.

Anyone auditing naming: do not trust a `git grep` sweep alone. Use `find -iname` for names and a plain `grep -r` for untracked content.

## Now fixed

**Renamed** (all three were untracked, which is why they were missed):
- `canon/metamers-protocol.md` → `canon/valerion-protocol.md`
- `canon/metamers-run-002.md` → `canon/valerion-run-002.md`
- `analysis/jarvis-metamers/` → `analysis/jarvis-valerion/` (and `jarvis-metamers.md` → `jarvis-valerion.md`)

**9 content edits**, all NAME uses only: `# METAMERS — orchestration protocol` → `VALERION`, the `METAMERS verbs` table header, `METAMERS Run 003`, the `jarvis → NouGen: Metamers Synthesis` title, the `**Protocol:** metamers` line, and the verbatim verb-list token.

**1 real breakage repaired:** `analysis/jarvis-valerion/fleet_transpose.py:19` had `OUT_DIR` hardcoded to the old `jarvis-metamers` directory, which the rename would have broken. Now points at `jarvis-valerion`; `py_compile` clean.

## Deliberate: "metamer" is KEPT as technical vocabulary

25 occurrences remain in the canon docs and they are **correct**. These documents *define* the term and build their argument on it:

> "A metamer is two physically different stimuli producing an identical percept."
> "Metamerism is observer-relative. Two spectra metameric to a [given observer]…"
> "A units error *is* a metamer failure."
> "A metamer is safe iff a cheap verifier can reject divergence at the point of use."

Run 002's whole ternary PARAMETRIC/RETRIEVE/UNSOLVED framework rests on metamerism as a concept, and `verify_metamers()` is a proposed dream.py phase. Purging this would gut a 49 KB research document. **Same standing as TMEM in commit `71f598a`: genuine technical term, not drift.** The *protocol* is named Valerion; the *concept* stays metamer. Reversible with one sed if the GM disagrees.

`canon/valerion-protocol.md` line 3 carries a canon lock ("given verbatim 2026-08-08, do not paraphrase the verb list") and the drift word sat inside it. Rather than silently rewrite a verbatim artifact, a dated provenance line was added recording the operator-instructed rename.

## Still open

1. **Three stale agent worktrees** at pre-purge commit `bc73a539` (dated 2026-08-08 / 2026-08-16) still hold `metameric_deep_sweep.py` and `metameric_longform.py`: `.claude/worktrees/busy-euclid-e483a6`, `busy-sanderson-6defde`, `gracious-shirley-fd2f39`. Not touched — editing detached checkouts creates confusing dirty state. Candidates for `git worktree remove`. Two further worktrees already report `prunable`.
2. **`NouGen\.vault\nougen_shards_{5,6,7,9}.db` contain the old strings** — that is the *stray* vault from the cwd trap, not `~\.nougen\shards`. Worth deciding whether that vault should exist at all.
3. GEMINI.md Rule 0.7 collision — unchanged, still needs a decision (see prior leg).

## Done when

Naming is verified by `find -iname` **and** `grep -r`, not `git grep` alone; the stale worktrees are pruned; and the stray `NouGen\.vault` is resolved.
