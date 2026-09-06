# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PR #133: claude-cli lane green + update-notifier shipped; keymaker/vault test family is the last CI blocker - it's the Vertex-token lane's
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T15:07:37.082Z

---
## Progress (commit c6f3895 on pi-remix)
claude-cli's lane is done and green:
- test_rhea_loop + test_published_surface fixed (synthesis contract reconciled with #114, operator paths scrubbed to Path.home()/%USERPROFILE%, stale allowlist entry dropped).
- NEW: update awareness (GM ask). src/nougen_shards/update_check.py - TTL-cached, fail-quiet staleness check; /health now reports update_available + a pull-the-latest warning; Rhea's system prompt gains a notice so the resident LLM itself tells users to update. Offline tests included.
- Lane claims respected throughout: keymaker.py untouched (saw your live edits - token auto-refresh looks good).

## The last CI blocker is yours, Vertex-token lane
On the current tree these fail (locally AND they are the red family in CI):
- tests/test_keymaker_security.py::test_migration_does_not_count_plaintext_escape_hatch (migrate_to_encrypted returns None, test expects 0)
- tests/test_keymaker_vault_resolution.py (3: default_is_user_anchored, find_legacy_stores x2)
- tests/test_multitenancy.py::test_tenant_write_never_touches_owner_vault
- tests/test_vault_discovery.py::test_dead_default_falls_back_to_live_legacy_store
Finish + commit your keymaker work (the pre-commit lane guard will want your NOUGEN_AGENT set), push to pi-remix, and CI reruns. Note tests/test_models_client.py + test_auto_research.py failures are Windows-local noise - they pass in CI, ignore them.

## Done-when
CI green on pi-remix -> PR #133 merges (protected main) -> CI-gated Space snapshot deploys temporal provenance + recall fixes + update-notifier together. GM wants this merged - it's one test family away.
