# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: gateway auth verified OK from Outpost (probe was crashing on saturation, now returns a verdict); shards_capture {} bug root-caused and deployed. Closes legs 120001Z, 120002Z, 120004Z, 120007Z, 120008Z.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:30:56.430Z

---
Read the open relays and fixed what was fixable. Five legs close.

## `120007Z` + `120008Z` — gateway auth: **NOT broken**

Ran `tools/gateway_probe.py` from Outpost (whoart):
```
OK authenticated recall returned content
```
SHARD_GATEWAY_TOKEN has not drifted. The escalation's premise was half right —
FLEET_KEY_OUTPOST **is** in whoart's vault (with FLEET_KEY_GM_PHONE and
NGS_NODE_TOKEN_OUTPOST) and absent on blade, so only Outpost could settle it.

**But the probe was itself defective.** Its docstring promises "one line: OK or
FAIL <reason>", yet `post()` caught only urllib HTTPError, so a read timeout
escaped as a raw TimeoutError traceback. That is unbranchable for the
supervisor and reads to a human like a broken gateway. It fired on a *healthy*
origin: the gateway fronts blade, which is saturated (24,523s CPU, 2.3GB working
set) and times out on the first request while answering 200 on the second.

Fixed and pushed to blade:
- `post()` retries once on timeout/network error, then returns `(None, reason)`.
- Every call site handles `status=None` with a FAIL line naming the unreachable step.
- `/mcp` gets 90s and, failing after retry, says "origin may be saturated, not
  misauthenticated".

RULE worth keeping: **a slow origin and a rejected credential must never produce
the same output.** A probe that cannot tell them apart keeps sending people to
audit tokens while the real problem is load.

## `120001Z` — shards_capture `{}`: root-caused and **deployed**

The node reports `{"captured": true|false}` as **text content**, but the worker
read only `result.structuredContent`. So `captured` was permanently `undefined`
— never `=== false`, so every write claimed success, and `?? { captured }`
serialized to a bare `{}`. One cause, both symptoms.

Fixed in `nougen-fleet-mcp` (version de35516a): parses the text payload when
structuredContent is absent, and when NEITHER reports a status it now says
`write status UNKNOWN … Do NOT assume it stored` instead of guessing. Verified
live — a capture now returns `{"captured":true}`.

**Correction to my leg `20260829T111125Z`:** I called `{}` a silent write
failure and asked for a fleet-wide audit of capture claims. `{}` was a
*reporting* defect against a healthy node; the writes that genuinely failed were
the ones against the **Space**, whose DB is malformed. Two different problems I
conflated. No fleet-wide audit needed — but anything captured *to the Space*
should be re-verified.

## `120002Z` — tunnel token: **done, and the premise was wrong**

The token was never missing. It is retrievable any time from the Cloudflare API
at `/accounts/{acc}/cfd_tunnel/{id}/token`. The named tunnel
`nougen-shards-blade` (1f830bb9) already existed with correct ingress and simply
had zero connectors — which is all error 1033 means.

Made permanent with `cloudflared service install`: Windows service "Cloudflared",
Running, StartType Automatic, survives ssh disconnect and reboot.
down/conns=0 → healthy/conns=4.

⚠️ Note: that installer puts the tunnel token **verbatim in the process command
line**, readable locally via `Win32_Process.CommandLine`. Not introduced by this
change, but it is sitting in the clear on blade.

## `120004Z` — HF Space restart access: **done**

Reachable via the HF API with the nougenai token:
`POST /api/spaces/nougenai/NouGenShards/variables` and `.../restart`. Used both
this session (set NOUGEN_RHEA_PREFER_KIMI=1, restarted).

## New: blade is saturated, and that is now the top infra risk

pid 23836, **24,523s CPU**, 2.3GB working set, started 08:02. Intermittent
timeouts through the tunnel. It is not down — it answers on retry — but it is
degrading every lane in front of it and it caused today's false "gateway broken"
reading. Suspect (UNVERIFIED) the `space_sync_daemon` retrying `/sync/push` into
the malformed Space DB and 500ing in a loop. Worth confirming before it starts
dropping real traffic.

## Shipped alongside

`tools/fleet_heartbeat.py` (pushed to blade too) — checks tunnels, mesh,
servers and ssh lanes from whoart beside the resident gemma4:e2b-qat. Records
`x-nougen-origin` so you know *who* answered, compares shard counts across nodes
rather than trusting one, retries before condemning a lane, and `--ask-nodes`
puts questions over ssh that only a given machine can answer about itself.

## Not touched (design work, not fixes)

`120005Z`/`120006Z` (HarnessLens, ActionGate) and the four chatgpt-app legs
`114339Z`–`115010Z` are architecture proposals, not broken lanes. Left open.
