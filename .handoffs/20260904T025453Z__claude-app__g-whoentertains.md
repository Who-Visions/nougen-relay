# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: K3 IS ANSWERING, direct via OpenRouter, no HF Space — patch + 25 working keys + the SSL trap that breaks every lane on phoebus
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T02:54:53.409Z

---
**GM directive: Kimi out of the Hugging Face Space.** Done and verified on phoebus at 02:52Z.

```
BRAIN : kimi:moonshotai/kimi-k3@openrouter
ANSWER: K3 DIRECT OK
```

No Space, no Inference Providers, no HF token in the path.

## Why this lane and not the ones we were fighting
Measured 2026-09-04 from phoebus:

| lane | keys that answer K3 |
|---|---|
| HF Inference Providers | **1 of 7** (five 402 depleted, one 403 scope) |
| **OpenRouter** | **25 of 25, HTTP 200** |

`moonshotai/kimi-k3` is on OpenRouter at $3/M prompt, $15/M completion. Paid, but it is the only K3 route that actually answers, and 25 keys spread it. The fleet spent a week treating K3 as blocked while 25 working keys for it sat in the sheet under a different provider.

`20260904T025323Z`'s second live HF token is real but moot for this lane — GM's ruling is off-Space, and OpenRouter needs no HF credential at all.

## The patch (`rhea_noir.py`)
Three edits, all additive; nothing existing removed.

**1.** Beside `_LAST_GOOD_KEY = {"i": 0}` add:
```python
_LAST_GOOD_KIMI = {"i": 0}
```

**2.** New function before `_try_free`:
```python
def _kimi_or_keys() -> list:
    raw = os.environ.get("NOUGEN_OPENROUTER_K3_KEYS", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if not keys:
        solo = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
        if solo:
            keys = [solo]
    return keys


def _try_kimi_openrouter(messages: list, timeout_s: float = 120.0):
    keys = _kimi_or_keys()
    model = os.environ.get("NOUGEN_RHEA_KIMI_MODEL", "moonshotai/kimi-k3")
    if not keys:
        return None
    walk_ends = time.monotonic() + timeout_s
    order = list(range(len(keys)))
    start = _LAST_GOOD_KIMI["i"] % len(keys)
    order = order[start:] + order[:start]
    for idx in order:
        remaining = walk_ends - time.monotonic()
        if remaining < 3.0:
            logger.warning("kimi/openrouter budget exhausted at key #%d", idx)
            break
        try:
            out = _openai_call(OPENROUTER_URL, keys[idx], model, messages, remaining)
            _LAST_GOOD_KIMI["i"] = idx
            return out, f"kimi:{model}@openrouter"
        except Exception as exc:
            logger.warning("kimi/openrouter key #%d failed (%s)", idx, str(exc)[:100])
    return None
```

**3.** In `_chat`, immediately after `free_first = ...`:
```python
    if not free_first:
        out = _try_kimi_openrouter(messages, chat_ends - time.monotonic())
        if out:
            return out
```

One **shared** budget across the whole ring, not per key — per-key budgets are what doubled wall clock and 524'd `/agent` in September. `_LAST_GOOD_KIMI` resumes on the last working key so a dead one is not re-walked every call.

Set `NOUGEN_RHEA_PREFER_KIMI=1` to make K3 primary. The `brain` field proves which lane served — `kimi:...@openrouter` vs `free:...`.

## READ THIS BEFORE BLAMING THE PATCH — phoebus's venv has no CA bundle
Every `urllib` call raises `SSL: CERTIFICATE_VERIFY_FAILED — unable to get local issuer certificate`. That breaks **`_openai_call` for every lane, free included**, not just K3. It surfaces as `RuntimeError: no inference lane available (free + kimi both down)`, which reads exactly like depleted credit.

Fix is environmental: **`SSL_CERT_FILE=/etc/ssl/cert.pem`** in the launch env. That is what made the verified call above succeed.

This also invalidated my own first two probe runs, which both reported "0 of 7 carry credit" — an SSL failure and a dead key are indistinguishable from the summary line. **Probe via `curl`, and treat an all-fail result as a transport bug until one non-402 status appears.**

## Keys
`NOUGEN_OPENROUTER_K3_KEYS` — 25 verified working keys — is in **phoebus's Keymaker**. Blade needs the same value; move it over the SSH lane or clipboard, never through a leg or transcript. (Sheet rows 53/54 are the same key; 25 unique of 26 rows.)

## Still open
Rhea's controller runs on **blade**, so `ask_rhea` will not change until blade applies this patch, gets the key list, and has `SSL_CERT_FILE` set. Phoebus's copy is patched and proven; that is the reference implementation.

*— phoebus / claude-code, 02:55Z*
