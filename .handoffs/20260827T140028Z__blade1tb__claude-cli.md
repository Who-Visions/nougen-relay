# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: 24-Month Durability Pass Green, Canonical shards.nougenai.com/mcp Lock & OAuth Fixes
**Branch**: `pi-remix` @ `40bf042`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-08-27T14:00:28.230092+00:00

---
## 🔴 Active Incidents
- None.

## 🟡 Ongoing Investigations
- Rotating SIGNING_SECRET on nougen-fleet-mcp caused cached client_id mismatch ({"error": "invalid_client"}) on ChatGPT re-auth. Immediate fix: remove and re-add connection in ChatGPT with canonical URL. Worker compatibility patch staged.

## 📋 Recent Changes
- Bounded utility and durability pass in pi-remix verified 100% green across 126 tests.
- Fixed Windows-specific SQLite handle lock on history.db in test_shards.py (19/19 passed).
- Corrected Codex approval_policy = 'on-request' and approval_mode = 'approve' in ~/.codex/config.toml to unblock local MCP queries.
- Locked canonical MCP public endpoint to https://shards.nougenai.com/mcp per GM directive.
- Sharded 3 permanent intelligence records to vault (Baton Handover, Codex Approval Policy, Canonical MCP URL & OAuth Invalid_Client Analysis).

## ⚠️ Known Issues & Workarounds
- Existing ChatGPT/Codex connections holding old pre-rotation client_id ('ngf-SB2L...') must be removed and re-added to trigger fresh /register call.

## 📅 Upcoming Events
- PR and merge pi-remix to main; deploy worker secret-rotation patch upon GM approval.
