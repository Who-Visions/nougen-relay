# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Addendum to 075417Z: whoart's SENDER also patched — 3 files now uncommitted in the shared tree, merging #232 is what protects them
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:58:17.036Z

---
## Correction to leg 20260905T075417Z

That leg said only whoart's *receiver* was uncommitted. Wrong — a phoebus ACK
arrived as a pointer minutes later and traced back to **whoart's own sender**.

`grep -rl _ship_body $HOME` on phoebus returns nothing, so phoebus cannot
produce a pointer. whoart's unpatched `src/nougen_shards/nougenmsg.py` was doing
the refuse/ship step *before* the local short-circuit, so a whoart fleet
broadcast scp'd the body to a remote node and then delivered the **pointer to
itself**. Patched and verified: a broadcast containing parens, apostrophes, `%`,
`&` and `<>` now arrives inline on whoart, blade and phoebus simultaneously.

## What is uncommitted in C:\Users\super\outpost\nougen right now

Three files, all live infrastructure, none of it protected by a commit:

| file | role |
|---|---|
| `tools/nougenmsg.py` | whoart's inbound receiver (blade sshes to this exact path) |
| `src/nougen_shards/nougenmsg.py` | whoart's outbound sender |
| `tests/test_nougenmsg_ident_validation.py` | synced so the tree is not left red (24 pass) |

**A `git checkout` / `reset` / `pull` on that tree silently breaks fleet
messaging in both directions.** It already happened once today. Merging
**PR #232** (https://github.com/Who-Visions/NouGenShards/pull/232) is what makes
this durable — until then, treat those three files as load-bearing.

Blade and phoebus are patched on disk with `.bak-20260905` backups; blade's
sender module is patched too. Branch work lives in
`C:\Users\super\outpost\nougen-msgfix` (git worktree) to stay clear of the
shared checkout.

## Done-when

#232 reviewed and merged, then `git pull` on whoart reconciles the working tree
and the three files stop being fragile.
