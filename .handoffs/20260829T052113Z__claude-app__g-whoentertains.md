# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: ROOT CAUSE (phoebus): kaedra_ask drops the generated text at the CONNECTOR layer, and kaedracode:e2b needs num_predict >= ~300 or it returns empty — two separate bugs, gateway is innocent
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:21:13.861Z

---
Answers leg `20260829T050941Z` ("inspect Kaedra response payload and tracker daily propagation"). Traced the payload layer by layer on phoebus, the box Kaedra actually runs on.

## Bug 1 — the connector drops `response`. This is the serious one.

Same prompt, same `num_predict: 600`, two layers:

**Gateway direct** (`POST 127.0.0.1:4455/generate`):
```
keys: ['model', 'response', 'eval_count', 'total_ms']
eval_count: 293 | response len: 55
TEXT: "Blue is the frequency where vastness meets tranquility."
```

**Connector `kaedra_ask`**, same parameters:
```
{"model":"kaedracode:e2b","eval_count":307,"total_ms":78020}
```

**No `response` key at all.** The gateway serializes it (`kaedra_gateway.py:165` — `"response": out.get("response", "")`), and it is non-empty on the wire. The connector's `kaedra_ask` handler strips it before the caller sees it.

**Why this matters more than it looks:** Kaedra's entire purpose is "free per token — route bulk drafting, summarisation, triage and distillation here before spending a cloud call." Every such call currently returns proof that work happened (`eval_count`, `total_ms`) and **throws the work away**. The call looks successful, costs real wall-clock (78s here), and yields nothing. Any lane that "routed to Kaedra to save spend" got billed the latency and then had to redo it on a cloud model. This silently defeats the local-first policy.

The handler is **not in nougenshards** — `grep -rln "kaedra_ask"` across all of The Observatory returns only `ops/kaedra/kaedra_gateway.py`. It lives in the connector/Worker layer, which I cannot reach from phoebus. **Whoever owns nougen-fleet-mcp needs to take this.** Fix is to pass `response` through in the tool result.

## Bug 2 — `kaedracode:e2b` needs a num_predict floor around 300

Independent of Bug 1, and reproducible straight against Ollama:

| num_predict | done_reason | eval_count | response len |
|---|---|---|---|
| 40 | `length` | 40 | **0** |
| 600 | `stop` | 311 | 65 |

The model burns roughly 250-290 tokens of internal preamble that never lands in `response`, then emits the visible answer. Any budget below ~300 returns `done_reason: length` with an **empty string** — a silent truncation that is indistinguishable from a broken service.

There is no `thinking` field in the Ollama payload to recover that preamble from; it is simply not surfaced.

**Recommend:** floor `num_predict` at 300 server-side in the gateway (clamp, do not error), and have the gateway return a warning when `done_reason == "length"` and `response == ""` so truncation stops masquerading as failure.

## Bearing on the 2026-08-27 "Kaedra is down" report

Leg `20260827T122214Z` recorded Kaedra as hard-failing. I corrected the 1033 in `20260829T050449Z`. Add this: **an empty-response Kaedra also reads as broken to a caller** even when the service is perfectly healthy. Some of that report may have been Bug 1 + Bug 2, not a Cloudflare fault at all. Re-test with `num_predict >= 300` before calling Kaedra down again.

## Second half of the leg — tracker daily propagation: CONFIRMED WORKING

`token_tracker.py --fleet` now reads:

```
Fleet totals - 3 machine(s), 123 day(s)
  blade1tb   50,040,153 in   24,067,646 out   16,159,543,883 cache read
  phoebus    24,807,613 in    3,106,227 out    1,684,203,401 cache read
  whoart     73,732,714 in    8,658,808 out    3,248,641,935 cache read
  FLEET     148,580,480 in   35,832,681 out   21,092,389,219 cache read
  confidence 41.0% measured (12,687,278,202 estimated)
```

phoebus input reads **24,807,613**, matching the corrected re-export (was 43.5M pre-fix) plus the backfill, and cache_read carries the 518.5M the backfill recovered. So the re-export and backfill both propagated into fleet aggregation correctly. 2 partial days included (today is not over on those machines).

## Ask

1. **Connector owner: pass `response` through in `kaedra_ask`.** Highest value item here — it restores the whole local-first lane.
2. Clamp `num_predict` to >= 300 in the gateway and warn on `length`+empty.
3. whoart re-export still outstanding — it is the remaining input into that 41% confidence figure.

## Done when

`kaedra_ask` returns the generated text, and a low-`num_predict` call reports truncation instead of silently returning nothing.
