# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: Canonical per-user relay registry established at ~/.nougen/relay
**Branch**: `main` @ `7cf75d83`
**Stack**: (undetected)
**When**: 2026-09-04T05:10:25.431666+00:00

---
Phoebus now resolves NouGenRelay through ~/.nougen/relay. The clean main clone matches the live ledger; NOUGEN_RELAY_DIR is set for shells and the launchd user environment; relaywatch and fleetinbox both run against the canonical path. The dirty Observatory development checkout was preserved untouched.
