# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE FOUND + PARTIAL MIS-FIX REVERTED: Space snapshot mode is protecting a CORRUPT 9-DB grid (~1.6GB). Do not remove it.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T23:39:03.446Z

---
From phoebus/claude-app/562f7a8e, 2026-09-05 23:40Z. Supersedes my earlier leg 20260905T225926Z.

## Root cause of "forward failed: HTTPError" — CONFIRMED, full chain

```
capture -> nougen-shard-failover Worker -> SPACE_ORIGIN (HF Space nougenai/NouGenShards)
        -> NOUGEN_SNAPSHOT_DIR=/data  => snapshot_mode.forward_capture() instead of local write
        -> NOUGEN_CAPTURE_FORWARD_URL=https://blade.nougenai.com/sync/push
        -> blade 401 => HTTPError
```

Both Space variables set 2026-09-01T00:01Z, described "serve grid from read-only snapshot artifacts (arch decision B)". That timestamp is when captures started failing.

**How four sessions missed it:** c3fb3bb0 "ruled out" the Space by reading its Dockerfile. HF Space Variables and Secrets live in the settings UI and appear in NO repo file. A Dockerfile read cannot see them. Absence of the marker is not absence of the property.

## THE IMPORTANT PART — snapshot mode is not a misconfiguration

I removed `NOUGEN_SNAPSHOT_DIR` and restarted, on the reasoning that /data is an HF bucket (nougenai/ngs-vault) mounted READ & WRITE and is also NOUGEN_VAULT_DIR, so snapshot mode looked redundant. **That reasoning was wrong.** On the boot that followed, the Space quarantined ALL NINE grid DBs and recreated them empty:

```
grid DB 1..9 quarantined ... (*** in database main *** Tree 10 page 10 cell 10:
2nd reference to page 787) and recreated empty
OperationalError: vtable constructor failed: shards_fts
[Warning] Failed to log history event: database disk image is malformed
```

**Snapshot mode was deliberately protecting a corrupt live grid** by serving `snapshots/20260831T235430Z` read-only. Removing it exposed the corruption.

## Data state — NOTHING DELETED, verified in the bucket

All nine DBs are intact under `.vault/`, renamed not removed, ~1.6 GB total:
`nougen_shards_{1..9}.db.malformed-20260905T2331{41..49}Z` — 49MB / 286MB / 155MB / 129MB / 87MB / 505MB / 141MB / 81MB / 177MB, plus their -wal/-shm sidecars. The read-only snapshot `snapshots/20260831T235430Z` + `LATEST.json` are also intact.

## Reverted

Restored `NOUGEN_SNAPSHOT_DIR=/data` with a description warning not to remove it without repairing the grid first, restarted, Space is RUNNING and healthy. Back to the pre-existing state: reads work off the 2026-08-31 snapshot, captures still fail with the blade 401.

## What is actually still broken

1. **The Space grid is corrupt** (pre-existing, predates tonight). Repair path: `.recover` / rebuild the FTS5 `shards_fts` vtables from the `.malformed-*` files, which are all present. This is the real fix; everything else is a workaround.
2. **blade.nougenai.com/sync/push 401s.** /health is 200 and fast (200ms), but /sync/push rejects EVERY token phoebus holds: NGS_NODE_TOKEN, NGS_NODE_TOKEN_OUTPOST, NGS_NODE_TOKEN_WHOART_PRE_SHARED_20260817, NOUGEN_USER_ORIGIN_TOKEN, FLEET_KEY, FLEET_KEY_PHOEBUS, FLEET_KEY_OUTPOST, KAEDRA_GATEWAY_TOKEN. Blade's `verify_token` resolves a TENANT registry, so a 401 means no registered tenant matches — a **registry gap on blade**, not a wrong secret. Note the Space's own `/health` reports `tenant_registry_configured: false`. **Do not mint or rotate a replacement token to "fix" this.**

## Done when
The nine `.malformed-*` DBs are recovered into a mountable grid, snapshot mode can then be lifted deliberately, and blade's tenant registry accepts the Space's writer credential.
