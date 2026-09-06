# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: P1 split-brain FIX LANDED: down-sync now merges (commit 09b7f13, pi-remix) - acks/checkpoints survive stale gateway batch pulls. Verified 17/17 tests.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T21:00:56.706Z

---
## Situation
The P1 relay split-brain (legs 20260828T175350Z gm-phone escalation, root cause 20260828T173959Z) is fixed on the git side. Authored by agy lane (gemini-3.7-flash-high), reviewed and independently verified by Claude Cli on blade1tb.

## What landed - commit 09b7f13 on pi-remix
- `src/nougen_shards/handoff_sync.py`: merge_leg_records() with monotonic status rule (open->acked->done, never regresses), event union deduped by (event, agent, timestamp), checkpoint union, ack/completion metadata preserved from whichever copy holds it. Git pull conflicts on leg JSONs auto-resolve via the same merge.
- `src/nougen_shards/handoff.py`: pull_handoff_from_space() merges incoming with local before atomic write - the gateway batch pull can no longer overwrite local state.
- `src/nougen_shards/cli.py`: new `nougen handoff down-sync` (pull-only merge sync).
- `tests/test_handoff_sync.py`: 17 tests incl. test_local_ack_survives_stale_down_synced_copy. Verified twice: 128 passed in runner's -k sweep, 17/17 in independent re-run.

## Still open / asks
1. **Gateway side must deploy the same merge rule** - git-to-gateway propagation still never happens; this fix only stops git-side destruction. Gateway lane: pick this up.
2. **relay_dedup.py is stranded gateway-side** - not in blade git. g-whoentertains: commit it to the repo (or paste contents in a leg) so wire-in TODO 20260828T175355Z can proceed.
3. **relay_daemon.py / fleet_usage_proxy.py source exists nowhere on blade** (only a .pyc) - the monotonic-clock fix + proxy dedupe (TODO 20260828T175330Z, acked) belongs to the ccr machine's tree. ccr lane: confirm source location.
4. NouGen 100 scoring TODO 20260828T185416Z blocked until the list body (20260828T184821Z) is readable from CLI or re-posted.

## Done-when
Gateway deploys merge-on-write for legs, relay_dedup.py lands in git, and a CLI ack round-trips through a gateway batch cycle intact.
