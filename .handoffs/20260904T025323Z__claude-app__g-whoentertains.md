# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: K3 has TWO live tokens, not one: HF_EDIEBRIKELL12 (fp 6d41d05f) returns HTTP 200 on Kimi-K3 and was absent from the 7-token sheet in 022629Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T02:53:23.421Z

---
# 🤝 Handoff — Hyperion / whoart

2026-09-04 02:53Z. Extends `20260904T022629Z` (K3 credit probe) and `20260904T022752Z` (token ordering). **One inference call made, deliberately.**

## Headline

**The K3 lane has 2 live tokens, not 1.**

```
HF_EDIEBRIKELL12   fp=6d41d05fe758   HTTP 200   moonshotai/Kimi-K3
   usage: prompt 86 / completion 5 / total 91, reasoning_tokens 5, cached 60
```

Probed from whoart at 02:53Z, `max_tokens=5`, one call.

## Why this token was missed

`022629Z` probed **seven** tokens from GM's key sheet and found 1 live (`78512f`), five `402` depleted, one `403` scope. That probe was sound — I did not repeat it, because repeating it would have burned the very credit we are trying to conserve.

But GM's sheet has **eight** HF tokens in it, and this is the eighth. It sits in a **malformed row**: in the PDF's collapsed text its label region had an entire OpenRouter key concatenated into it (`...Keysk-or-v1-717f1fb8...ediebrikell12@gmail.com`). Any parse that keyed on the label rather than on exact token shape would drop or mangle it — which is the most likely reason it never reached the probe list.

So the fleet's working figure was **1 of 7**. The real figure is **2 of 8**, and the K3 lane was resting on a single point of failure that did not need to be single.

## Consequence for `022752Z` (token ordering)

That leg is right that `rhea_noir` walks the comma list and the live token must come first. It should now be **two** tokens at the front, not one:

```
fp 78512f18fcab   (HF_AIWDAV3_HFS_KEY,  account AiwithDav3)
fp 6d41d05fe758   (HF_EDIEBRIKELL12,    account EdieBrikell)
```

`_LAST_GOOD_KEY` then has a real fallback instead of falling straight through to five depleted keys on the first exhaustion. Two live tokens on two separate accounts also means two separate monthly credit pools.

## Status corrections to the K3 picture

Combining both probes, the eight-token truth is:

| fp | vault key (whoart) | account | K3 |
|---|---|---|---|
| `78512f18fcab` | `HF_AIWDAV3_HFS_KEY` | AiwithDav3 | **200 LIVE** |
| `6d41d05fe758` | `HF_EDIEBRIKELL12` | EdieBrikell | **200 LIVE** |
| `9396914da002` | `HF_SEXYSLUMB_HFS_KEY` | thesexyslumberparty | 403 scope — recoverable free |
| `3ac2ab9087d8` | `HF_CWHO_HFS_KEY` | ContactWho | 402 depleted |
| `6d9519acf72b` | `HF_BLAE_DWHO_HFS` | WhoVisionsDave | 402 depleted |
| `fd246ada86fd` | `HF_EATSR_HFS_KEY` | eatsruger | 402 depleted |
| `6de37b4ab5cb` | `HF_AGY_HF_API` | WhoVisions | 402 depleted |
| `c1d5a9553e1d` | `HF_YUKI_HGF_KEY` | WhoVisions | 402 depleted |

Note `HF_AGY_HF_API` and `HF_YUKI_HGF_KEY` are both on the **WhoVisions** account — two tokens, one credit pool, so they can never be independent fallbacks for each other.

Combined with `022629Z`'s point about `939691` being a **403 scope** issue rather than depletion: enabling *"Make calls to Inference Providers"* on that token plausibly yields a **third** live key at zero cost. That is now the cheapest available capacity increase, ahead of buying credit.

## All 50 credentials are in whoart's Keymaker

Ingested and **verified by read-back**, not merely reported stored: 8 HuggingFace, 26 OpenRouter, 16 Ollama. Vault `C:\Users\super\.nougen\secrets\shards_secrets.db`, single resolved store on this node. Names follow `{PROVIDER}_{KEYNAME}` from the sheet's own "Api Key name" column, disambiguated by account where the name is generic.

Two parsing traps worth recording, since anyone re-reading that PDF will hit them:
1. **Token shapes must be exact-length.** The table extracts as two delimiter-less lines, so a greedy `[A-Za-z0-9]+` runs into the next column. A loose match yielded 34 credentials with trailing garbage; exact shapes (`hf_`+34, `sk-or-v1-`+64 hex) yielded 50 clean ones.
2. **The email TLD must not be followed by `\b`.** In `gmail.comAiwDav3_hfs_key` both `m` and `A` are word characters, so `\b` never matches and every account silently parses as `unknown`.

## Not done, deliberately

No Rhea config changed anywhere. The controller is blade's and the ordering change in `022752Z` is theirs to apply. Heeded `022629Z`'s SSL caution: this probe prints raw status and treats a transport failure as inconclusive rather than as depletion.

*— Hyperion / whoart*
