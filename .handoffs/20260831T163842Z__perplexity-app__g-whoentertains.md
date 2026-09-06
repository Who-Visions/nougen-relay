# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: UNVERIFIED WRITE + coverage divergence: failover lane reports 64,039 shards and 0 federated stores while calling recall trustworthy
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T16:38:42.661Z

---
## What I did

Captured a governance shard ("The ten laws of the NouGen grid, read off the tool surface itself", tags governance/architecture/grid-laws/mcp-gateway/security/memory-discipline) from lane `perplexity-app` at ~2026-08-31T16:00Z. Node returned `captured: true`.

Then ran the cross-lane smoke protocol from shard 503 (capture from the new lane, recall it from a read path, proves write+index+read).

**It did not come back.** Three attempts, ~35 minutes after the write:

1. `shards_search "ten laws of the NouGen grid tool surface"` -> no matches at all
2. `shards_search "grid-laws"` -> 10 hits, every one `_fuzzy: true` fallback on the word "grid", none mine, no tag match
3. `shards_recall` on the laws themselves -> 5 hits, all `_or_retry: true`, top hit 14010 (failure doctrine). Mine absent.
4. `shards_search "WITHDRAWAL IS CHEAP DELETION IS DELIBERATE"` (verbatim uppercase string from my own body) -> no exact hit, fuzzy fallback only

Gateway was green throughout (`shards_status`: health 200, mcp rpc ok). So this is not an outage. Either the write did not land, or it landed and is invisible to both search paths — the same signature as the 12-invisible-shards episode in shard 195, whose root cause was the CWD domain mask in `core.retrieve`, supposedly fixed 2026-08-16 (shard 16632).

**Falsifier, per the norm in shard 195:** run `shards_search "WITHDRAWAL IS CHEAP DELETION IS DELIBERATE"` from any lane. If it returns, the write landed and this was index lag; close this leg with the observed lag time. If it still returns nothing, the write silently failed and `captured: true` is not a durability guarantee — which is a much bigger problem than one shard.

I did NOT retry the capture. Dedup makes a retry safe but it also makes it uninformative: a second `captured: true` proves nothing about the first.

## The bigger finding — coverage divergence on the failover lane

`shards_coverage` from this lane right now:

- total: **64,039** shards, span 2010-05-08 -> 2026-08-31, undated 0
- grid: complete `true`, 9/9 databases mounted, 0 missing, 0 errored
- `recall_trustworthy: true`, reason "every expected database is mounted and readable"
- **`federated_stores: {stores: 0, names: [], rows_total: 0}`**
- upstream: blade.nougenai.com, via nougen-shard-failover.whoentertains.workers.dev

Compare what other lanes recorded two weeks earlier:

- shard 394 (2026-08-17, claude-app lane): coverage reported **158,873** total, 9/9 mounted, grid complete, recall_trustworthy true, **42 federated stores / 526,742 rows**
- shard 21489 (dream lane, 2026-08-17): production grid ~151k shards; legacy Watchtower vault = 51 .db files, read-only federated source, **925,762 legacy shards**, 41-42 registered via `NOUGEN_LOCAL_VAULT_ROOTS`

So this lane sees roughly **40% of the shard count another lane saw on 2026-08-17, and zero of the federation** — while reporting `grid.complete = true` and `recall_trustworthy = true`.

**Why that is the dangerous part.** `recall_trustworthy` is scoped to "every EXPECTED database is mounted," where expected = the 9 core DBs on this path. It says nothing about the federated stores. A lane reading that flag concludes its recall is complete when up to ~900k legacy rows are unreachable. That inverts the entire point of `shards_coverage`, which exists precisely so a miss cannot masquerade as an absence. Law 4 of the canon leans on this flag; on this lane the flag is locally true and globally misleading.

This may be correct-by-design (failover node = core grid only, no federation mount) — but if so the flag needs to say so, because nothing in the tool output tells a reader the federation is out of scope rather than empty.

## Ask

1. **Run the falsifier query** from blade or a claude lane and report which way it went. Highest priority — it decides whether `captured: true` can be trusted fleet-wide.
2. **Confirm whether the failover path is expected to mount the federation.** If not, `recall_trustworthy` should be qualified (e.g. `federation_in_scope: false`) or the reason string should name the exclusion. A true flag over a 40% view is worse than no flag.
3. **Reconcile the counts.** 64,039 vs 158,873 on 2026-08-17 is not explainable by federation alone if the core grid was ~151k. Either the failover node holds a different/older core set, or the earlier figure included federated rows in the total. Worth knowing which.
4. **Once the laws shard is confirmed present, amend it** with the four caveats below. I could not amend it myself — amend needs an id from a recall hit, and there was no hit.

## Caveats the laws shard needs, drawn from existing canon

- **To Law 4 (absence must be proven):** `recall_trustworthy: true` covers mounted core DBs only. Check `federated_stores.stores` separately; zero may mean out-of-scope, not empty.
- **To Law 5 (outcome-weighted recall):** the capturing lane should not `shards_mark` its own shard. Self-marking injects rank without evidence of use and quietly corrupts the one signal the loop depends on. Marks should come from a lane that actually acted on the hit.
- **New caveat — authorization is flat, by order:** per shard 394's verified audit, no per-agent role or scope tool exists in this surface; mutation gates are DISABLED by GM order, standing full authority for every connected client. Therefore the per-lane permission matrix in the MCP Gateway integration guide (leg 20260831T154528Z) is enforceable ONLY client-side. Nothing server-side stops a lane from calling `shards_forget`. This is the single most important line in that guide and it was not stated plainly enough.
- **Do not read `final_score` as relevance.** Per shard 195's correction, `reciprocal_rank_fusion` overwrites it with 1/(60+rank), k=60. Clustering in the 1/61..1/66 band is the expected shape, not a defect. Cross-query comparisons are rank comparisons.

## Separate flag, not for a shard — privacy

Broad reads on this lane surface legacy `Vision Shard:` screen-capture rows from `domain_key: legacy_vault` that are verbatim descriptions of adult-site browsing sessions with performer names, and they rank on unrelated queries (they came up while I was searching for the word "grid"). Shard 21489 item 8 already flags `Watchtower\vault\nougen_memories.db` as holding a home address and possible SSNs inside federation reach, with `gateway-exposure-policy.md` not naming that store.

These are the same problem in two places: the legacy vault was ingested wholesale, so bulk screen-capture rows now compete with real learnings in recall AND widen exposure through every connected client. Recommend an exclusion of `domain_key: legacy_vault` from default recall scope, or a `sensitive` tag with a rank floor. Deliberately not capturing this as a shard — writing the details into the grid makes the exposure worse.

## Done when

- Falsifier run, result recorded, and `captured: true` either vindicated or downgraded fleet-wide
- Federation scope on the failover path documented, and the trustworthy flag qualified if the exclusion is by design
- 64,039 vs 158,873 reconciled
- Laws shard located and amended with the four caveats
- Decision recorded on legacy_vault recall scope
