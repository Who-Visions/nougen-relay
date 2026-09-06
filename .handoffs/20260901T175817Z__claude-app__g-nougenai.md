# 🤝 Git Handoff — claude-app / g-nougenai

**Goal**: War-gamed shard hardening backlog: correct shipped/superseded items and execute truth gates before recall tuning
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T17:58:17.583Z

---
## Active Incidents
- No new outage verified. Canonical health and MCP lanes return 200/RPC OK.
- Truthfulness incident remains: the 100-item artifact says "nothing shipped," but shard 16632 proves domain-mask, OR-retry, BM25 fixes and regression tests already shipped; shard 17192 proves a guarded fleet deployer already exists.

## Ongoing Investigations
- War-game conclusion: execute by dependency, not artifact category order.
- P0 truth gates: origin-vs-connector parity, structuredContent/content contract, isError propagation, schema/code/node identity, trustworthy completeness semantics.
- P1 deploy/durability: canonical versioned worker source, quarantine stale deploy path, bindings/config backup, pre/post smoke and rollback, restart-survival persistence probe.
- P2 federation/data: self-identity loop guard, hop ceiling, quarantine, network-volume journal policy, write-read-restart canary, offline restore drill.
- P3 retrieval quality: inventory existing guards before adding tests; golden ranking set, score explanation, supersession/correction ranking, domain canaries.
- P4 frictionless CLI/auth and status UX only after truth and safety gates hold.

## Recent Changes
- Read current relay/open queue/claims: 20 open legs, no active claims.
- War-gamed five coupled attacks:
  1. dropped MCP payload -> false empty -> observer-derived wrong RCA -> destructive repair risk;
  2. stale duplicate deploy -> silent 366-line rollback -> absent smoke -> false success;
  3. self-loop + timeout + swallowed isError -> laundered complete=true;
  4. delivered writes without restart-survival proof -> apparent rebuild evaporates;
  5. RRF final_score treated as relevance -> invalid thresholds and cross-query comparisons.
- No repo or production mutation.

## Known Issues & Workarounds
- Shard 17738 corrects the record: the self-loop was bad hygiene but did NOT cause the empty-recall incident; structuredContent payload loss did.
- Shard 17190 is superseded on temporal_meta/data-loss claims: open leg 20260901T160920Z reports all 9 DBs healthy with temporal_meta; stale code remains a separate concern.
- Before execution, convert the artifact into a ledger with status: proposed / already-shipped / verified-live / superseded / blocked, plus owner and evidence.

## Upcoming Events
- First implementation slice should be the P0 truth gate + live contract probe, followed by the deploy/durability gate.
- Done when a single synthetic query is proven identical at origin, worker content, structuredContent, and each provider renderer; errors cannot become empty success; deployment can roll back with bindings preserved.
