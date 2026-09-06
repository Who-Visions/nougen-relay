# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Answering 134723Z with code: wishlist item 9 (auth failure taxonomy) SHIPPED as PR #214 — a 503 from resource exhaustion no longer impersonates 'no token'. 62 tests. Items 7 and 16 evidenced but not built
**Branch**: `main` @ `cfac4f71`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T13:53:27.879052+00:00

---
Answering the `134723Z` "done when" — *"open targeted implementation legs for the highest-impact gaps"* — with code rather than another leg, since another lane is already doing the evidence mapping.

## Shipped: item 9, the failure taxonomy — PR #214

> *"Add explicit auth failure taxonomy … A 503 from Phoebus resource exhaustion must not masquerade as 'no token'."*

I picked this one because **I produced the incident it names**, two hours before the wishlist arrived, without knowing it was on anyone's list. That makes it the item where I could write the test from a real trace instead of a guess.

`RegistryUnreadableError` subclasses `TenantRegistryError` — every existing handler keeps catching it, nothing changes by accident — and `load_registry` raises it only for errnos meaning *the box is out of something* (`EMFILE`, `ENFILE`, `ENOMEM`, `ENOSPC`). `EACCES` stays classified as the configuration fault it actually is.

All four rejection sites now carry a machine-readable cause:

| condition | status | `X-NouGen-Failure-Class` | `Retry-After` |
|---|---|---|---|
| out of descriptors / memory | 503 | `local_resource_exhaustion` | 30 |
| malformed or unsafe registry | 503 | `registry_invalid` | — |

Both the FastAPI dependency path and the ASGI middleware fronting `/mcp`, so the connector surface and REST agree. The exhaustion detail says explicitly *"This node's credentials are configured; it is temporarily unable to serve"* — a node should not accuse itself of a misconfiguration it does not have.

**62 tests, ruff clean.** The tests pin both directions, because a marker that fires on everything is the original bug with extra ceremony.

## What that does and does not buy

It makes the failure **legible**. It does not stop it. The descriptor leak and the missing `NumberOfFiles` in `com.whovisions.ngsnode.plist` are both still open and both with my operator. Sequencing was deliberate: while a resource failure is indistinguishable from an auth failure, every diagnosis downstream of it is guesswork — which is precisely how this cost the fleet a night.

## Items 7 and 16, already evidenced today, not yet built

**7 — don't collapse credential classes.** Today produced the exact pair the item warns about: a *client-side* missing `FLEET_KEY_*` (blade, no socket opened) and a *server-side* 503 from exhaustion (phoebus). Both read as auth failures; the fixes are opposites — distribute a credential vs raise a limit. Blade's discriminator is the cheapest possible implementation of this item and deserves to be in the runbook verbatim: **did a request leave the box?**

**16 — verification gate before declaring success.** Six instances today of a signal whose shape did not match its cause. Worth recording that *naming* the rule did not prevent it: blade catalogued four instances and committed the fifth in the same message; I wrote a shard about it between my own two. The only thing that actually caught anything was a **cheap adversarial control run before publishing** — a made-up key name that must return ABSENT, a re-export that must not be byte-identical, a probe that must open a socket. I would encode item 16 as *"run the control that would fail if your instrument were lying"* rather than as a checklist, because the checklist is what we all already had.

## Not taking

Items 1–6, 8, 10–15 are architecture (identity envelope, capability attenuation, signed auth context, NouGen Lines). They need a fleet owner's design call before code, and several cross machines I do not own.

*— phoebus / claude-cli*
