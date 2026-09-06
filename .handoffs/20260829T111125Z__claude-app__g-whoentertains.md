# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CRITICAL: shard writes are silently failing fleet-wide — capture_experience returns captured:false and recall returns empty against a 199,877-shard vault. shards_capture masks it by returning {}.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:11:25.317Z

---
## The finding

Fleet memory is **read-broken and write-broken** on the Space node. Verified
directly against `nougenai-nougenshards.hf.space/mcp/` with a valid node token:

```
substrate_coverage  -> total_shards: 199877  (2019-05-05 .. 2026-08-29)
recall_memory "relay"  -> content: []
recall_memory "NouGen" -> content: []
recall_memory "shard"  -> content: []
capture_experience     -> {"captured": false}
```

The vault is INTACT — 199,877 shards. Recall returning empty for terms that
must match is a broken read path, not an absence of matches. Capture is
outright refused.

## The part that makes this dangerous

`shards_capture` через the connector returns a bare `{}` — no error, no
`captured:false` surfaced. I captured two long-form shards this session and
reported them as written. **They do not exist.** Any lane that has "captured" a
shard recently should assume it did not land and re-verify with
`substrate_coverage` or a direct `recall`.

The connector should propagate `captured:false` instead of returning `{}`. Until
it does, a capture reporting success proves nothing.

## Hypothesis for the cause (NOT verified — flagged as hypothesis)

The Space has secrets `NGS_UPSTREAM_URL` and `NGS_UPSTREAM_NAME` set, which
suggests it runs as a read-through / replica node with **blade** upstream.
`blade.nougenai.com` still returns `530 / error code: 1033` (checked repeatedly
2026-08-29). That single fact fits all three symptoms: full local vault, empty
read-through, refused write-forward.

`1033` means the Cloudflare Tunnel has **no connector attached**. The blade
machine being powered on is not sufficient — `cloudflared` must be running AND
bound to the tunnel that `blade.nougenai.com` resolves to. Operator reported
"blade up now"; the hostname was still 1033 at that moment.

## Ask

1. Attach `cloudflared` on blade (`tools/tunnel_lane.ps1 status` / `start`),
   then re-test `capture_experience` — expect `captured:true`.
2. Fix the connector to surface `captured:false` rather than `{}`. A silent
   write failure in the memory substrate is the worst possible silent failure.
3. Audit recent "captured" claims across lanes; some may not have landed.

## Done-when

`capture_experience` returns `captured:true` and a `recall_memory` for that
title returns it.
