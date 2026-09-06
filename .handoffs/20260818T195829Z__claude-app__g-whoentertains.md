# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: FIXED: ChatGPT connectors were 400ing — nougen-fleet-mcp redirect allowlist was hardcoded Claude-only. Deployed, bindings intact.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-18T19:58:29.378Z

---
Production unblock, done from phoebus 2026-08-18. Verified live, not inferred.

## What was actually wrong

`nougen-fleet-mcp` carried a hardcoded allowlist:

```js
const REDIRECT_ALLOW = [
  /^https:\/\/claude\.ai\//,
  /^https:\/\/claude\.com\//,
  /^http:\/\/localhost(:\d+)?\//,
  /^http:\/\/127\.0\.0\.1(:\d+)?\//,
];
```

Every ChatGPT callback failed `redirectAllowed()` and returned `400
invalid_redirect_uri` before any other logic ran. It gates `/register`,
`/authorize` and `/google/start`, so all three entry points refused. The
node itself was never involved — `app.py`'s own `/register` has no such
allowlist and would have accepted ChatGPT fine. `/mcp` also carries no
`x-nougen-origin` header, so it does not pass through `nougen-shard-failover`
at all; diagnosing this at the node wastes the afternoon.

Nothing broke today. The allowlist has been Claude-only since the worker was
written; ChatGPT simply was not tried against it before.

## Fix, deployed

- ChatGPT callbacks added (`chatgpt.com`, `chat.openai.com`, `platform.openai.com`)
- `redirectAllowed(uri, env)` now also honours a `REDIRECT_ALLOWLIST` binding —
  comma-separated https:// origin prefixes, matched as **literal prefixes, never
  as regex**, so a stray character in config cannot silently widen it to `.*`.
  Adding a vendor no longer needs a redeploy.
- Fixed a latent bug in the same patch: `uris.every(redirectAllowed)` passed the
  array INDEX as the second argument. Harmless while the function took one
  parameter; it would have silently become the `env` argument.

Deployed via the CF API from the phoebus lane with
`keep_bindings: ["secret_text","plain_text"]`. **28 bindings before, 28 after,
name-for-name identical** — the documented settings-PATCH secret-drop did not
occur. Verified after deploy:

| check | result |
|---|---|
| ChatGPT callback | 201 + client_id |
| Claude callback | 201, no regression |
| `evil.example.com` | 400 refused |
| non-TLS host | 400 refused |
| `/mcp` unauthenticated | 401, correct |

Live on `fleet.nougenai.com`, `mcp.nougenai.com`, `shards.nougenai.com`.

`nougen-shards-mcp` still carries the same Claude-only hardcode and was left
alone — it was not in the path of this failure. Worth the same patch before
someone hits it.

## Process failure worth more than the fix

**I SSH'd to blade for `CLOUDFLARE_API_TOKEN_NOUGEN_FULL` that was already in
phoebus's own Keymaker vault.** Every node carries
`~/.nougen/secrets/shards_secrets.db`. Phoebus held the CF token the whole time;
only `NGS_NODE_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` were genuinely missing. Both
are now ingested locally and round-trip verified, so no node should cross a
machine boundary for these again.

Order is Keymaker -> other node -> ask GM. Not the reverse.

Two BINDING sections added to the Observatory `CLAUDE.md`, above the NouGen hook
so they are read before any work starts: **Read the relay first** and
**Credentials come from the Keymaker**.

## Also landed today

- **PR #102 merged** — `/sync/push` was dropping `original_timestamp`, silently
  re-dating every bulk-ingested shard to ingest time. Permanent, because
  `capture()` dedups on a content hash so a corrected re-push is a no-op. Two
  regression tests, both fail without the one-line change. This is the fix the
  Space got directly as `14ca0388` that never landed upstream — every node now
  carries it from source. **Blade is still running pre-#102 code and needs a
  pull + restart to pick it up.**
- `tools/fleet.py` de-hardcoded (`10.0.0.87` -> `NOUGEN_BLADE_HOST`, default
  `blade1tb.local`).

## Open

- Blade: pull + restart to carry #102.
- HF Space is **503**, `hf-mount` init failure. It is `nougen-shard-failover`'s
  PRIMARY origin, which is why blade serves every public hostname right now.
- `nougen-shards-mcp` allowlist unpatched.

No secrets in this leg — key names, paths and results only.
