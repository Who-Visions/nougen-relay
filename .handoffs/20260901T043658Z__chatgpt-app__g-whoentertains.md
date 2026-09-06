# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Fix UNK Trader vault targeted recall blind spot
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-01T04:36:58.711Z

---
Confirmed a reproducible federation/retrieval inconsistency around the literal UNK canon.

Ground truth from ChatGPT connector:
- Correct names are literal `UNK`, `UNK AI`, `UNK Trader`, `unk_trader`, and `unk_trader_vault`. Do NOT normalize/expand UNK to `unknown` or `Unknown Trader`.
- A prior broad Griot gather surfaced `vault_unk_trader_vault` with artifact `knowledge_pass.dart`, proving the vault is visible to at least one federated retrieval path.
- Two subsequent targeted Griot gathers returned `shown: 0`, `total: 0`, `held_back: 0`, `failures: []` even when explicitly targeting `unk_trader_vault` and then the literal aliases above.

Likely failure domain: vault is mounted/federated but its records are not discoverable through targeted keyword/semantic retrieval, alias routing, metadata/index registration, or query fan-out.

Please inspect: vault registration -> index ingestion -> alias/token handling (`UNK` must remain literal) -> keyword arm -> semantic arm -> federated query fan-out -> Griot gather filtering. Verify that records from `vault_unk_trader_vault` are indexed with searchable content/metadata, not merely enumerable as artifacts.

Done when: a targeted Griot query for `UNK Trader` / `UNK AI` reliably returns relevant `vault_unk_trader_vault` memories, including `knowledge_pass.dart` when appropriate, without relying on unrelated broad-query leakage.
