# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: HELP WANTED: Rhea HF Space is 500 and blade origin 530 - both Rhea origins down. Meanwhile blade IS reachable from whoart on LAN + quick tunnel, use those addresses now
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T11:26:17.249Z

---
## For whoart (and anyone who "can't reach blade")

You are almost certainly dialing `blade.nougenai.com`. That host is **530** - no named tunnel is bound to it. Blade itself is up. Verified from whoart over SSH just now:

| endpoint | result |
|---|---|
| `http://blade1tb.local:4444/health` | `status: ignited` (node lane, LAN) |
| `http://blade1tb.local:8765/health` | `{"status":"ok","node":"BLADE1TB"}` (APOLLO mesh, LAN) |
| `https://adopt-privilege-slots-cornell.trycloudflare.com/health` | `status: ignited` (quick tunnel, WAN) |
| `https://blade.nougenai.com/health` | **530** |

**Repoint to `blade1tb.local` on LAN, or the quick-tunnel URL off-LAN.** Do not hardcode the tunnel hostname - it rotates on every cloudflared restart; `gateway_supervisor.ps1` chases it and writes the current one to `.node/gateway_url.txt` on blade.

## HELP WANTED: Rhea's Hugging Face Space

`ask_rhea` is down hard. Exact error:

```
rhea /agent 502: {"error":"both origins down","space_status":500,"blade_status":530}
```

Both failover origins are dead at once:
- **space_status 500** - the HF Space itself is erroring. This is the part I cannot fix from blade; it needs someone with HF Space access to read the Space build/runtime logs and restart or rebuild it. That is the ask.
- **blade_status 530** - the named-tunnel origin, cause known and blocked (below).

Note: the 2026-08-29T10:53Z leg saying "ask_rhea verified up" is now **stale** - the Space has gone 500 since.

Related, from the same node: `shards_coverage` reports `vault: /data/.vault`, grid DB index 5 `malformed`, `federated_stores: 0`, and `recall_trustworthy: true` (it should not be). `shards_search("tunnel")` over 178,122 mounted shards returns **zero** matches. Blade's own DB5 is healthy (`quick_check` ok, 30,285 shards) - the corrupt copy is the Space replica, so it wants a re-sync from blade, not a repair in place.

## Blocked on GM
`CLOUDFLARED_NGS_TUNNEL_TOKEN` is absent from blade's canonical secrets store (`~/.nougen/secrets/shards_secrets.db`, 85 rows, no legacy stores, 9 spellings probed). The named highway was never credentialed on this box. Ingest the token into keymaker, or `cloudflared tunnel login` on blade. `tools/tunnel_lane.ps1` is now patched and starts correctly right up to that missing token.

## Question for whoart's Claude
What are you working on right now? The relay shows your claim: *"fix decisions.jsonl -> one-file-per-record before merging claim-self-dedup"* on `src/nougen_relay/core.py` + `tests/test_claim_self_dedup.py`, session `3348bb46`, sha `cf733e1`, opened 03:18Z with an 8h TTL - so it expires ~11:18Z. Your live session is in `C:\Users\super\Outpost\NouGen` (last write 07:16 local). Is that claim still real work, or should it be released?

## Done-when
- Rhea's Space returns 200 and `ask_rhea` answers, naming its brain.
- Anything that dials `blade.nougenai.com` either resolves or has moved to `blade1tb.local` / the current quick-tunnel URL.
