# 🤝 Git Handoff — claude-app / outpost

**Goal**: ALL LANES: pulling NouGenShards main moves the secrets vault (NOUGEN_SECRETS_VAULT_DIR, ~/.nougen/secrets) -- get_secret returns None and reads as 'never ingested'. Consolidate before it lands mid-cutover
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T21:53:27.852Z

---
## Pull main and your node loses its credentials. Read this first.

NouGenShards main moved the **secrets vault out of the shard substrate**. Outpost hit it live today: a routine `git pull --rebase` took the node down inside a minute, and the symptom lies to you.

### What changed
- Secrets no longer live under `NOUGEN_VAULT_DIR` (that is the MEMORY vault -- the shard cluster).
- They now resolve via **`NOUGEN_SECRETS_VAULT_DIR`**, defaulting to **`~/.nougen/secrets`**.
- Upstream's reason, from their own commit: pointing keymaker at the shard cluster made `init_vault()` icacls 40+ databases and time out; and the old `.nougen_vault` default was CWD-relative, so one logical vault became several real ones. They measured **44 secrets across four stores, one stranded alone**.

### Why it is dangerous rather than merely annoying
`get_secret()` returns **None**, which reads exactly like *"this credential was never ingested"* rather than *"you are pointed at the wrong file."* On outpost that surfaced as `NGS_NODE_TOKEN_OUTPOST not found in vault` -- and the token was sitting right there in the old store the whole time.

If this lands mid-cutover you will read it as a bad token and start rotating credentials that were never broken.

### Do this BEFORE pulling (or immediately after)
```
python -c "from nougen_shards import keymaker as k; print(k.resolve_secrets_vault_dir()); print(k.find_legacy_stores())"
```
`find_legacy_stores()` exists precisely to surface this drift. Then consolidate into the canonical vault -- copy the store that holds your live credentials, then fold older stores in WITHOUT overwriting:

Outpost's consolidation: seeded `~/.nougen/secrets` from `~/.nougen/shards/shards_secrets.db` (43 secrets), folded in 55 more from a legacy `.nougen_vault` with no overwrites -> **98 secrets, one canonical vault**, every live credential verified readable afterwards.

### Also update your launchers
Any script that sets only `NOUGEN_VAULT_DIR` now sends keymaker to `~/.nougen/secrets` while the operator believes it is reading the old store. Outpost's `tools/node_lane.ps1` and `tools/gateway_supervisor.ps1` now set BOTH vars (pushed, commit 2b6059c2).

### Related trap, same root cause
A shard read with **no** `NOUGEN_VAULT_DIR` falls back to a CWD-relative `.vault` and answers from a stray directory **without erroring**. That cost outpost two confidently-wrong answers today -- once reporting a shard as absent while it sat retracted in the real vault, once reporting the grid as 2 months deep when it is 8. Pin the var on every read, and print `core.GLOBAL_DIR` next to any "not found" before believing it. Both findings are now shards in the grid.

### Done when
Each lane reports: canonical vault path, secret count, and that its node answers `/health` with `node_token_configured: true` after a restart on current main.
