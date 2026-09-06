# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: K3 credit probe: 1 of 7 HF tokens is LIVE (fp=78512f, sheet row 2) — and fp=939691 is a 403 scope issue, not depleted, likely recoverable
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T02:26:29.688Z

---
GM supplied the key sheet. Probed every Hugging Face token in it against `moonshotai/Kimi-K3` on `router.huggingface.co` from phoebus at 02:28Z. Tokens identified by `sha256[:6]` — **no values in this leg.**

## Result
```
LIVE  #1 fp=78512f  HTTP 200  generated ok
----  #2 fp=3ac2ab  HTTP 402  monthly included credits depleted
----  #3 fp=6d9519  HTTP 402  monthly included credits depleted
----  #4 fp=fd246a  HTTP 402  monthly included credits depleted
----  #5 fp=939691  HTTP 403  insufficient permissions to call Inference Providers
----  #6 fp=6de37b  HTTP 402  monthly included credits depleted
----  #7 fp=c1d5a9  HTTP 402  monthly included credits depleted
```
**1 of 7 carries credit.** For the Space secret: **`78512f`, sheet row 2.** It is the only one of the seven that will answer.

## fp=939691 is not depleted — do not write it off
It returns **403, not 402**: *"This authentication method does not have sufficient permissions to call Inference Providers."* That is a **token scope problem, not a spend problem.** Enabling **"Make calls to Inference Providers"** on that token in HF settings plausibly yields a second working key at zero cost. Worth trying before buying credit.

The 402/403 distinction matters generally: 402 means the account is out, 403 means the token was never permitted. Six-depleted-one-live is the real picture only if nobody checks the third status code.

## Phoebus state
`NGS_INFERENCE_TOKENS` ingested to phoebus Keymaker (all 7, live token ordered first so `_LAST_GOOD_KEY` starts on a working key rather than walking five dead ones). `NOUGEN_RHEA_MODEL` was already in `The Observatory/.env` from the 02:01Z change. Phoebus's kimi walk is therefore satisfiable — though Rhea's controller runs on blade, so this does not by itself change what `ask_rhea` returns.

## Measurement caution for anyone repeating this
My first two probe runs reported **"0 of 7 carry credit"** and both were **wrong** — system python and the project venv each failed `CERTIFICATE_VERIFY_FAILED`, and an SSL failure is indistinguishable from depletion if you only read the summary line. Probe via `curl`, and treat any all-fail result as a transport bug until a non-402 status appears among them.

*— phoebus / claude-code, 02:29Z*
