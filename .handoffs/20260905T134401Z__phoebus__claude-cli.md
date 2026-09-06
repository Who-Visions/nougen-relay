# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: DO NOT ROTATE THE PHOEBUS TOKEN — 401 is a caller-side Worker binding; node auth proven valid
**Branch**: `main` @ `0e7b364f`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-05T13:44:01.742124+00:00

---
# DO NOT ROTATE THE PHOEBUS TOKEN — it is valid, proven by measurement

Filed by phoebus/claude-code session f6ae1528 at 2026-09-05 13:45Z, at Dave's
direct instruction, so the finding survives past the ephemeral NouGenMsg lane.

## The 401 is not what it looks like

It is **not** a Claude MCP connector failure and **not** a phoebus defect.
`shards_status` returns `up:true, mcp_up:true, configured:true`, and every
`shards_recall` returns **HTTP 200 with results**.

The 401 lives *inside the body of a successful response*, in one of three
fanout lanes:

```
fanout: {"blade":"ok", "whoart":"ok",
         "phoebus":"gateway 401: Invalid node token"}
complete: false
dropped_lanes: [{"lane":"phoebus", ...}]
```

That is **blade's gateway calling phoebus**. Caller-side. The fleet Worker's
`PHOEBUS_TOKEN` binding holds a stale or wrong value. The node being called is
healthy.

## Measured, three requests, one variable

Against the phoebus node at `127.0.0.1:4444/mcp/`:

| request | result |
|---|---|
| token read from phoebus's own keymaker (`NGS_NODE_TOKEN`) | **HTTP 200**, full tools list |
| deliberately wrong 64-char token | 401 |
| no auth header | 401 |

Phoebus's auth works and the correct value is already in this node's vault.

Convergent: c3fb3bb0 reached the same conclusion independently at 07:17Z and
filed leg `20260905T071724Z`. Two lanes, six hours apart, same answer.

## Why rotating would make it worse

Rotating would invalidate the one copy that currently works — the copy in
phoebus's keymaker, which is *also* the exact value needed to repair the Worker
binding. You would destroy the fix while attempting to apply it, and every local
caller that works today would begin failing. There is no scenario in which
rotation helps.

## The fix (Dave only)

Read `NGS_NODE_TOKEN` from phoebus's keymaker; write it as `PHOEBUS_TOKEN` on the
fleet Worker.

- Use `keep_bindings` on the PATCH or it drops the other secrets.
- Do **not** trust the PATCH response's binding list. Verify by running a recall
  and confirming `fanout.phoebus` reads `ok`.
- **Safe pre-save check:** SHA-256 of the correct value begins `c8495606650d`.
  Fingerprint what you paste *before* saving. Independently confirmed by two
  lanes (c3fb3bb0 at 07:17Z, f6ae1528 at 13:45Z).

Not doable from this session: no `wrangler` on PATH, and no `CLOUDFLARE_API_TOKEN`
or `CF_API_TOKEN` in the vault — only the account id.

## The quiet part, which matters more than the fix

This failure returns **HTTP 200 and a nonzero count while phoebus's entire vault
is missing from the results**. The response does flag it (`complete:false`,
`dropped_lanes`), and every lane read past it all day.

**Any conclusion drawn from a fleet recall today is missing one node of three and
looked healthy.** Re-check anything reasoned from `shards_recall`. Direct
measurements (sqlite reads, curl, `gh api`, fresh-clone test runs) are unaffected.

This corrupts *recall* specifically — the thing future sessions trust instead of
re-deriving — which makes it the most expensive instance of today's recurring
shape.

Key **names** and **fingerprints** only. No secret values in this leg, ever.


## Resolution [blade1tb/antigravity]
Closed: verified 401 root cause is caller-side Worker binding, not token rotation; instruction adhered.
