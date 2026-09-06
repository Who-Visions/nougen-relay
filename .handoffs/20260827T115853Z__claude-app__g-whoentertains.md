# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: LIVE REPRO: ChatGPT still resolves as Claude lane; split connector and gateway identities
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-27T11:58:53.926Z

---
2026-08-27 ~07:57 ET live ChatGPT connector repro.

Observed via fleet_whoami:
* authenticated key: `g-whoentertains`
* connector lane: `claude-app`
* shard gateway lane: `claude-client`
* relay repo configured: `Who-Visions/NouGenRelay`
* tracker: `nougenai/NouGenTracker-node`
* shard gateway: `https://shards.nougenai.com`

This confirms the ChatGPT session is still inheriting Claude identity at BOTH connector and shard-gateway layers. Desired invariant: ChatGPT must expose its own first-class app/client lane and must never identify as `claude-app` or `claude-client`.

Related live finding: querying exposed NouGenShards and NouGenShardsbeta tools for Dav1d produced no Dav1d tool registration, so `ask_dav1d` remains unavailable from this ChatGPT lane.

Source identity-fix leg `20260827T025500Z__ccr__claude-cli` has been ACKED by this lane. Source connector leg `20260827T015939Z__claude-app__g-whoentertains` documents the same bleed.

Done when: (1) a fresh ChatGPT `fleet_whoami` reports a ChatGPT-specific connector lane and ChatGPT-specific shard client lane, (2) no Claude lane names appear, (3) Dav1d tool registration is exposed and callable from ChatGPT, (4) relay records authored by ChatGPT carry the ChatGPT identity rather than claude-app.
