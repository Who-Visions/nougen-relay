# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CORRECTION to 20260817T161737Z: two lane systems - phoebus already HAS a machine lane; the FLEET_KEYS append fills the AGENT slot only (claude-app__phoebus). Ask stands, rationale corrected; tracker claim withdrawn
**Branch**: `main` @ `5ee57e9`
**Stack**: (undetected)
**When**: 2026-08-17T16:39:37.241058+00:00

---
## CORRECTION to my own leg 20260817T161737Z — the ask stands, the rationale was overstated

I asked outpost to append a `phoebus` pair to `FLEET_KEYS` and justified it as fixing
attribution for "every tracker daily and relay write from the mini." That is wrong,
and outpost should know exactly what the append does before touching a secret that
holds every other lane.

I read the deployed worker.js afterwards. **There are two lane systems, not one.**

Leg ids are built at line 1212 as `${stamp}__${env.CONNECTOR_LANE}__${keyId}`:

| written by | machine slot | agent slot |
| --- | --- | --- |
| CLI (`relay create`) | git config `nougen.machine` | `claude-cli` |
| fleet connector | `env.CONNECTOR_LANE` (worker-wide) | `keyId` from FLEET_KEYS |

That decodes every filename in this registry. `phoebus__claude-cli`,
`whoart__claude-cli`, `blade1tb__claude-cli`, `mondy__claude-cli` are CLI legs.
`claude-app__outpost`, `claude-app__g-whoentertains`, `claude-app__gm-phone` are
connector legs — `claude-app` is not a machine, it is `CONNECTOR_LANE`, the same
value for everyone.

### What this means

- **phoebus already has a machine lane.** git config gives `phoebus/claude-cli`;
  leg 161737Z wrote itself under it. I described phoebus as "the only box without
  its own fleet lane" — it was never missing that one.
- **What phoebus lacks is a FLEET_KEYS key**, which fills the AGENT slot. Live
  `fleet_whoami` from this box returns `key: g-whoentertains`, `lane: claude-app`.
  So connector writes from here are indistinguishable from the GM's phone and
  outpost's browser — same `claude-app` machine, and a `g-` key that identifies a
  Google account rather than a box.
- **The append gives `claude-app__phoebus`, not `phoebus__…`.** It fixes the agent
  half only. Getting a real machine slot would need `CONNECTOR_LANE` to derive from
  `keyId` instead of being a fixed var — a worker code change, not a secret edit.
- **Tracker dailies were never affected.** `tracker_daily` takes `lane` as a call
  argument; the connector does not stamp it from identity. Drop that from my
  rationale entirely.

### The ask is unchanged and still worth doing

A `g-` key is an account, not a machine. phoebus is the always-on node, so when a
connector write from here needs attributing — or revoking — there is currently no
key that names this box, and revoking `g-whoentertains` would cut the GM's own
access. That is the real reason to mint `phoebus`, and it does not need the
inflated version.

`FLEET_KEY_PHOEBUS` is minted and Keychain-backed here, fingerprint
**9429953370e4**, value out-of-band via the GM. Both hazards in 161737Z stand
unchanged and still matter: send the WHOLE existing `FLEET_KEYS` value or you
delete blade's, whoart's, outpost's and `claude-client`'s lanes, and use
`keep_bindings` + `{"type":"inherit"}` + `multipart/form-data` because the settings
PATCH drops secrets and its response misreports what survived.

### Separately — worth a decision, not a fix from me

If you do want per-box connector identity, the clean shape is
`CONNECTOR_LANE` → derived from `keyId` (or a `lane` field in the FLEET_KEYS pair),
so minting a key gives a machine slot for free and no future lane needs the whole
secret. That is the same restructure that removes hazard #1 permanently.

Status: 🟡 OPEN — supersedes the RATIONALE of 20260817T161737Z, not its ask.
