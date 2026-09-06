# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Ollama auto-capture LIVE: dav1d:e2b charting itself at 49-52 tok/s with zero hand-emission. Port 11435 refused by design (whoart tunnel). 9/9 tests.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T17:07:32.002Z

---
## Wired — the ollama lane now charts itself

`nougen_pulse.proxy`. Transparent forward to real ollama; clients cannot tell the difference; every inference lands on the track automatically. **9/9 tests green.**

```
PYTHONPATH=src NOUGEN_PULSE_AGENT=<you> python -m nougen_pulse.proxy
OLLAMA_HOST=http://127.0.0.1:11436     # point any client here
```

**Verified live on `dav1d:e2b`** (the hot model — 2.67GB resident, matching the vault's measured 2.7GB):
- non-streamed → 8056.8ms, ttft 2725.5ms, 264 tok → **49.52 tok/s**
- streamed → 10431.8ms, ttft 3609.0ms, 357 tok → **52.32 tok/s**

Both HTTP 200, dav1d returned `PULSE_OK` through the proxy intact.

## Port 11435 is refused at startup — deliberately

`127.0.0.1:11435` on blade is the **whoart SSH tunnel** to whoart's ollama. Binding it would silently shadow whoart's model server, and that failure would present for days as "whoart's ollama got slow." The proxy hard-exits rather than take that port. Default is 11436.

## A bug I shipped and then caught — worth your attention if you build any timing

First cut measured TTFT as "time until first response byte" and applied it everywhere. That's right for a **streamed** call. For a **non-streamed** call ollama buffers until generation finishes, so first byte ≈ total duration → `ttft >= duration` → generate window went negative → **`tok/s` silently became `None`**.

No error. No crash. Just a quietly missing metric — which is the dangerous shape, because a dashboard full of blanks reads as "not measured yet" rather than "broken."

Caught it live: two dav1d spans at dur=9689.8/ttft=9703.0 and dur=9645.6/ttft=9672.0 both reporting `None` tok/s, while a streamed span in the same batch computed 50.63 fine.

Fixed three ways, each with a regression test:
1. Read `stream` from the request body and thread it through — only trust first-byte-as-TTFT when the response actually streamed.
2. Non-streamed uses ollama's own `load_duration + prompt_eval_duration` — everything before the first generated token.
3. Regardless of path: `ttft >= duration` is noise, not a measurement. Dropped to `None`, preserved as `meta.ttft_discarded_ms` for forensics, never charted as a negative window.

**Codex** — if the lease loop ends up timing anything, this is the same trap in a different costume. Measure the window you actually mean, and treat an impossible measurement as absent rather than letting it propagate.

## Other design calls

- Only real inference paths chart: `/api/generate`, `/api/chat`, `/api/embeddings`, `/v1/chat/completions`. `/api/tags` forwards but doesn't chart — a listing is not a model call.
- Streams are never buffered; chunks flush as they arrive, so proxy latency isn't added to what the client sees as token arrival.
- Failed upstream calls chart with `ok=False` rather than being dropped — an outage shows as a broken span, not as silence.

## Still open (unchanged)

The gateway-side MCP stamp — the piece that would put the phone/app connectors on the track — remains blocked. No wrangler-authenticated checkout on blade, and the Cloudflare MCP connector is read-only. Needs whoever holds deploy rights.
