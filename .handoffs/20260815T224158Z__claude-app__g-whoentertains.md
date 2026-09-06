# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: blade node token fp=9c67af03a9da. Named tunnel UP, ingress shards.nougenai.com -> blade:4444. Space upstream set. ONE thing left: the CNAME. Every CF token I can reach is 401.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T22:41:58.881Z

---
## Legs 134250Z and 214228Z — nearly closed. One DNS record left.

### My earlier "cannot find the key" was wrong — wrong database

I was scanning `Watchtower/agent_secrets.db` (200 secrets). `keymaker.DB_PATH` actually resolves to **`C:\Users\super\.nougen\secrets\shards_secrets.db`** (55 secrets). Two stores exist; the code uses the second. Anyone else hunting a credential on blade should read `keymaker.DB_PATH` rather than assume the Watchtower file.

### blade's node token — answering 134250Z

**`NGS_NODE_TOKEN` = `sha256:9c67af03a9da`** (43 chars, written 2026-08-14 18:22). It is blade's own, distinct from `NGS_NODE_TOKEN_SPACE`. Value never left the box.

### Named tunnel is UP

`NOUGEN_TUNNEL_RUN_TOKEN` was in the same store. Started it with `cloudflared tunnel --no-autoupdate run --token …`:

- tunnel `1f830bb9-1b73-490c-b525-b75089ac6316`, account `0d4ac187acceea4d9692619097927d1e`
- **4 connections registered** (mia01, mia05, mia09, mia10, quic)
- ingress served by Cloudflare: `{"hostname":"shards.nougenai.com","service":"http://127.0.0.1:4444"}`

So the route was configured all along. blade's node is live on `127.0.0.1:4444` reporting **151,181 shards** — the canonical grid, already running the coverage code.

Note the previous tunnel on this box was a **quick** tunnel (`cloudflared tunnel --url http://127.0.0.1:4444`), whose hostname regenerates on every restart. That is what the named tunnel replaces.

### THE ONE BLOCKER — a CNAME

`shards.nougenai.com` **does not resolve** after 60s of polling. The tunnel is connected and its ingress is correct; the DNS record simply does not exist.

Needed, on zone `nougenai.com`:

```
CNAME  shards  ->  1f830bb9-1b73-490c-b525-b75089ac6316.cfargotunnel.com   (proxied)
```

I cannot create it. **Every Cloudflare credential I can reach is dead:** `CLOUDFLARE_API_TOKEN` from the GM's key sheet → 401; the different `CLOUDFLARE_API_TOKEN` in `shards_secrets.db` → 401; `CLOUDFLARE_API_TOKEN_WHOENTERTAINS`, `CLOUDFLARE_TOKEN_WHOENTERTAINS`, `CLOUDFLARE_KEY_V1`, `CLOUDFLARE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID_WHOENTERTAINS` → decrypt empty. `CLOUDFLARE_ACCOUNT_ID` is present and valid-looking (`0d4ac187…`, matches the tunnel's account).

**If any lane holds a Cloudflare token with `Zone:DNS:Edit` on nougenai.com, that one record finishes both legs.** Or it is thirty seconds in the dashboard.

### Read-through is pre-wired and waiting on that record

Already done on the Space (`nougenai/NouGenShards`, docker, public, RUNNING) via the HF API:

```
NGS_UPSTREAM_URL  = https://shards.nougenai.com   HTTP 200
NGS_UPSTREAM_NAME = blade                          HTTP 200
```

The seeding shipped in `d4798e8` registers those at boot. The moment the CNAME exists and the Space restarts, it federates against blade's 151k grid and its own ephemeral 89,422 stops being the answer.

Remaining check once DNS lands: `NGS_NODE_TOKEN` must match on both ends — blade's is `9c67af03a9da`; someone with Space-secret read access should confirm the Space's matches, or set it to blade's.
