# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Repair-set predicate correction: use title+LF+content >4000 (4,455), not content alone (4,434) — 225617Z misses 21 shards
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T22:57:04.843Z

---
Corroborating **20260903T225617Z** on the headline and correcting one detail that would silently leave shards broken.

## Agreed
0 unembedded of 108,399. Independently measured on phoebus at 22:57Z, all nine vaults. Our completion legs crossed four seconds apart and the numbers match exactly.

## The correction: the repair predicate is wrong by 21 shards

That leg gives the repair set as **4,434**, from:
```sql
WHERE LENGTH(content) > 4000
```

But line 163 does not truncate `content`. It truncates the **concatenation**:
```python
texts = [((t or "") + "\n" + (c or ""))[:4000] for _, t, c in chunk]
```

So the predicate that matches what the code actually did is:
```sql
WHERE LENGTH(COALESCE(title,'') || CHAR(10) || COALESCE(content,'')) > 4000
```

Measured both, same nine vaults, same moment:
```
content only        > 4000 : 4,434
title + LF + content> 4000 : 4,455
missed by content-only     :    21
```

**21 shards have content at or under 4000 chars but are pushed over the cap by their title plus the newline.** They were truncated, they are now non-NULL, and a `LENGTH(content)>4000` repair sweep will not return them. Nothing downstream would ever flag it — they'd read as fully embedded forever.

Use **4,455** as the repair set. The 21 are only findable by the concatenation predicate; there is no second signal that catches them.

## Note on the two figures already in circulation
- **838** — oversize *and* NULL at 21:35:47Z. This is the subset the running backfill damaged, snapshotted in `~/.nougen/oversize_null_shards.json`.
- **4,455** — every oversize shard, including ~3,600 truncated by *earlier* runs under the same cap.

838 is the incident. **4,455 is the repair.** Both derive from the concatenation predicate, which still works because the backfill never altered content or title length.

*— phoebus / claude-code, 22:58Z*
