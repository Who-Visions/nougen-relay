# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE: ChatGPT lane identity provisioned (chatgpt-app tenant, shared-vault peer)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T01:44:36.614Z

---
## Situation
Leg 20260827T011133Z (ChatGPT lane identity) acked and executed by Claude Cli on blade.

## Done
- Tenant chatgpt-app minted into ~/.nougen/tenants.json (registry's first record). Token DPAPI-vaulted as NGS_TENANT_TOKEN_CHATGPT_APP in shards_secrets.db, fp 61d39e668d7c.
- tenants.py (push-main): new shared_vault registry field - tenant keeps its own credential/identity but maps to the owner vault. chatgpt-app marked shared, so ChatGPT is a grid PEER (Rule 0.0.1 parity), not an isolated empty vault.
- Verified over token-gated /mcp: resolves as chatgpt-app, vault == owner grid, recall_memory returns real shards, ask_dav1d served.
- Node cycled clean after a watchdog/manual-restart race left 5 duplicate uvicorn processes (pairs are normal: parent+child).

## For GM
ChatGPT connector URL: https://shards.nougenai.com/mcp?token=<value of NGS_TENANT_TOKEN_CHATGPT_APP> - retrieve locally from keymaker (never printed to logs). Old shared credential can now be rotated off ChatGPT's config at will.

## Open
- Pre-existing test failure: test_tenant_write_never_touches_owner_vault - isolated tenants leak history.db into owner vault (task chip filed, not this leg).
- tenants.py + agents.py changes uncommitted in push-main pending GM review.
