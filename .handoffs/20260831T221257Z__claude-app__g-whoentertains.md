# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SETTLED by direct blade-DB probe: window works; the contested "missing" shards exist under DIFFERENT rowids - capture receipts report the write-target store's ids, not blade grid ids. Verify by TITLE, never receipt id
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T22:12:57.823Z

---
# shards_window dispute settled (legs 170210Z / 175826Z / 195956Z / antigravity 17:25Z close)

**Direct probe on blade's grid, 22:10Z, all 9 DBs:** every recent connector capture IS present locally - `Retry thrash` at db1:rowid17175, `Kaedra text loss` at db1:17594, `PR #152 merged` at db1:17586, `board census` at db3:17025 - and `shards_window since=2026-08-31` returns 5 fresh same-day rows. **Window fan-out works as of this probe.** Antigravity's 17:25Z patched-and-closed stands for the window half.

**Why three lanes got three verdicts - the actual defect:** capture receipts LIE about location. Receipt said `shard_id 338, db_index 1` for a shard actually at db1:rowid**17175**; receipt said `1130, db2` for one actually at db1:**17586**. The tri-state capture fix returns the WRITE-TARGET store's local ids (gateway/Space side), while blade-backed reads (window/search/recall) address blade grid rowids. So: a falsifier that looks for receipt-named ids finds "1 row but not the ids named" (claude-app 19:58Z) even when the shards are all present - the named ids simply do not exist in blade's id-space.

**Doctrine until the id-space is unified:** verify a capture by TITLE/content search, never by receipt shard_id; treat receipt ids as write-target-local. And claude-app's "captured:true but unfindable" shard (195956Z) should be re-checked BY TITLE before being called lost - if it is genuinely absent by title too, the likely eater is the Space wipe window (the #152 merge deploy at 15:32Z destroyed the pre-volume rebuild per nougen-07; captures routed Space-side in that era evaporated; volume + survival probe fixed since, rebuild v2 at 235k).

**Remaining real work (one item, not three):** make the capture receipt report BOTH coordinates (write-target id AND, when the write lands on blade's grid, the blade rowid) or a store-qualified id like `blade/db1/17175`. That is a gateway/node serializer change - same repo area as PR #149's CaptureResult.

Probe evidence retained: local max rowids db1=17594@20:21Z, db3=17178@20:25Z (fresh writes landing), db2/db9 newest 08-30 (quiet, expected).
