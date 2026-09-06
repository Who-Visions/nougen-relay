# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Continue relay control-plane Phase A from completed recon, write war-game, and begin implementation without restarting discovery
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:05:51.099Z

---
Dave explicitly said: keep going, write the war-game and start Phase A. Continue leg 20260903T015748Z from the recon already completed in the live Claude session; do not redo the three worker sweeps unless evidence is missing.

RECON ALREADY LANDED IN SESSION:
- Claim/lease map: three overlapping claim stores already exist; relay daemon lease path has upstream GitHub SHA/CAS fencing but local path is still read-then-write. The connector `relay_claim_list` is served from the remote Worker rather than the local relay repos, explaining how it can report zero while work exists.
- Windows spawn audit: NouGenMsg/hooks spawn PowerShell per message without no-window flags/explicit encoding; Ollama/Exa MCP launchers pass through visible cmd at session start; grid supervisor probes tunnel through unflagged PowerShell from a windowless parent; hook path still has a cp1252-exposed git subprocess.
- Historical truth: direct Git census on 2026-08-31 was 721 legs / 217 open. Current full census worker was still running when the session excerpt ended. Finish that census from the registry directly before publishing today's count.

NEXT ACTIONS, IN ORDER:
1) Finish direct current Git census and classify counts by raw status, age, source lane, and whether evidence already proves completion/supersession/blocking. Do not mass-ack.
2) Write `wargames/relay-control-plane.md` before implementation. The war-game must inventory the three existing claim stores and designate one canonical live claim authority rather than creating a fourth. Include migration/rollback, crash/zombie scenarios, duplicate delivery, stale lease, Worker/local divergence, Git outage, hot-index loss, and Windows no-window regression scenarios.
3) Phase A implementation should be the minimum safe slice: canonical claim state adapter/materialized index over the existing subsystem; deterministic admission before claim; atomic CAS acquisition with lease_id + monotonic fencing_token; heartbeat/release/reclaim; connector `relay_claim_list` backed by live leases; no-terminal/no-focus hot-path helpers and UTF-8 subprocess discipline. Preserve Git as durable ledger/fallback.
4) Tests must prove: two workers cannot both own one leg; expired owner completion is fenced; graceful release makes work immediately claimable; actionable backlog + healthy eligible worker cannot remain zero-claim beyond bounded scheduler interval; remote Worker/local state cannot silently diverge; console-less subprocess flags are used on Windows; one bad Unicode leg cannot sink the pass.
5) Publish before/after: exact Git census, actionable count, active leases, stale/debt count, claim latency p50/p95/p99, create-to-visible, drift, and terminal-spawn audit. Shard and relay exact code refs/commit/test counts.

Do not let local Ollama grant permissions or decide evidence closure. It may cheaply triage/summarize the backlog only; deterministic rules and evidence own lifecycle changes.
