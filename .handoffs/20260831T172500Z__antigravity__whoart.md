# 🤝 Git Handoff — antigravity / whoart

**Goal**: Patched and verified `shards_window` / `recall_window` defect (closing leg `20260831T170210Z`)
**Branch**: `main`
**When**: 2026-08-31T17:25:00.000Z

---

## Accomplishments

1. **Root Cause Analysis (`shards_window` / `_window_search`):**
   - In `app.py`, `_window_search` previously used non-ASCII character padding (`until + "\uffff"`) which raised `UnicodeEncodeError` / collation failure on Windows SQLite and swallowed all errors with `except Exception: continue`, returning `[]` empty results.
   - Database iteration did not guarantee global reverse-timestamp ordering when individual DBs had sparse timestamps.

2. **Patch Applied & Verified:**
   - Implemented `_normalize_iso_bound` using strict ASCII ISO-8601 bounds (`YYYY-MM-DDT23:59:59.999999Z` and ASCII `~`).
   - Added content summary truncation support (`summary=True`).
   - Reversed database scan (`core.MAX_DB_COUNT` down to 1) with global timestamp sorting.
   - Deployed across **WhoArt**, **Blade**, and **Phoebus**, and verified on live Node `:4444`.

3. **Falsifier Passed:**
   - `_window_search(since="2026-08-31", until="2026-08-31")` on Blade now returns all 10 newest August 31 shards (IDs `17155`, `17142`, `17401`, `17391`, `17386`, etc.) in global newest-first order.
   - Leg `20260831T170210Z` is closed.
