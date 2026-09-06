# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HF Space is persistent: persistent_storage True, read_through True via blade. The hf-mount failure WAS the volume; a restart fixed it. PR #105 merged.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T21:22:35.719Z

---
Done from phoebus 2026-08-18. Verified against live `/health`, not assumed.

## The Space is persistent now

```
persistent_storage : True      (was False)
read_through       : True      (was False)
upstreams          : [{"name":"blade","url":"https://blade.nougenai.com"}]
recall_trustworthy : True
total_shards       : 198027
```

Warnings dropped from 3 to 1.

**The `hf-mount` init failure earlier today WAS the persistent volume failing to
attach.** It was never a missing feature — storage is provisioned, the mount
just failed on that boot, so `ismount("/data")` was false and the node correctly
reported itself ephemeral. A clean restart mounted it. Anyone who reads
`persistent_storage: false` on this Space should restart before concluding
storage is unprovisioned.

That also revises what I wrote in `20260818T205929Z`: the Space was not running
on ephemeral storage by design. It was a failed mount on one boot.

## PR #105 — the fix that made federation actually work

`query_cloud_shards()` resolved `X-NGS-Token` through keymaker only, and
keymaker reads exclusively from its on-disk store. With
`NOUGEN_SECRETS_VAULT_DIR=/data/nougen_secrets`, a boot where the volume does
not mount leaves that store empty — while `NGS_NODE_TOKEN` is still in the
environment, because that is what `app.py` reads to gate inbound auth.

So on exactly the boot where federation matters most, the node registered its
upstream, sent every federated read unauthenticated, took a 401, and returned an
empty list — indistinguishable from "the upstream has nothing". The silent
degradation the function's own docstring warns about, reached by a path the
docstring did not anticipate.

Now falls back to the environment. Test `test_federated_read_token_falls_back_to_env`
covers the wiped-store case and fails without the change. 587 passed.

## Mistake I made and corrected

I set `NGS_UPSTREAM_URL` as a Space **variable** without listing **secrets**
first. It already existed as a secret. HF rejects the same name in both, and the
Space went to `CONFIG_ERROR: Collision on variables and secrets names` — down
until I deleted the variable and restarted.

**Upstream federation was already configured.** Both `NGS_UPSTREAM_URL` and
`NGS_UPSTREAM_NAME` were secrets the whole time; what was missing was only the
token fallback in #105. For anyone touching Space config: **list variables AND
secrets before writing either.** They share one namespace and a collision takes
the Space down, not just the new value.

Total downtime ~3 minutes, covered by the failover worker falling through to
blade.

## Also confirmed

- `NGS_INFERENCE_TOKENS` **survives as a Space secret.** Rhea's 9-identity
  rotation config is intact — along with `NOUGEN_RHEA_MODEL=moonshotai/Kimi-K3`
  and `NOUGEN_RHEA_FALLBACK`. Only `rhea_noir.py` itself was lost. Whoever
  rewrites it does not need to redo the credential work, just the code.
- The Cortex HUD is **not exposed**. Every HUD path returns 404 on the public
  Space; it fails closed rather than mounting without auth.
- But `NGS_HUD_USER` and `NGS_HUD_PASSWORD` **do exist as secrets** while
  `/health` reports them unset. Most likely set to empty values. Harmless today
  because the HUD is not mounted, but it means that warning cannot be trusted as
  a signal either way — worth resolving so it reports the truth.

## State

| item | state |
|---|---|
| Space persistent storage | **True** |
| Space read-through -> blade | **True** |
| blade #102 | live, verified |
| PR #102 / #104 / #105 | merged to main |
| ask_rhea | still down — needs `rhea_noir.py` rewritten INTO THE REPO |
| mondy | needs GM to install keys |
| push-main on blade | still a feature branch, 39 dirty files, needs a real rebase |

No secrets in this leg — key names and results only.
