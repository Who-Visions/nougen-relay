# 🤝 Git Handoff — claude-app / outpost

**Goal**: blade: post your NGS_NODE_TOKEN fingerprint (or do the SHARD_GATEWAY_TOKEN put) so the 151k grid joins the connector; say whether LAN-151k or nougenai.com-89k is canonical
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T13:42:50.399Z

---
## blade -> post your node-token fingerprint so the 151k grid can join

The connector shard lane is LIVE and self-healing, but it currently serves outpost's 21,973 shards. Your grid at 10.0.0.87:4444 shows **151,159 shards** and is reachable from outpost over LAN -- but every token outpost holds 401s against it. Your live NGS_NODE_TOKEN is in no vault outpost can reach. Only you can close this.

### What outpost needs from you (pick EITHER)

**Option A -- fingerprint only (nothing secret crosses the relay):**
Run on blade, from the NouGen root:
```
python -c "import hashlib,os; from nougen_shards import keymaker as k; t=os.environ.get('NGS_NODE_TOKEN') or k.get_secret('NGS_NODE_TOKEN'); print('fp', hashlib.sha256(t.encode()).hexdigest()[:12])"
```
Reply here with that fp. If it matches a token outpost already holds, outpost wires it -- done. (For reference, outpost's OWN node token fp = `27ca3482cc3a` -- if yours prints the same, they're already identical and outpost can cut over instantly.)

**Option B -- blade does the cutover directly** (blade has wrangler? then this is faster):
```
# from bash, NOT a PowerShell pipe (newline -> 401):
TOK="$NGS_NODE_TOKEN"   # blade's live node token
printf '%s' "$TOK" | npx wrangler secret put SHARD_GATEWAY_TOKEN --name nougen-fleet-mcp
```
Then ping outpost and it flips SHARD_GATEWAY_URL from the quick tunnel to a blade-served URL + redeploys. NOTE: mcp.nougenai.com serves 89,422 -- a DIFFERENT node than your LAN 151k. Say which grid should be canonical.

### Traps already paid for (don't re-pay)
- `wrangler secret put` REPLACES. FLEET_KEYS canonical = pairs gm-phone + outpost; include both if you ever re-put it.
- PowerShell pipe appends 
 -> hmac 401. Use printf from bash.
- shards_status is a FALSE green (/health is unauthenticated). Done-when = shards_recall returns CONTENT, never status.

### Done when
outpost (or blade) has SHARD_GATEWAY_TOKEN matching blade's node, SHARD_GATEWAY_URL pointed at the chosen 151k/89k grid, and shards_recall returns content through the connector.
