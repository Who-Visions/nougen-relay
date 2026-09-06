# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: LIVE: canonical NouGenMsg now targets active Codex through authenticated node transport
**Branch**: `main` @ `e9aac4e2`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T05:51:36.634358+00:00

---
Canonical clone installed at ~/.nougen/nougenmsg on branch codex/nougenmsg-native-queue commit 360a27a. The nougenmsg command is available through ~/.local/bin and sends structured authenticated JSON to the supervised port 8766 receiver; peer-gated by default, explicit --owner provenance through Keymaker, no SSH shell interpolation, and plaintext credentials refused off loopback. Receiver target routing landed on NouGenShards branch codex/live-relay-queue commits 753dfb3 and 93ed4bd: @codex reaches only Codex, @claude only Claude, @all broadcasts; keyring is now declared and installed for fail-closed Keymaker auth. Verified 8 NouGenMsg tests, 141 transport/security tests, Ruff, compilation, launchd auth required, and an owner @codex end-to-end probe with delivered=true.
