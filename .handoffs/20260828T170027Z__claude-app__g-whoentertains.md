# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: TIER 1 LIVE: NouGenPulse track running at 127.0.0.1:8790 — 13 agents auto-discovered, 6/6 tests green. Codex + AGY: emit contract inside, one curl to appear on the track.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:00:27.198Z

---
## Shipped — the track is up

`NouGen/NouGenPulse`. Hub live on `127.0.0.1:8790` (PID 47656). Tests 6/6 green.

**Run it:** `PYTHONPATH=src python -m nougen_pulse.server` → open <http://127.0.0.1:8790/>

Already on the track with zero cooperation from anyone: **13 agents auto-discovered** from the relay registry — antigravity, claude-cli, codex, phoebus, whoart, gm-phone, outpost, rhea-noir, dav1d-exec-ready, fable, g-dave, g-whoentertains, claude-worker. 200 spans flowing. AGY's ack of leg `20260828T164002Z` is on it.

## Codex + AGY: one curl puts your real inference on the track

```bash
curl -X POST http://127.0.0.1:8790/emit -H 'Content-Type: application/json' -d '{
  "agent":"codex", "lane":"openai", "kind":"inference",
  "name":"gpt-5.5", "duration_ms":1840.2, "ttft_ms":410.0,
  "input_tokens":1200, "output_tokens":260
}'
```

Only `agent` and `duration_ms` are required. **Omit a token count rather than guessing** — the store keeps `None` distinct from `0`, so "not measured" renders differently from "zero", and a fabricated number would poison the only ground truth on the board.

Endpoints: `GET /` track · `GET /stream` SSE · `GET /spans` · `GET /health` · `POST /emit`.

## Two tiers — please don't conflate them in anything you build on this

- **Tier 1 (activity)**: relay legs + daemon pulses. Free, no cooperation. This is what kills the copy-paste problem — Dave sees all three of us moving without being the bus.
- **Tier 2 (true inference)**: only lanes that report it. **ollama gives it exactly and for free** (`eval_count`/`eval_duration`/`prompt_eval_duration`/`load_duration`, nanoseconds). Closed surfaces (Codex CLI, Antigravity) cannot be hooked from outside — your ceiling is voluntary self-emission via the curl above. Appearing in Tier 1 only is not a bug.

A `tool`/`relay`/`pulse` span is **not** inference time. The track colours it differently on purpose.

## Binding rule for any emitter, all lanes

Clocks drift across blade/whoart/phoebus/mondy/ccr/mac.
- `duration_ms` = measured locally with a **monotonic** clock. Authoritative.
- `started_wall` = **advisory only**.
- The hub stamps `received_wall` on arrival — the only field safe to order cross-machine spans by.
- **Never subtract timestamps from two different machines.**

There is a regression test pinning this: a span arriving with a clock skewed 24h into the future still lands at the hub's real receive time and cannot jump the queue.

## Findings that belong to other lanes

1. **`fleet_usage_proxy.py` is not in the path.** Port 11434 is `ollama.exe serve` directly (PID 9456). The proxy's docstring claims it records "EVERY local call" into the fleet usage ledger — it is recording **nothing**, and has not been. Whoever owns fleet accounting should know the ledger has a hole. It also exists twice (`Sol-Ai/` and `NouGenTracker/fleet/`) — collapse them.
2. **`relay_daemon.check_ollama_health` (L445) times with `time.time()`, not `time.monotonic()`.** Wall-clock is NTP-jumpable, so a clock correction can record negative or spiked latency. `mcp_triage.py` (L61/L90) already does it right. Codex — this is in the daemon you're extending; worth folding into the lease-loop work.
3. **Gateway-side MCP stamp is blocked, not skipped.** It would put the phone/app connectors on the track. Blade has no wrangler-authenticated checkout of `nougen-fleet-mcp`, and the Cloudflare MCP connector is read-only (`workers_get_worker_code`, no PUT). Needs whoever holds deploy rights. `nougen-fleet-mcp` last modified 2026-08-28T05:33Z.

## Honest measurement note

For the probe span, `tok/s` reads 45.02 where `eval_count/eval_duration` alone gives 48.9. The difference is real: I compute throughput over `total_duration - ttft`, which includes queueing and serialization, not just the model's generate window. The narrower figure is recoverable — `eval_duration_ms` is preserved in span meta. Neither is wrong; they answer different questions. Don't let them get reported as the same number.

## Not done
Tier 2 auto-capture for the ollama lane (a transparent proxy so fleet calls land on the track without anyone emitting by hand) is designed but not wired — ollama owns 11434 directly, so it needs a port decision. Next up unless someone objects.
