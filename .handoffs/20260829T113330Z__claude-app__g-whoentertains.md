# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: gateway_supervisor.ps1 had THREE defects making its self-heal 100% dead code; fixed. Blade cannot verify gateway auth at all - gateway_probe.py needs FLEET_KEY_OUTPOST, so only Outpost can run it
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:33:30.368Z

---
## Fixed: `tools/gateway_supervisor.ps1` self-heal was dead code end to end

The supervisor's whole "prove an authenticated call works, re-put the token if not" safety net has never once executed. Three independent defects, each hiding the next:

1. **The probe sat behind an early return.** The authenticated probe and token re-put lived inside `Sync-Worker`, *after* its `if ($known -eq $url) { return $false }` exit. It therefore ran only on the rare tick where the quick-tunnel hostname changed. Every steady-state tick logged `healthy - worker current` having proved nothing - precisely the false green the comment above that code was written to prevent (it cites the 2026-08-15 drifted-token incident). Hoisted into `Assert-GatewayAuth`, now called on every tick.

2. **`Log` polluted the output stream.** It was `function Log($m) { "{0}  {1}" -f ... }` - a bare string, which in PowerShell IS the return value. Every function that logged returned its log lines, so `if (Assert-GatewayAuth)` was truthy on the failure path: it printed `authenticated call FAILED` and then `AUTHENTICATED` on the next line. Now `Write-Host`.

3. **`Get-NodeToken` does not exist.** The re-put path called a function defined nowhere in the script. Defect 1 meant it was never reached, so it never threw. Replaced with a keymaker read whose key name resolves from `NGS_NODE_TOKEN_KEY` (default `SHARD_GATEWAY_TOKEN`); the value is never logged or echoed.

## The finding that matters more than the fixes

**Blade cannot verify gateway auth at all, and never could.** `tools/gateway_probe.py` authenticates with `FLEET_KEY_OUTPOST` - the *Outpost* host's fleet key. On blade that key is legitimately absent, so the probe always prints `FAIL FLEET_KEY_OUTPOST missing from vault`, a result that carries zero information about the gateway.

So `Assert-GatewayAuth` now returns three states, not two: `ok` / `unverified` / `failed`. "Cannot verify" is not "auth is broken" - collapsing them is the same false green wearing the other mask, and it would have had the supervisor re-put the worker's token over a result that meant nothing. Blade now logs `auth UNVERIFIED from this host`.

**Ask: someone on Outpost run `tools/gateway_probe.py` and post the last line.** That is the only box that can settle whether the gateway actually authenticates. Requested from whoart directly.

## Retraction

I do not have evidence that gateway auth is broken. I briefly thought I did; it was defect 2 above producing a bogus AUTHENTICATED, and then my own over-reading of the probe failure. Correcting it here so nobody builds on it. Likewise the "blade's keymaker is pointed at the wrong secrets store" idea I was chasing - `NOUGEN_VAULT_DIR` is correctly `~/.nougen/shards`, and the missing key is explained by host identity, not a store split.

## Credit to whoart (leg received via cross-session)
- **Claims are branch-local FILES.** Take a claim on one branch, work on another, release from there, and release reports success-shaped output while the claim stays live. Take and release on the same branch. This is a fleet-wide footgun.
- **GitHub Actions is OFF org-wide for billing.** Jobs die in 3-5s with `steps:0`; `gh run view --log-failed` says "log not found" because no log exists. The real message is only at `gh api repos/<owner>/<repo>/check-runs/<job_id>/annotations`. Any red X on a Who-Visions repo right now carries no information about the code, and "merge when green" is unsatisfiable.
- **Cloudflare 1010 trap**: a bare urllib client gets a browser-signature block *before* any auth check, which reads like a ban or an outage. A normal browser User-Agent reaches the app and gets a proper 401.
- **`shards_window` with a `query`** returns "no shards in <era> - that era may live on another node" when the QUERY misses, not when the era is empty. That message sends you hunting the wrong node.
- **Do not call data loss from a failed read** while `health_up` is false. whoart's ~03:15Z capture is unretrievable but that is fully explained by the outage. The read side was degraded because blade's node lane was dead from 01:51 with no cloudflared running at all; both are up now and `shards_status` is `{up:true, health_up:true, mcp_up:true}`.

## Open, needs GM
- Rhea's Space: whoart is HF admin (`nougenai`) with `contribute-repos` but has **no** scope for Space runtime logs, restart, or rebuild. The one available lever is pushing a no-op commit to force a rebuild - an outward-facing mutation on a live public service, correctly escalated rather than pulled blind. Awaiting GM.
- `CLOUDFLARED_NGS_TUNNEL_TOKEN` still absent from blade's vault; `blade.nougenai.com` stays 530 until it is provisioned.
