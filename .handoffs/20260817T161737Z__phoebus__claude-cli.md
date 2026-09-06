# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: ASK outpost: append a phoebus lane to FLEET_KEYS (fp 9429953370e4); phoebus vault initialised + keyring installed; mcp.nougenai.com routes to phoebus not the stale Space
**Branch**: `main` @ `e5ebdbe`
**Stack**: (undetected)
**When**: 2026-08-17T16:17:37.910903+00:00

---
## ASK — append a `phoebus` lane to FLEET_KEYS on nougen-fleet-mcp

phoebus is the always-on node and the only box in the fleet without its own
fleet lane. blade1tb, whoart and outpost all have one; this box has been
borrowing `g-whoentertains` (the Google-minted lane, worker line 379), so every
tracker daily and relay write from the mini is attributed to an identity that
is not a machine. That makes per-lane usage accounting wrong for the one box
that never sleeps.

### What I did on phoebus (done, verified)

- keymaker vault did not exist here AT ALL — no `~/.nougen/secrets/`, zero
  providers, `find_legacy_stores()` empty. Initialised it (dir `0700`).
- `keyring` was missing from the nougenshards venv, so `ingest_secret` refused
  to store and the only alternative was `NOUGEN_ALLOW_PLAINTEXT_VAULT=1`.
  Installed `keyring`; backend is now `keyring.backends.macOS.Keyring`, so the
  vault is Keychain-encrypted at rest rather than cleartext. Anyone standing up
  a fresh mac lane hits this same wall — it is a prerequisite, not a detail.
- Minted the lane secret, stored as `FLEET_KEY_PHOEBUS`, vault round-trip
  verified.

```
lane name    phoebus
vault key    FLEET_KEY_PHOEBUS   (on phoebus, Keychain-backed)
sha256 fp    9429953370e4        (first 12 hex of sha256 of the value)
length       55
```

The VALUE IS DELIBERATELY NOT IN THIS LEG. Legs are committed to git; a live
fleet key does not go in one. Compare fingerprints, never values — the GM
carries the value to you out-of-band, and `9429953370e4` proves the pair you
paste is the one this box holds.

### What outpost needs to do

`FLEET_KEYS` is a single Worker secret holding `name:secret` pairs, split on
`,` then on the FIRST `:` (worker.js line 87). Append one pair:

```
...existing pairs...,phoebus:<value from GM>
```

Two hazards, both already paid for once by this fleet:

1. **You must send the WHOLE existing value.** Worker secrets never read back —
   I cannot see the current pairs from phoebus, which is exactly why this is an
   ask and not a patch. Writing `FLEET_KEYS` blind would delete blade's,
   whoart's, outpost's and `claude-client`'s lanes, and `claude-client` is what
   fronts blade's gateway. Every shards_* tool in the fleet dies with it.
2. **The settings PATCH drops secrets.** Use `keep_bindings`, send secrets as
   `{"type":"inherit"}`, and use `multipart/form-data` not JSON. Do NOT trust
   the PATCH response's binding list — it has lied before. Re-verify the five
   secrets (`FLEET_KEYS`, `GITHUB_TOKEN`, `GOOGLE_CLIENT_SECRET`,
   `SHARD_GATEWAY_TOKEN`, `SIGNING_SECRET`) after deploying.

### How phoebus verifies on its side

Headless, no browser, key never printed:

```
cd NouGen/nougenshards && ./.venv/bin/python tools/fleet_key_check.py FLEET_KEY_PHOEBUS
```

Full OAuth 2.1 + DCR + PKCE dance then an authenticated `tools/call`. When that
goes green, `fleet_whoami` should report lane `phoebus`.

### Two findings while I was in here, unrelated to the lane

- **`mcp.nougenai.com` is NOT the stale HF Space.** blade's leg `20260815T232500Z`
  left this open. It routes through PHOEBUS's named tunnel `e2f9e313` to
  `127.0.0.1:4444` — this box's local node. cloudflared config here serves both
  `ngs.nougenai.com` and `mcp.nougenai.com` off that tunnel. So the "stale third
  deployment" theory is wrong: the hostname points at a live node, and the
  staleness people saw is whatever `nougen-shards-mcp` still serves. Closing
  that open item.
- **nougen-fleet-mcp is healthy after the 02:41Z CORS deploy.**
  `/.well-known/oauth-authorization-server` → 200,
  `/mcp` → 405 on GET (correct for streamable HTTP). Slashless `/mcp` now 307s
  instead of 404ing on the node, so PR #86 looks superseded — someone should
  close or rebase it. Every hostname answers: `mcp.nougenai.com/mcp/`,
  `shards.nougenai.com/mcp/`, `ngs.nougenai.com/mcp/` all 401 (alive,
  auth-gated), none 404.

  Note for whoever chases the GM's connector next: the fleet MCP tools 404 from
  THIS session's connector while the Worker itself is provably 200/405. That is
  a stale connector URL, not a dead backend — connector URLs are immutable, so
  it needs remove + re-add, not an edit.

Status: 🟡 OPEN — outpost claims the FLEET_KEYS append. phoebus's half is done
and waiting; nothing else here is blocked on it.
