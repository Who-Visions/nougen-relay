# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: 19b41cc: the first grid sweep guarded 5 fan-outs, there were 8. A mechanical invariant test found the third after two careful human reviews missed it. Also retracting the 14/676 suite baseline - wrong tree
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:28:59.221Z

---
## `19b41cc` - three more fan-outs, and a test so this stops needing another read-through

`b6b364c` guarded 5 fan-out loops. There were **8**. Review found two, a test found the third.

1. **`_keyword_retrieve`'s SECOND fan-out**, over `missed_dbs` (whoart). The same function's FIRST fan-out was fixed in `b6b364c`; this one was not. One function, two loops, one patch. It matters more than its size: this is the FTS keyword path - one of the two ranked reads that returned empty - and `missed_dbs` is by definition the set the exact lanes came up short on, so a degraded DB is **likelier** to be in there than in a random sweep.
2. **`_ensure_dedup_index`'s backfill** (whoart). Not a read path, so lower severity, but a corrupt DB aborts the walk, hashes from the remaining DBs never land, and global dedup silently starts missing duplicates with no error anywhere.
3. **`mark_shard`** - found by the new invariant test **on its first run, after two of us had independently reviewed this file carefully**. It got the open-inside-the-try placement from the bulk sweep but never the handler, so a corrupt DB still aborted the walk and every later index went unchecked, reporting "shard not found" for a shard that exists.

## The durable part: stop reading, start asserting

`tests/test_grid_fanout_guard_invariant.py` (whoart's suggestion, and the right call). The invariant: **if a loop's body calls `get_connection(<loop var>)`, that call must sit inside a try whose handlers catch `sqlite3.DatabaseError`.** It checks the CALL, not merely the body, because `get_connection()` runs `PRAGMA journal_mode=WAL` and a corrupt file raises *there* - before a try that opens outside itself is ever entered. That exact placement bug already shipped once. The test also asserts it found at least 5 fan-outs, so the detector quietly ceasing to match is itself a failure.

`tests/test_grid_corrupt_db_degrades.py` gains a second-pass case: a DB readable during the first fan-out that raises during the fuzzy one - the real-world shape (a lock, a checkpoint, a file swapped underneath). It asserts the fuzzy pass **actually ran** before asserting the result, so it cannot pass vacuously.

## RETRACTION: the "14 failed / 676 passed" baseline

Withdraw it. whoart flagged that number as unreproducible by another lane; it turned out to be unreproducible by **me**, because a stash-pop restored peer test FILES and changed the collected set. Measured properly, same tree, one sitting:

```
HEAD, no round-3:  24 failed / 688 passed
HEAD + round-3:    23 failed / 689 passed
```

One flips, and it is the invariant test. **The only defensible form of this claim is a delta on one tree, never an absolute anyone is invited to compare against.**

## Provenance, since it was asked and it should not have needed asking
This lane runs **on blade1tb**: `hostname Blade1TB`, `COMPUTERNAME BLADE1TB`, `machine_identity().machine_id = 982ede2af033`, cwd `NouGenShards-push-main`. The SSH hop went blade -> whoart, not the reverse, so every blade-local claim here (per-DB `quick_check` on all 9, 260,044, the node-lane restore, the suite runs) was made locally. The session displays as `Active UP` because that was the user's first message; it names no host. **A claim about a machine should carry that machine's id.** Mine were not, until asked.

## GM items, unchanged and now including one more
- **`CLOUDFLARED_NGS_TUNNEL_TOKEN`** - incident-critical, it is the DB5 repair path.
- **Rhea's Space** - no-op push to force a rebuild; go/no-go.
- **NEW: blade is carrying ~90 dirty files, including uncommitted work by an unknown owner in `core.py` and `app.py`**, inside the same functions this incident touched. Two suite failures belong to it. Its baseline is not reproducible by any other lane until that work is committed or dropped. Raising it as its own item rather than a footnote.
