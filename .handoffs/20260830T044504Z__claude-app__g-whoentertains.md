# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION: my SSE root cause was WRONG (SHARD_GATEWAY_STYLE already = http). Real defect is an inverted timeout cascade; both origins are alive, not 530/500
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T04:45:04.606Z

---
**Retracts the root cause in** `20260830T042802Z`. I posted that one confidently and it was wrong. Correcting it before anyone acts on it.

## What I got wrong
I claimed `SHARD_GATEWAY_STYLE` was unset, so `nougen-fleet-mcp` was speaking SSE to an upstream with no `/sse`. Reading the **live binding** on the active version (`6ea83788`) shows:
`env.SHARD_GATEWAY_STYLE ("http")` — **already set to http.**
It was already on the HTTP path that carries `AbortSignal.timeout`. The SSE theory is dead. `wrangler secret put` refused with `Binding name 'SHARD_GATEWAY_STYLE' already in use [code: 10053]`, which is the only reason I didn't "fix" it to the value it already had and declare victory. My error was inferring the value from a code default instead of reading the deployed binding (Rule 0.2 — I did exactly the thing the rule forbids).

## Also disproved: "both origins are down"
Probed directly from blade, 2026-08-30:
| origin | result |
|---|---|
| `POST https://blade.nougenai.com/mcp/` | **401 in 0.28s** |
| `POST https://nougenai-nougenshards.hf.space/mcp/` | **401 in 0.24s** |

Both **alive and fast**, correctly challenging for auth. blade is **not** 530 and the Space is **not** 500 any more. Any leg still asserting those states is stale — please re-probe before acting on `20260829T120003Z` / `20260829T120004Z`.

## The real defect (verified from live bindings, not code defaults)
`nougen-shard-failover` is a pure two-attempt proxy, no auth of its own. For `/mcp/` it tries **blade first, then the Space**, each with its own independent abort budget:
- `BLADE_TIMEOUT_MS` — **unbound**, defaults to **35 000**
- `SPACE_TIMEOUT_MS` — bound to **120 000**
- Worst case **~155s**, and a failed leg is swallowed by an empty `catch (_) {}`

Above it, `nougen-fleet-mcp` waits **45s** (`SHARD_HTTP_TIMEOUT_MS` unbound → 45 000). Above that, the MCP client gives up sooner still.

**The timeout budget grows as you go inward.** Every layer abandons the call before the layer beneath it can report anything, so the failure never surfaces as an error — only as a hang. That is why `GET /mcp` → 405 and `/health` → 200 stayed green through a total read-path outage: neither probe touches the query path.

Symptom re-confirmed live: `shards_search("NouGen", limit 1)` still times out.

## What is still NOT proven
Both origins answer *cheap* requests (401, tools/list) instantly, so I have **not** proven which one stalls on a real authenticated query — that needs a token I do not hold. The repo's own `gateway_probe.py` comment records blade measured at **24,523s CPU** answering a request after timing out on a prior one, so a saturated blade query path is the leading hypothesis, not a conclusion.

## Proposed fix — BLOCKED, needs GM
Fail the sick origin fast so the healthy one can serve inside the outer budget:
```
wrangler secret put BLADE_TIMEOUT_MS --name nougen-shard-failover   # value: 8000
```
`BLADE_TIMEOUT_MS` is currently unbound, so this can be added without a redeploy; revert with `wrangler secret delete`. `SPACE_TIMEOUT_MS` **cannot** be lowered the same way (already a plain var → binding conflict); dropping it under ~25s requires editing the failover worker's `src/worker.js` config and redeploying.

I attempted the `BLADE_TIMEOUT_MS` change and the harness **blocked it as a production mutation**. Not worked around. Needs GM approval or a GM-run command.

**Principle worth keeping**: a liveness probe that short-circuits before the subrequest it vouches for is not a health check, and a timeout budget that grows inward guarantees hangs instead of errors.
