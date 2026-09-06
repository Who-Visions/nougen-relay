# 🤝 Git Handoff — claude-app / outpost

**Goal**: blade: Google Sign-In on the fleet connector is LIVE - how to use it, the GOOGLE_ALLOWED_EMAILS revocation switch, the pinned-callback rule you must not undo, and how to wire it on your own worker
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-15T23:22:11.764Z

---
## Google Sign-In on the fleet connector -- already live. You do not build it, you use it.

Shipped and verified 2026-08-15. **You have already used it without being told**: your legs tonight
are signed `g-whoentertains`, which is a Google identity, not a fleet key. That flow is the one
documented here.

### For a lane that just wants in (30 seconds, no key to paste)
1. Add the connector: `https://fleet.nougenai.com/mcp` (or https://nougen-fleet-mcp.whoentertains.workers.dev/mcp -- both live).
2. On the consent screen click **Continue with Google**.
3. Pick an allow-listed account. Done. No fleet key, no secret handling.

Fleet keys still work and are unchanged -- the button is additive, not a replacement. Use a key for
headless/CI lanes, Google for humans on a device.

### Who is allowed (this is the revocation switch)
`GOOGLE_ALLOWED_EMAILS` on the Worker, comma-separated. Currently:
whoentertains@gmail.com, davemeralus@gmail.com, dave@whovisions.com, contact@whovisions.com,
aiwithdav3@gmail.com, superdavewho@gmail.com, nougenai@gmail.com

Remove an address and that identity's tokens die on the next call -- `identityStillEnrolled()`
re-checks the allowlist on every request, exactly like removing a FLEET_KEYS pair. Adding an
address is a var edit + `npx wrangler deploy` from source; do NOT hand-edit in the dashboard, a
deploy from source overwrites it back.

### What your identity becomes
`g-<localpart>` -- whoentertains@gmail.com -> `g-whoentertains`. That string is what `fleet_whoami`
reports and what gets stamped as the **agent** on every leg you write. The machine stays
`CONNECTOR_LANE` (claude-app) for all connector lanes, so legs read `<stamp>__claude-app__g-you`.
If you want blade-authored legs to read as blade, that is a CONNECTOR_LANE change and a redeploy,
not an auth change.

### The design decision you must not undo
`GOOGLE_REDIRECT_ORIGIN` is PINNED to https://nougen-fleet-mcp.whoentertains.workers.dev

The callback used to be derived from `url.origin`, which broke the moment the Worker answered on a
second hostname: Google rejects any redirect_uri not registered on the client, so sign-in worked on
workers.dev and failed on fleet.nougenai.com. Pinning it means ONE registered callback covers every
hostname the Worker will ever serve. The signed state blob carries the client's real redirect_uri,
so a flow can START on fleet.nougenai.com and LAND on the workers.dev callback -- verified live
(state minted on the branded domain verified at the workers.dev callback).

**Only ever set GOOGLE_REDIRECT_ORIGIN to a value registered on the Google client, or sign-in
breaks on every hostname at once.**

### If you stand up your OWN connector with Google
Client lives in the **Kaedra-Ai** GCP project. Client id (not a secret):
`69017097813-nsh02551klut5u5g51rotgp96344bu76.apps.googleusercontent.com`
Secret is a Worker secret; vaulted on outpost as GOOGLE_OAUTH_CLIENT_SECRET_KAEDRA.

1. console.cloud.google.com/auth/clients -> Create client -> type **Web application**
2. Put the callback under **Authorized redirect URIs** -- NOT under Authorized JavaScript Origins.
   Origins reject any URI with a path; pasting it there yields
   'Invalid Origin: URIs must not contain a path or end with /'. Cost us a round trip.
3. Worker vars: GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_ORIGIN, GOOGLE_ALLOWED_EMAILS
   Worker secret: `printf '%s' "$SECRET" | npx wrangler secret put GOOGLE_CLIENT_SECRET --name <worker>`
   printf from bash, NOT a PowerShell pipe -- it appends a newline.

### Traps that cost real time here
- **Custom domains lag.** After deploy, workers.dev updates first; a branded route can serve the
  previous version for a few seconds. My first post-deploy check said the fix had not landed. It had.
- **Adding `routes` silently disables workers.dev.** That orphaned the phone connector AND the
  registered Google callback until `workers_dev: true` was set explicitly.
- **Cloudflare bot check 403s scripted flows** (error 1010) with the default Python UA, before the
  Worker ever runs. Any script against these endpoints needs a real browser UA.

### Verify without a browser
`python tools/fleet_key_check.py FLEET_KEY_<NAME>` runs the full OAuth 2.1 + PKCE flow headlessly
(register -> consent -> code exchange -> authenticated fleet_whoami). Shipped in NouGenShards.

### Done when
Blade adds the connector, signs in with Google, and `fleet_whoami` reports `g-<you>` -- no fleet
key involved.
