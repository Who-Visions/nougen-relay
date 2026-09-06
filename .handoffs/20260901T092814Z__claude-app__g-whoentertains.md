# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CLOSED: arch B verified (canary 4.5s, 235k served) AND battle-proven same day (DB2 destroyed by test fixture, restored from snapshot in minutes); doctrine set; mission that began at "80k vs 260k" complete
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T09:28:14.069Z

---
# Mission close - claude-cli (Fable 5), 2026-09-01 ~09:40Z

VERIFIED FINAL STATE: Space serves snapshot 20260831T235430Z (235,064 rows) read-only from container-local disk - canary search 4.5s, planted canary top-1. Captures forward to blade, proven through an outage (nougen-bd's forwarded write landed as blade DB1 id17616 while the Space was down). Blade grid healthy, DB2 RESTORED to 29,537 rows after another lane's test fixture destroyed it at 08:57Z (env-var fixture resolved the live vault; their handoff owns it cleanly) - the snapshot architecture's first production save, ten hours after shipping.

THE SHIPPING CHAIN: #143 recall perf -> #145 loud lane switch -> #148 sync guard -> #151 fed pool (nougen-71) -> #152 launcher singleton -> #153 recall snippets + get_shard -> #154 guard restored w/ AST tests -> #156 snapshot mode -> #157 localize -> #158 single-flight -> #170 HTTP localize. Recall: 14-35s+timeouts last Friday -> sub-4s local, 4.5s on the public Space today.

DOCTRINE (fleet-agreed, in the closing shard): verify by title read-back never receipt ids; when reads degrade verify the WRITE against the store; failed=0 proves delivery not durability - probe survival before bulk sync; the 7 indeterminate 08-30 shards must never be read as never-landed (the dedup purge destroyed the settling signal; one confirmed-dropped claim was proven false); test fixtures monkeypatch GLOBAL_DIR, never env vars.

OPEN FOR OTHER LANES: worker should return explicit unavailable + pin reads to blade while Space lags; schedule the snapshot publisher; RRF relevance floor; UPS for the Stadium (the original physical root cause, still unbought).
