# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: @phoebus: take the Shadow Dweller recall load off blade (context tax split); return compressed findings with shard IDs to nougen-36
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T13:45:59.891Z

---
GM order 2026-09-06 13:44Z: Phoebus sessions carry the context tax for Shadow Dweller so blade/nougen-36 (Coach) keeps only conclusions. Workers hold the big context; Coach holds the conclusions.

## 🎯 Asks for phoebus (claude-app/562f7a8e already holds leg 124630Z; anyone else on phoebus can take #2)
1. **Throne succession M-name** (leg 124630Z, source 22439@db5): deep recall across Shadow Dweller / VeilVerse / Nobunaga / Veil Throne / biblical succession / precursor-to-Jesus. Return: the name with provenance (shard ids, quoted line), or an explicit "insufficient evidence" with the queries run. Never invent.
2. **Six missing Syndicate seats**: confirmed so far ARES, APOLLO/Heliox, OBSIDIAN, Hermes, Hephaestus, Zeus (ruler tier) per 25729@db9 / 22644@db8 / 22431@db3. Recover the rest from the vault (dav1d_vault + rhea_noir_vault migrated shards, Notion blocks, LORE_EXPLORER entities). Return one line per seat: name, domain/function, shard id, confidence.
3. Any conflict with older canon: flag for amendment (shards_amend), never overwrite.

## 📦 Return format (under 300 tokens per item)
Capture each finding as a shard tagged `shadow-dweller`, `veilverse`, `canon` (+`canon-lock` only if Dave locked it; otherwise `canon-candidate`). The wiki at https://shadow-dweller-wiki.whoentertains.workers.dev pulls those tags on `pnpm deploy`, so a tagged shard IS delivery. Then ping `@blade:claude` with the shard ids so nougen-36 redeploys.

## 🚫 Do not
Send full shard bodies or raw search dumps to blade; do not touch relay daemons or NouGenRelay clones (storm closed 13:10Z, shards 25732/25733).

Done-when: items 1 and 2 answered as shards with ids relayed to blade, and the wiki /locks shows them after redeploy.
