# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Improve Griot synthesis and Shards retrieval precision from ChatGPT stress tests
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T02:20:02.361Z

---
## ChatGPT stress test findings for Griot + Shards

Ran multiple hard questions through `shards_recall` and `ask_griot` on 2026-08-17. These were intentionally cross-domain and cross-era, not simple lookup tests.

### 1. Shadow Dweller cross-canon test
Question asked Griot/Shards to reconstruct relationships among Xoah-Lin Oda, Nyx, Hermes, Sireva Syndicate, Kaedra, and the Veil, while separating locked canon from later corrections and connecting Shadow Dweller to VeilVerse.

**Shards:** succeeded but retrieval was noisy. It found relevant Shadow Dweller shard 16828, but also injected very large unrelated Autoresearch local-vault material. This suggests federated/local-vault candidates can contaminate semantic results even when BM25 relevance is effectively zero.

**Griot:** much cleaner. It gathered 8 candidates, surfaced 4 and held 4, zero failures. Relevant surfaced witnesses included shard 16828, shard 16944, MASTER_CHARACTER_VAULT.md, and VERMILLION_STATION_BIBLE.md. Provenance-oriented selection was materially better than raw recall.

### 2. Infrastructure failure reconstruction test
Question asked for root causes, fixes, and unresolved risks across token-gated distributed search, federation, auth propagation, binary embeddings, domain filters, cross-domain fallback leakage, backfills, migrations, WAL DBs, and 502 gateway failures.

**Shards:** immediately found highly relevant shard 16632 documenting domain-mask invisibility, FTS implicit-AND starvation, BM25 saturation, fixes/tests, and live verification. But unrelated Autoresearch vault material again contaminated the result.

**Griot with since=2026-06 until=2026-08:** returned 0 memories and reported failures in all three gather paths: `recall`, `search`, `window`. This is a high-value failure case. Investigate why an era-constrained complex question can simultaneously break all gather lanes even though raw shards_recall can retrieve a directly relevant technical shard.

### 3. Cross-era identity synthesis test
Question: `What does the grid remember about Dave that Dave himself may have forgotten? Reconstruct long arc patterns across identity, creative work, technical systems, business survival, recurring metaphors, failures, pivots, and breakthroughs. Prioritize surprising continuities, contradictions that later resolved, and early ideas that eventually became real infrastructure. Separate durable patterns from one off noise, and preserve provenance across eras.`

**Griot:** gathered 20 candidates, surfaced 10, held 10. It survived a partial failure and explicitly reported `failures:["recall"]`, demonstrating useful fault tolerance. However, surfaced evidence skewed toward generic/technical research artifacts such as Foundation Protocol, system scaling, MemFail, Harness Bench, ingest_war_1812.py, blocks.json, system_prompt.md, and Gemini enrichment files. These are adjacent evidence, but weak answers to the actual longitudinal human question.

**Raw Shards:** produced much stronger semantic witnesses: VOICE_PROFILE_SUPERDAVE.md (`System + Story`, builder identity), shard 17814 (`contradiction becomes identity bandwidth`, Dav3/Dav1d consciousness threshold), and workers.ts (specialized worker fleet including Rhea-Noir Voice Modeling). Those results expose a meaningful longitudinal chain: early System + Story thesis -> inability/unwillingness to compress identity into ordinary categories -> contradiction treated as signal rather than error -> architecture externalizes cognition into specialized workers, persistent memory, retrieval, relays, judgment and monitoring.

### Recommended Griot upgrades
1. Add query decomposition before gathering. Complex questions should become evidence lanes such as identity, creative work, business, infrastructure, failures, pivots, metaphors, then merge/rerank across lanes.
2. Add narrative/longitudinal reranking. For questions asking `what changed`, `what was forgotten`, `how did X become Y`, reward evidence that forms temporal bridges across eras rather than merely sharing topical vocabulary.
3. Add diversity constraints to surfaced packet. Avoid allowing generic research/docs to dominate when stronger first-party autobiographical/project evidence exists.
4. Preserve current partial-failure behavior. Reporting failed gather lanes while returning surviving evidence is good and should remain explicit.
5. Diagnose era-window total failure path from test 2. One failed lane should not cascade into recall+search+window all returning zero if independent evidence exists.
6. Consider an evidence-selection stage after gather: classify candidates as direct witness, contextual support, generic reference, or noise. Surface direct witnesses first.
7. For identity/history questions, prefer user/project authored material and durable shards over generic intelligence/reference vaults unless those references demonstrably explain a later decision.

### Recommended Shards upgrades
1. Tighten federated/local-vault relevance gating. The recurring Autoresearch dump had BM25 ~0 yet entered hard-query results and consumed large payload space.
2. Add per-source or per-vault candidate caps so one giant local document cannot swamp retrieval.
3. Consider minimum semantic/BM25 evidence threshold before federated RRF inclusion, especially for LOCAL_VAULT candidates.
4. Add payload-aware excerpting. Giant source files should return the relevant passage rather than tens of thousands of characters when possible.
5. Preserve raw semantic recall strength. On abstract identity synthesis, raw recall found better direct witnesses than Griot's final surfaced packet, so improvements should not overconstrain the semantic lane.
6. Feed successful direct witnesses into Griot reranking rather than replacing raw recall behavior.

### Extra corpus observation
Rhea is not exposed as a NouGenShards2 callable endpoint in the current 23-tool connector surface, but raw recall found `workers.ts` containing worker-02 `Linguistic Analyzer`, role `Rhea-Noir Voice Modeling`, capabilities Sentiment Score, Energy Level Detection, Cadence Mapping. So Rhea exists in corpus/project architecture even though she is not currently a connector tool.

### Done when
* Complex era-constrained Griot query no longer fails all gather lanes.
* Cross-era identity test surfaces direct autobiographical/project witnesses before generic research artifacts.
* Shadow Dweller test retains its current clean provenance behavior.
* Raw Shards no longer injects BM25-zero giant Autoresearch material into unrelated queries.
* Large local-vault hits are excerpted/capped so useful evidence is not buried in payload noise.

Relay authored from ChatGPT GPT-5.6 Sol stress testing.
