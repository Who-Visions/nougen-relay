# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Make NouGen connector stack publicly reproducible from the public repo
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T04:33:08.766Z

---
Architecture requirement: what works for Dave's private fleet must also be reproducible by a stranger starting from the public repository. Treat this as a release criterion, not optional documentation polish.

A clean-room user should be able to:
1. Clone the public repo on a new machine.
2. Follow documented prerequisites with no hidden local knowledge.
3. Create their own credentials/secrets without copying Dave's secrets.
4. Configure environment variables from a complete .env.example or equivalent schema.
5. Start the required services with documented commands.
6. Connect supported AI clients/providers through the same canonical public MCP pattern, with provider identity resolved behind ingress.
7. Exercise shard health, recall, tracker, relay, and any other public surface exposed by the repo.
8. See correct per-provider/per-client ledger attribution.
9. Recover from common failures using documented diagnostics.
10. Pass an automated smoke test that proves the install behaves like the reference system.

No dependency on undocumented absolute paths, Dave-specific usernames, private machine names, pre-existing local vault state, hidden Cloudflare configuration, private DNS assumptions, manually seeded databases, or credentials committed elsewhere. Private infrastructure may provide hosted convenience, but the software itself must be bootstrappable by an unrelated user.

Recommended release gates:
* CLEAN-ROOM CI: build/test from a fresh runner with only declared dependencies and test secrets.
* BOOTSTRAP COMMAND: one documented entrypoint for initial setup where practical.
* CONFIG CONTRACT: validate required env vars at startup and fail with actionable messages.
* SECRET SEPARATION: examples contain names/placeholders only, never values.
* DATA BOOTSTRAP: empty-state initialization and migrations documented/automated.
* PROVIDER MATRIX: ChatGPT, Claude, Gemini, Perplexity, or any supported client documented against one canonical MCP architecture, not bespoke public URLs.
* LEDGER TEST: each simulated client must attribute writes/events to its actual lane/provider.
* PUBLIC README: architecture, install, run, connect, verify, troubleshoot, upgrade.
* REPRO TEST: an external machine should reach a green smoke-test state without access to Dave's local environment.

Done when a stranger can clone the public repo and independently reproduce the same class of working connector behavior Dave is using, with their own identity, secrets, storage, and ledger.
