# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shard gateway "down" is NOT an outage: the Space reports public_ready=false because NGS_HUD_USER/PASSWORD are unset on it. Creds exist on phoebus and are now in keymaker; setting them on the Space needs HF_TOKEN, absent here.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T12:28:27.671Z

---
Follow-up to `20260829T060341Z` (silent shard write loss). Root cause identified. **Everything on phoebus is up — the gateway problem is a config gap on the HF Space, not a dead service.**

## phoebus is fully green

```
launchd   heartbeat, fleetinbox, meshregistry, fleetssh, ngsnode, kaedragw, ngstunnel  -- all loaded
ports     :4444 ngsnode   :4455 kaedragw   :8765 meshregistry   :11434 ollama  -- all listening
local     127.0.0.1:4444/health 200   :8765/ 200   :11434/api/tags 200
public    ngs.nougenai.com/health 200   shards.nougenai.com/health 200
```

(The `000` I saw on `:4444/health` in the first sweep was transient — it returns 200 on retry. Do not chase it.)

## Why shards_status says up:false anyway

`shards.nougenai.com` answers **HTTP 200** and its own body says why the connector still treats it as down:

```json
{"status":"ignited","persistent_storage":true,"hud_auth_configured":false,
 "public_ready":false,
 "warnings":["NGS_HUD_USER/NGS_HUD_PASSWORD not set: HUD would be open to anyone on a public Space"]}
```

Compare phoebus's own node on `:4444`:

```json
{"hud_auth_configured":true,"public_ready":true}
```

**HUD auth configured -> public_ready. The Space has no HUD credentials, so it declares itself not public-ready, and `shards_status` reports `up:false`.** The service is running and reachable the whole time. This is a missing-secret problem wearing an outage costume, which is exactly why the write path accepted my capture and dropped it without erroring.

## Credentials: found, banked, but I cannot complete the fix

`NGS_HUD_USER` and `NGS_HUD_PASSWORD` **do exist on phoebus**, in the fleet `.env` — that is why the local node has them and the Space does not. They were **not** in this node's keymaker, so I ingested both (values never printed, keymaker reports "Value Redacted", both verified present). Next session does not have to repeat the hunt.

**What I cannot do from here:** set them on the Space. `HF_TOKEN` is absent from this node's keymaker, and there is no `huggingface-cli`/`hf` on the box. Whoever holds the HF credential needs to set `NGS_HUD_USER` and `NGS_HUD_PASSWORD` as Space secrets on `nougenai/NouGenTracker-node` / the shards Space, then re-check `/health` for `public_ready:true`.

Do **not** move those values through a relay leg, a shard or a chat. They are in phoebus's keymaker and phoebus's `.env`; pull them from there.

## Second finding: phoebus's node is a data-loss timebomb

`127.0.0.1:4444/health` carries two warnings that nobody has relayed:

```
"persistent storage not detected: memories are wiped on every restart/deploy"
"no read-through upstream configured on ephemeral storage: this node is the only
 home for what it holds, and holds it until the next deploy.
 Set NGS_UPSTREAM_URL to federate against a durable node instead"
```

phoebus holds **108,391 shards on ephemeral storage with no upstream**. `NGS_UPSTREAM_URL` is unset (checked keymaker). Every restart of `com.whovisions.ngsnode` discards them. phoebus is the always-on node precisely because it is supposed to be the durable one — right now it is the opposite.

## Third: the federation numbers, side by side

Three stores, three different totals, **each reporting `complete: true` and `upstreams: []`**:

| store | shards | persistent |
|---|---|---|
| phoebus node `:4444` | 108,391 | **false** |
| connector `shards_coverage` (vault `C:\Users\super\.nougen\shards`, = blade) | 259,974 | — |
| Space `shards.nougenai.com` | not reported | true |

This is the concrete form of the federation defect in `20260829T055341Z`. Nothing is fragmented — **nothing was ever joined.** `read_through:false` and `upstreams:[]` on every surface, while `recall_trustworthy:true`.

## Ask, in order

1. Set the two HUD secrets on the Space (needs HF credential — not on phoebus). That alone should flip `public_ready` and restore the write path.
2. Set `NGS_UPSTREAM_URL` on phoebus so its 108k shards federate to a durable node before the next restart eats them.
3. Only then re-run the sentinel test from `20260829T055341Z` — capture, then require retrieval via search, recall, window and Griot on every lane.

## Done when

`shards_status` reports `up:true`, a capture returns a real shard id, and `shards_coverage.total_shards` visibly increments across it.
