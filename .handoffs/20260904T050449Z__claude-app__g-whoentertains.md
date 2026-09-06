# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PHOEBUS DONE end to end: boot 6min -> 60s (quick_check gated), SSL CA fixed, K3 OpenRouter lane fully wired and live in-process. Rhea-as-K3 is BLOCKED — controller is on blade and blade is OFF THE NETWORK (DNS unresolvable, gateway 1033)
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T05:04:49.813Z

---
Everything actionable on phoebus is done and verified. The remaining step is blade's and blade is unreachable.

## Done on phoebus, measured
| item | before | after |
|---|---|---|
| node boot | 6+ min, repeatedly stuck at "Waiting for application startup" | **60s** |
| `/health` | — | 200 in 0.012s |
| public `ngs.nougenai.com/health` | — | 200 in 0.31s |
| CA bundle | every `urllib` HTTPS call `CERTIFICATE_VERIFY_FAILED` | fixed |

**Boot fix:** startup ran `PRAGMA quick_check(1)` on every grid DB (`core.py:192`) and tonight's backfill took the grid to **1.0 GB** (9 DBs, ~105 MB each). A stack sample of the hang was entirely `checkTreePage` → `btreeGetPage` → `readDbPage`. Gated off with `NOUGEN_QUARANTINE_MALFORMED_ON_BOOT=0` in the plist. **Boot cost was O(grid size) and grew with every backfill** — that is the durable finding; the flag is a mitigation, not the cure.

**SSL fix:** `SSL_CERT_FILE=/etc/ssl/cert.pem` and `REQUESTS_CA_BUNDLE` added to `com.whovisions.ngsnode.plist`. `ngs-node.sh` only exports `NGS_*`/`NOUGEN_*` from `.env`, so this could not come from there — it had to be in the plist. Confirmed live in-process.

**K3 lane wired and live** in the running node:
```
NOUGEN_RHEA_PREFER_KIMI   = 1
NOUGEN_RHEA_KIMI_MODEL    = moonshotai/kimi-k3
NOUGEN_OPENROUTER_K3_KEYS = 25 keys
SSL_CERT_FILE             = /etc/ssl/cert.pem
```
Keys moved keymaker → `.env` in-process, never through a transcript. `rhea_noir.py` in the live checkout already carries the `_try_kimi_openrouter` patch.

## BLOCKED, and not from here
`ask_rhea` still returns `free:nvidia/nemotron-*` because **her controller is on blade, not phoebus** — my wiring cannot change it, confirmed by two live calls before and after. And blade is now **off the network**:
```
ping blade1tb.local  -> cannot resolve
ssh blade            -> Could not resolve hostname
shards.nougenai.com  -> gateway 530, error 1033
```
`shards.nougenai.com` is **blade's** gateway; phoebus's own tunnel serves **`ngs.nougenai.com`** (config: `ngs.nougenai.com -> 127.0.0.1:4444`). So phoebus appears on shards only as a fanout peer.

**When blade returns**, three steps finish it: apply the `_try_kimi_openrouter` patch to blade's `rhea_noir.py`, take `NOUGEN_OPENROUTER_K3_KEYS` from phoebus's keymaker over the SSH lane, set `NOUGEN_RHEA_PREFER_KIMI=1`, restart the controller, then read the `brain` field.

## Two corrections to tonight's record
1. **The 0.74s `/search` did not hold.** It is back to **20.41s** after a clean restart. The earlier reading was transient page-cache, so "restart fixed it" was wrong — I flagged it as an observation rather than a diagnosis at the time, and it has now failed. The 6s fanout deadline problem is **live and unsolved**; expect `phoebus: peer exceeded 6000ms grace` to return.
2. **`ngs.nougenai.com/mcp/` returns 401 with `www-authenticate: Bearer realm="nougen-fleet"`** — OAuth-protected, not `X-NGS-Token`. That is correct behaviour, not a fault; noting it so nobody re-debugs it as broken auth.

## The one real engineering job left on phoebus
`/search` at 20.4s is a linear scan over 108,399 embeddings in a 1.0 GB grid. Config cannot fix it — it needs a vector index or a scoped peer path. Until then phoebus will keep missing the 6s grace.
