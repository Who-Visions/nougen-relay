# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DEPLOYED to blade: vault circuit breaker live (module verified loaded), node restarted, CPU 34,638s -> fresh. But measurement says the breaker is NOT the dominant cost: each recall still burns ~120s CPU and grows RSS ~850MB.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T14:31:09.612Z

---
Shipped over ssh and measured. Reporting what the numbers actually say, including
where my fix does NOT help.

## Deployed

- `src/nougen_shards/connectors/local_vault.py` copied to blade's checkout.
- Verified loaded, not just present:
  `module: ...NouGenShards-push-main\src\nougen_shards\connectors\local_vault.py`
  `breaker: True`
- Node restarted. `blade.nougenai.com` answers externally again.

## I caused a ~2 minute outage doing it

I stopped the old node before confirming the new one could bind, then read 60s of
URLError as a failed start and launched a second process. **The first restart had
actually succeeded** — the node takes longer than 60s to come up because it loads
~10GB of shard DBs. The second launcher could not bind and exited. Sequence
should have been: start, wait for bind, THEN stop the old one. Blade's sshd also
timed out mid-banner during this, because the box was saturated enough to refuse
handshakes.

## The measurement, and it does not flatter my fix

Fresh node, then 4 `recall_memory` calls through the tunnel:

```
before restart : cpu 34,638s   rss 2,599 MB   (accumulated ~6h)
after restart  : cpu     16.2s rss   153 MB   (7.6 min idle)
after 4 recalls: cpu    495.7s rss 3,594 MB   (11 min)
```

That is **~120s of CPU and ~860MB of RSS per recall**. Latency 10.3s / 34.8s /
15.5s / 24.8s.

`recent_timeouts=2, breaker_skips=0` — the breaker has not tripped once yet,
because it needs 3 consecutive timeouts on the same vault.

**So the breaker is not the dominant cost.** It fixes a real waste — 1,340
timeouts x 2s re-proving 26 dead stores — but that was an accumulation over
hours, not the per-query expense. The per-query expense is the sweep itself:
federating 9 shard DBs plus ~26 registered vaults, pulling ~860MB into memory
each time. Restarting reset the accumulated damage; it did not make recall cheap.

## What actually needs doing (not attempted)

1. Bound the sweep. 120s CPU per recall is the headline number, and no circuit
   breaker addresses it — the vaults being swept are mostly *alive*, just costly.
2. Investigate the ~860MB RSS growth per query. That looks like results being
   materialised rather than streamed/limited; a `limit=2` query should not cost
   that.
3. Tier-2 gating already exists (`NOUGEN_FEDERATE_TIER2`,
   `NOUGEN_FEDERATE_HOT_MAX_MB`) — worth checking whether blade has it configured
   at all, since an unbounded tier-2 sweep would explain both numbers.

## Also live from this session

- `_allowed_roots()` now always allows an explicitly declared `NOUGEN_VAULT_DIR`.
  It was cwd-relative: on whoart it resolved to `<repo>\.vault`, so the canonical
  `~/.nougen/shards` was not an allowed root at all. Blade had it right; same
  code, different answer, decided by working directory.
- Removed a **shadowed duplicate `cmd_init`** in cli.py from a concurrent merge —
  Python bound the later definition, so one implementation and its three tests
  were dead code asserting a function that never ran.
- `tools/lane_loadtest.py` and `tools/fleet_heartbeat.py` on blade too.

## Caveat on the test suite

`TestPerStoreTimeout` is flaky under load, before and after my change (3 baseline
runs FAIL/FAIL/pass; 3 with changes FAIL/pass/FAIL). It races a 0.000001s budget
against a progress handler that fires every 4000 VM ops, and `LIMIT 3` over
all-matching rows finishes first. I briefly claimed this was my regression; three
runs each disproved that. Left as found — a real fix makes the timeout
deterministic, and swapping the query term only makes `rows == []` true for the
wrong reason.
