# 🤝 Git Handoff — claude-app / outpost

**Goal**: OWNING LANE: 4 conflicted NouGenShards files preserved in stash@{0} on outpost (lib.rs, cli.py, App.tsx, styles.css) - tree is clean, nothing lost, pop and resolve deliberately
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:00:00.184Z

---
## Your in-flight NouGenShards work is in `stash@{0}` on outpost -- not lost, not committed

Outpost rebased NouGenShards main to push the node write tools + coverage. Your uncommitted work
was carried through with `--autostash`, and four files conflicted against the incoming HUD/
design-skill commits.

**I did not resolve them.** Resolving another lane's in-flight edits needs your intent, not my guess.

### Where things stand on outpost's checkout
- **69 of your modified files are restored in the working tree**, untouched.
- **4 conflicted files were reverted to HEAD in the tree**, so no conflict markers remain anywhere:
  - `src-tauri/src/lib.rs`
  - `src/nougen_shards/cli.py`
  - `ui/src/App.tsx`
  - `ui/src/styles.css`
- **Your versions of those 4 are intact in `stash@{0}` (18 files total)** -- verified present by name.

### To recover
```
git -C C:\Users\super\Outpost\NouGen stash show --name-only 'stash@{0}'
git -C C:\Users\super\Outpost\NouGen stash pop     # then resolve the 4 against current main
```
Mind the quoting: `stash@{0}` unquoted in PowerShell brace-expands and git rejects it.

### What landed while you were out
main moved 803f83d8 -> 9b560a42. From other lanes: HUD token-tracker/relay panels, the
mandatory-skills registry, design-skill packages, nougen-builds. From outpost: substrate_coverage,
recall_window, the shard mutation + write-only vault tools, and ops scripts under tools/.

**Before you pop:** main now resolves secrets via `NOUGEN_SECRETS_VAULT_DIR` (`~/.nougen/secrets`),
NOT `NOUGEN_VAULT_DIR`. See leg 20260815T215327Z -- get_secret returns None and it reads as
'never ingested'.

### Done when
The owning lane pops the stash, resolves those 4 against current main, and commits or discards
deliberately.
