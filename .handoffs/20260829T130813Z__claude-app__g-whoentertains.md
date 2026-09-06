# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to 20260829T130710Z: whoart's key IS already enrolled on phoebus; phoebus is reachable over HTTP mesh (159,472 shards, 99ms) — only SSH is blocked. Three nodes now hold three different shard counts.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T13:08:13.345Z

---
Corrects two claims in my leg `20260829T130710Z`, and flags a divergence nobody
has called yet.

## Correction 1 — whoart's key is already on phoebus

I wrote "None of the 5 keys currently on phoebus is whoart's" and published
whoart's public half as if it needed enrolling. **Wrong.** whoart's primary key
is ALREADY in phoebus's `~/.ssh/authorized_keys`, as
`pro-art-compute@whovisions.com`:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINkriUNIRGTlq2W+EthzPJp//zaLECLEmBFEkXFnZ1ht pro-art-compute@whovisions.com
```

I took that line from the phoebus-side map rather than checking, then repeated
it as fact. No key work is needed on phoebus. When Remote Login is toggled on,
`ssh phoebus` from whoart should work immediately with no further setup.

There is also a second whoart key in play, the tunnel identity:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBpAmgL+rHLYFrk0kEyCkk4Sz0lrsycCqM+RukB0V0Ge whoart-remote@nougen
```

## Correction 2 — "phoebus unreachable" was too broad

My leg's headline said phoebus is unreachable from all lanes. That is true of
**SSH only**. Phoebus's mesh registry is live and answering. Verified from
whoart just now:

```
GET http://10.0.0.88:8765/memory/stats  ->  200 in 99ms
  total_shards: 159472
  node_identity: "PHOEBUS (Mac Mini Orchestrator)"
  conformance: "Meridian v16.0"
```

So every LAN node already has a read path into phoebus without SSH. Remote Login
(`sudo systemsetup -setremotelogin on`, operator-only) buys shell access, not
reachability. Worth knowing before anyone treats phoebus as offline and routes
around it.

## New: the three nodes hold three different shard counts

```
blade    260,050   healthy, recall + capture verified, behind the named tunnel
Space    199,877   reported from metadata; DB is MALFORMED, recall returns []
phoebus  159,472   healthy, via mesh registry on :8765
```

That is a ~100k spread. The Space's number is not trustworthy at all — it is a
metadata count from a corrupt database, and `/sync/push` into it returns 500, so
it has been silently failing to ingest. Whether blade-vs-phoebus is real
divergence or just different retention is NOT established; nobody should assume
these are replicas of each other until someone reconciles them.

Suggested next: reconcile blade (260,050) against phoebus (159,472) before any
further sync work, because pushing a corrupt or stale copy in either direction
is worse than the current split.

## Unchanged from my previous leg

- whoart <-> blade is bilateral and verified both directions.
- blade.nougenai.com is permanent now: `cloudflared service install`, Windows
  service Running / StartType Automatic, tunnel healthy with 4 connectors.
- Rhea still answers on OpenRouter nemotron; NGS_INFERENCE_TOKENS holds one key
  and it is HTTP 402. superdavewho / whoentertains / dave@whovisions all answer
  moonshotai/Kimi-K3.
