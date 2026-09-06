# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Fix federated recall for unk_trader_vault
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T23:59:24.958Z

---
Coverage confirms `unk_trader_vault` is mounted among the federated stores, but retrieval cannot surface it. `shards_recall` and `shards_search` for Unknown Trader returned no results, while Griot queries naming Unknown Trader and `unk_trader_vault` returned zero memories. Coverage simultaneously reports a complete 9 of 9 shard grid with read-through enabled and explicitly lists `unk_trader_vault`. Treat this as a federation routing or indexing visibility defect, not evidence that the memory is absent.

Please verify store-name routing, vault indexing, aliases, metadata normalization, read-through behavior, and handling of undated vault rows. Test `Unknown Trader`, `unk trader`, `unk_trader_vault`, `NFL`, `football`, and `trading`. Prove returned records originate from `unk_trader_vault` and expose provenance through Griot.

Immediate use case: restore the authentic Unknown Trader corpus so Dave can retrieve its original football analysis framework for the 2026 NFL Week 1 board. Do not synthesize a substitute framework.

Done when a connector lane can query `Unknown Trader` and receive real `unk_trader_vault` memories with provenance, and Griot can gather them without requiring the physical vault name.
