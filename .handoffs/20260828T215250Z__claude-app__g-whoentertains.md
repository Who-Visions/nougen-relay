# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION: stall report obsolete; live defects are scope collision + duplicate emission, not stalled pickup
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T21:52:50.924Z

---
## Situation

Live read at 2026-08-28T21:2xZ via fleet connector contradicts leg `20260828T211104Z` ("relay transport works, autonomous pickup is stalled").

**1. Stall finding is obsolete — pickup already fired.**
That leg reported 0 active claims at 21:11:04. At 21:17:04 `blade1tb/codex` claimed "Implement daemon autonomous relay pickup, stale recovery, and evidence reconcile" (ttl 8h) with no manual relay/run command from Dave. Its own success criterion — active claims becomes non-zero unprompted — was met ~6 min after it was written. Nobody reconciled the leg. Treat autonomous pickup as PROVISIONALLY WORKING, not stalled.

**2. Scope collision — two workers in the same files right now.**
- `blade1tb/codex` — scope `tools/relay_daemon.py tests/test_relay_daemon.py autonomous pickup reconcile`, since 21:17:04, ttl 8h
- `blade1tb/antigravity` — scope `tools,tests,logs,src,.relay`, since 20:24:42, ttl 8h — still live, strictly contains codex's scope

The non-overlapping-claims requirement is being violated by the work item that authored it. Coarse scope tokens (`tools`, `src`) with 8h TTLs will swallow every future fine-grained claim. Claim matching needs path-prefix containment, not string equality.

**3. Duplicate emission — one event fanning out per connector lane.**
- `blade1tb/antigravity` double-claimed the identical Grand Prix scope `relay_daemon,hud,ui,keymaker` at 17:17:13 and 17:17:34 (21s apart)
- Open legs `20260828T205500Z__blade1tb__gm-phone` and `20260828T205500Z__blade1tb__chatgpt-app` — same timestamp, same machine, byte-identical Stadium Broadcast body, differing only by agent suffix

Same root cause as the shard-grid content dedup: emit path is keyed on (machine, agent) rather than content hash. Legs and claims both need it.

**4. Bad counter — do not trust in completion evidence.**
The 21:11 leg cites "relay_open remains at 20 legs." Actual unacked count is 2 (newest 40 scanned). The reported figure is reading total-ever or an unrelated field. Any completion that cites open-leg count as evidence is currently unverifiable.

## Ask

Priority order:
1. Narrow or expire the antigravity 20:24 claim (`tools,tests,logs,src,.relay`) before codex writes. Highest-risk item — active file-level conflict on an 8h TTL.
2. Implement path-prefix containment in claim-overlap detection so a coarse claim cannot silently absorb fine ones.
3. Content-hash dedup on leg + claim emit, so one event from N connector lanes lands once.
4. Fix the open-leg counter, then reconcile leg `20260828T211104Z` with the codex claim as evidence.

## Done when

- No two active claims have containing paths
- Re-emitting an identical leg or claim from a second lane is a no-op
- `relay_open` count matches unacked legs on inspection
- The 21:11 stall leg is closed with the 21:17 codex claim cited
