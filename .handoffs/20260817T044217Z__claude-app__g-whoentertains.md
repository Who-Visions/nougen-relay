# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: RULING: federation now, replica later — blade seeds stopped, whoart lane = store #43, tunnel join deferred behind a continuous-sync design
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-17T04:42:17.627Z

---
## Situation
Codex lane (whoart) executed the GM's "same tunnel, share the lane" instruction by rewriting node_lane.ps1 to a shared token, authoring tunnel_lane.ps1, installing a private lane key on blade, and launching a blade→whoart full-grid seed. Two seed processes ended up running concurrently (one with --include-private), progressing ~156 of 158,882 rows because each row transits the full capture path (dedup→redact→embed→encrypt) — a multi-day operation. A one-time seed followed by a shared hostname also drifts immediately: no continuous sync exists, so the replica design as-built recreates split-brain after the first divergent capture.

## Actions taken (GM delegated: "steer it straight")
1. Blade's 13 encrypted rows verified decryptable under the installed key (13/13 ok — "prior key preserved=False" meant no prior key existed; nothing was clobbered).
2. Both seed processes stopped on blade (pids 32052, 44908). Zero relay_push processes remain.
3. Ruling injected into the Codex session directly (codex exec resume); Codex adopted: "Ruling adopted exactly as stated. No transport action was taken."

## The ruling
- FEDERATION IS THE LANE OF RECORD for whoart: store #43 (whoart_grid_vault.db on blade, refresh = rebuild + scp same path). Blade's grid stays the single write-canonical substrate.
- REPLICA IS DEFERRED, NOT REJECTED: it may proceed only behind a written continuous-sync design (scheduled bidirectional /sync, drift/conflict policy, write-ownership rule) with GM signoff. Until then: no tunnel join, no seed, no shared-token cutover.
- Whoart's node may stay up LAN-only, token-gated.
- The ~156 already-seeded rows stay (deduped, harmless).
- Codex's assurance-sprint work (PR #89, redaction, preflight, Iris oracle, CLI fix) is untouched and valued.
- STILL OPEN, GM-ONLY: revert of the 47.5MB FLEET-LOG commit (bcb04e2, NouGenRelay) and correction of the AUTHORITY.md transport line.

## Done when
A continuous-sync design doc exists and is GM-approved before any multi-connector tunnel work resumes; until then all lanes treat blade as write-canonical and whoart as federated-read.

∴ FABLE
