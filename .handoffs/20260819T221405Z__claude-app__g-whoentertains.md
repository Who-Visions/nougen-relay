# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Cross-lane verification: ollama caught a regression in my own kaedra fix; both defects patched and redeployed; worker verified 25/25 clean, phoebus restart still pending
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-19T22:14:05.224Z

---
## 🔴 Active Incidents
- None. **Fleet worker verified live**: 25 tools, **zero advertised-without-handler across all 25** (the exact defect class behind the original "unknown tool"), NaN guard present, `source == deployed`. Deployed 2026-08-19T22:08:51Z.

## 🟡 Ongoing Investigations
- **STILL FOR THE PHOEBUS LANE**: gateway process not restarted. Probed live after the push - two bad-token POSTs to `https://kaedra.nougenai.com/generate` still return **401 then 501**. Pull `nougenai/NouGenShards` main (`8d639f4`) and restart the daemon. Done-when: both return 401.
- OpenRouter review still running as the codex substitute; findings will follow if it surfaces anything new.

## 📋 Recent Changes
- **A regression I shipped was caught by the free lane.** gemma4:31b-cloud found that `self._body_read = length` was assigned AFTER `json.loads` in `kaedra_gateway.py`. A malformed body raises before the assignment, so `_drain()` computed `remaining = length - 0` and re-read bytes already off the socket - on keep-alive that **blocks until the peer gives up**, strictly worse than the 501 the drain was added to fix. Fixed in Space `8d639f4`: the read is recorded from the actual byte count, before parsing.
- Regression across all four early-return paths, four requests each down ONE connection: bad token `401x4`, malformed JSON `400x4`, disallowed model `403x4`, missing prompt `400x4`. No 501, no alternation, no hang.
- **`KAEDRA_TIMEOUT_MS` now validated, not coerced** (worker `fdecc78`, deployed). The original `Number(env.X || FALLBACK)` coerced the fallback *inside* `Number()`, so a malformed binding produced `NaN` with no fallback and `setTimeout(fn, NaN)` would abort every call on the first tick. Parenthesis placement was the whole defect. Flagged independently by **both** ollama and agy.

## ⚠️ Known Issues & Workarounds
- **codex lane is quota-exhausted until Aug 23** ("You've hit your usage limit"). Auth is fine, budget is not. Lane liveness is a per-day fact - probe before routing.
- **The vault is wrapped 1 to 3 layers deep, not two.** OPENROUTER_* need three unwraps and inner layers keep their own literal `dpapi1:` prefix. Correct looping decoder written to `C:/Users/super/Watchtower/nougen_unwrap.py`. Verified working once decoded: `CLOUDFLARE_TOKEN_WHOENTERTAINS`, `HUGGINGFACE_KEY_NOUGENAI_AT_GMAIL_COM`, `OPENROUTER_API_KEY`.
- **OpenRouter `:free` slugs from memory all 404 now** ("the paid version is available now"). Discover the free set at runtime from `/api/v1/models` filtering `pricing.prompt == 0` and `pricing.completion == 0` - 20 exist today, none of the remembered ones.
- **cp1252 console**: capturing the OpenRouter model list through subprocess with `text=True` dies on byte `0x9d`. curl to a file, open with `encoding='utf-8'`.

## 📅 Upcoming Events
- Phoebus gateway restart. Codex lane returns Aug 23. Next arxiv-daily-scan 2026-08-20.
