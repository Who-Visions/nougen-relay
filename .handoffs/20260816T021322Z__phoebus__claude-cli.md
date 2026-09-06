# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: URGENT for outpost — fleet worker has NO CORS, so every claude.ai WEB connector fails post-auth. ~10-line fix, patch attached. Also: signer mismatch between the two workers is now PROVEN.
**Branch**: `main`

---
## The GM's "authorized, but error when connecting" — root cause found

Web claude.ai calls connectors FROM THE BROWSER. OAuth is top-level navigation (no CORS),
so auth succeeds — then the first fetch to /mcp dies on preflight:

```
nougen-fleet-mcp (both hostnames):  OPTIONS /mcp -> 401, zero access-control headers
nougen-shards-mcp:                  OPTIONS /mcp -> 204 + full CORS
```

Native apps do not preflight — which is why every claude-app lane (including yours)
connected fine all night while the GM's browser failed on every URL variant.

## FIX (outpost, `C:\Users\super\Outpost\nougen-fleet-mcp`)

Copy the CORS layer you already wrote for nougen-shards-mcp into the fleet worker:

1. `CORS` const with `allow-headers: authorization, content-type, mcp-protocol-version,
   mcp-session-id, accept` and `expose-headers: WWW-Authenticate, mcp-session-id`
2. In fetch(): `if (request.method === "OPTIONS") return new Response(null, {status: 204, headers: CORS})`
   BEFORE the path switch
3. Wrap every response in withCors() — the 401 challenge especially, or the browser
   cannot read WWW-Authenticate and discovery breaks

`npx wrangler deploy` and the GM's web connector works with no client-side change.

## Signer mismatch PROVEN (upgrades my leg 015716Z from hypothesis to fact)

Both workers derive client_id = prefix + b64url(HMAC(SIGNING_SECRET, "client|" + uri)).
Same registration POST to each:

```
ngf-5BxNDxA9FIu_Dlt_CY6L-HYgDs4RnYdm   (fleet)
ngs-Gb4xMTdfAIo_eKeVe5yRAfcOJwru7cnA   (shards-mcp)
```

Different HMACs -> different SIGNING_SECRETs -> nougen-shards-mcp's Google flow is dead
(its gstate lands on the fleet worker's callback and fails verification). Either share
the fleet secret, repoint its GOOGLE_REDIRECT_ORIGIN at a hostname it serves itself, or
retire the worker once the fleet worker has CORS.

## Kaedra client housekeeping (whoever holds worker creds)

- The client now carries TWO enabled secrets (****0L8K 09:22, ****O-MP 19:37). The live
  workers' google_secret_fp is 7J8RPVJNbC7V. Do NOT delete either blind: disable the
  older one, run a live sign-in, then delete on green / re-enable on red.
- Redirect URI list has a bare-origin entry `https://nougen-shards-mcp...workers.dev`
  (no /google/callback path) — matches nothing, either append the path or drop it.

Status: 🟡 OPEN — outpost claims the CORS deploy; it unblocks the GM's browser immediately.
