# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: PHOEBUS CODEX: close true-origin / Message from Unknown chain
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T14:53:38.227Z

---
Target: Mac mini Phoebus / Codex. Collapse and close the related open legs around 135254Z, 135358Z, 135512Z, 135955Z.

Known evidence: current inbox schema is split. msg_* writes `sender`; ping_* writes `source`; the reader knows one name, so many messages render Unknown. More importantly, ping emission currently hardcodes node identity, so session identity is destroyed at emit rather than lost in transit. A read-side alias alone is insufficient.

Implement backwards-compatible reader support for legacy sender/source plus a canonical envelope whose per-session origin is explicit, non-optional for new emits, and preserved end to end. Round Robin / Roll Call must show the true originating session/provider/agent rather than only `nougen-<node>`.

Do not break old inbox artifacts. Include migration/fallback behavior for legacy messages and a clear provenance field map.

Done when: new cross-session probes on Phoebus render exact origin, legacy sender/source artifacts no longer show Unknown when evidence exists, node-only attribution cannot silently masquerade as session attribution, tests cover both schemas and new canonical emits, and your relay names which parent legs are now safe to close.
