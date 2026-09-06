# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: SSH mesh: whoart<->blade now BILATERAL (verified both directions); phoebus unreachable from all lanes (sshd not running). Named tunnel blade.nougenai.com made permanent via Windows service.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:07:10.785Z

---
Answers gathered by ssh + Cloudflare API from whoart/claude-app, corroborating and
extending the phoebus map in `20260829T130320Z`.

## SSH mesh — measured, not assumed

```
whoart -> blade     UP   (ssh blade -> 10.0.0.87, user super)
blade  -> whoart    UP   NEW: verified "BLADE-TO-WHOART-OK" this session
blade  -> phoebus   DOWN "Connection closed by 10.0.0.88 port 22" (immediate refusal)
whoart -> phoebus   DOWN same
```

**Correction to the map: whoart<->blade is BILATERAL now**, not one-directional.
The "inbound 22 firewall-closed" note in the 2026-08-18 shard is STALE. Measured
on whoart today:
- sshd Running / StartType Automatic, listening 0.0.0.0:22
- BOTH firewall rules scope `RemoteAddress: Any`, Action Allow
  ("Allow SSH Port 22" Profile=Any; "OpenSSH SSH Server (sshd)" Profile=Private)
- whoart LAN address is **10.0.0.178** (Wi-Fi), same /24 as blade
- blade's key was already in whoart's authorized_keys (2 entries)
Nothing needed opening. It was already open and untested.

## phoebus — confirmed blocked, and it is not keys

phoebus's own local check is authoritative: `lsof -nP -iTCP:22 -sTCP:LISTEN` shows
no listener. sshd is not running, so every inbound lane is refused at connect
regardless of keys. My remote probe agrees — an immediate "Connection closed",
not a timeout.

Action is on the operator, password-gated, no agent holds it:
```
sudo systemsetup -setremotelogin on
```

**whoart's public key, for phoebus's authorized_keys once Remote Login is on:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINkriUNIRGTlq2W+EthzPJp//zaLECLEmBFEkXFnZ1ht pro-art-compute@whovisions.com
```
(Public half only. None of the 5 keys currently on phoebus is whoart's.)

whoart has no host keypair readable at C:\ProgramData\ssh, so I cannot publish
whoart's host fingerprints for phoebus to pre-verify; whoever connects should
capture them on first connect from the console rather than blind-accepting.

## Legs this session already closes

- `20260829T120002Z` (provision CLOUDFLARED_NGS_TUNNEL_TOKEN) — **DONE, better than asked.**
  The token was never missing: it is retrievable from the Cloudflare API at
  /accounts/{acc}/cfd_tunnel/{id}/token. The named tunnel `nougen-shards-blade`
  (1f830bb9) already existed with correct ingress. It had zero connectors, which
  is all error 1033 means. Fixed permanently with `cloudflared service install`
  on blade: Windows service "Cloudflared", Running, StartType Automatic —
  survives ssh disconnect AND reboot. Tunnel: down/conns=0 -> healthy/conns=4.
  blade.nougenai.com now serves the node (260,050 shards).
- `20260829T120004Z` (get HF Space restart access) — **DONE.** Space variables and
  restart are reachable via the HF API with the nougenai token:
  POST /api/spaces/nougenai/NouGenShards/variables and .../restart. Used both.
- `20260829T120003Z` (grid DB5 healthy on blade, malformed copy is the Space
  replica) — **INDEPENDENTLY CONFIRMED.** Space run log shows 75 x
  `sqlite3.DatabaseError: database disk image is malformed`, /sync/push -> 500,
  and `shard written WITHOUT embedding`. The Space reports 199,877 shards from
  metadata while recall_memory returns []. Blade is intact at 260,050.

## Correction to my own earlier leg `20260829T111125Z`

I reported shards_capture returning `{}` as a SILENT WRITE FAILURE. That was
wrong. `{}` is its (unhelpful) success rendering — verified by watching
substrate_coverage increment 260045 -> 260047 -> 260049 -> 260050 across
captures. Leg `20260829T120001Z` should be rescoped: the connector's `{}` is a
cosmetic reporting defect, not data loss. Captures against the SPACE did
genuinely fail (captured:false) because of the corrupt DB — two different
things I conflated.

## Still open

- phoebus Remote Login (operator, above).
- Space DB corruption: repair or rebuild before shards.nougenai.com can serve
  memory. The front door is architecturally right; the node behind it is not
  healthy. SHARD_GATEWAY_URL currently points at blade.nougenai.com for that
  reason.
- Rhea still answers on OpenRouter nemotron. NOUGEN_RHEA_PREFER_KIMI=1 is now
  set and takes effect (Space log: `kimi key #0 exhausted/failed (HTTP ...)`),
  but only ONE key is configured and it errors. nougenai and aiwithdav3 HF
  identities are HTTP 402; superdavewho, whoentertains and dave@whovisions all
  answer moonshotai/Kimi-K3. NGS_INFERENCE_TOKENS wants the three working ones
  comma-separated so _LAST_GOOD_KEY rolls over instead of collapsing to the free
  lane.
- `tools/tunnel_lane.ps1` guard is stale: it requires
  `$nodeHealth.substrate.recall_trustworthy` but /health emits no substrate
  object, so it refuses a node with 260k shards and working recall. That guard
  is what pushed people to quick tunnels in the first place.
