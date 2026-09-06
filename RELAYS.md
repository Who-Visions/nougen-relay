# Live Relay Registry

The live cross-machine registry is `.handoffs/` in this repository and on
`Who-Visions/NouGenRelay` branch `main`.

For every relay:

1. Read the `.json` record for status and identity.
2. Read the paired `.md` file for the complete handoff body.
3. Check `.handoffs/claims/` before editing shared files.
4. Preserve other lanes' dirty or staged files.

State changes from `relay ack`, `relay checkpoint`, and `relay complete` use a
compare-and-swap GitHub contents write when `gh` is available, targeting the
canonical branch instead of the checkout's feature branch. Local-only remotes
retain the legacy branch-push fallback.

Antigravity's legacy writer may still publish to:

`C:\Users\super\Watchtower\NouGen\NouGenShards-push-main\.handoffs\gemini handoffs`

If an expected Antigravity leg is missing here, check that directory before
concluding the relay failed. The complete map is in
`C:\Users\super\Watchtower\NouGen\RELAYS.md`.
