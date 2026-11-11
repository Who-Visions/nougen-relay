# Phase 0 — NouGenRelay Protocol Inventory & Frozen Golden Fixtures

Recorded against `Who-Visions/NouGenRelay` baseline `5327c0021` on `2026-11-11` prior to extending `gorelay` with `ack` and `claim`.

## 1. Repository & Directory Inventory

| Surface | Path Pattern | Observed Count / Status | Protocol Notes |
| --- | --- | --- | --- |
| Primary handoffs | `.handoffs/*.json`, `.handoffs/*.md` | `6,881` top-level `.json`, `6,842` top-level `.md` | `75` `.json` without `.md` partner; `36` `.md` without `.json` partner; missing `"status"` means `"open"`. |
| Non-handoff sidecars | `.handoffs/ask_verdicts*.json` | Ignored via `.gitignore` | Auxiliary JSON sidecar inside `.handoffs/`; not a relay leg. |
| Canonical claim store | `.handoffs/claims/*.json` | `853` `.json` records | `claims_dir(root)`; `scope` may be string OR legacy JSON `[]string`; normalized via `_normalize_scope_field`. |
| Legacy claim dir (v1) | `.claims/*.json` | `6` historical records (`2026-09-14..2026-10-01`) | Legacy `*_ack.json` closing receipts; read-only legacy artifacts. |
| Legacy claim dir (root) | `claims/*.json` | `1` historical record (`2026-09-29`) | Legacy single-file claim receipt; read-only historical artifact. |
| Hot lease state | `.relay/leases/<leg_id>.lease.json` | Ignored via `.relay/` | `leases_dir(root)` (`NOUGEN_LEASE_DIR` override); monotonic `fencing_token`, 12-hex `lease_id`. |
| Idempotency ledger | `.relay/idempotency/<key>.json` | Ignored via `.relay/` | `idempotency_dir(root)` (`NOUGEN_IDEMPOTENCY_DIR` override); SHA-256 of `<leg_id.strip()>:<goal.strip()>`. |
| External host authority | `~/.nougen/AUTHORITY.md` | Outside repo (`not committed`) | Host-local precedence & operational doctrine; intentionally excluded from git repo. |
| Compiled Go binary | `gorelay/gorelay` | Gitignored | Present in private `.gitignore`; must also stay ignored in public `.gitignore`. |

## 2. Fencing & Lease Symbols in Python Baseline

- `fencing_token` appears in **3 source files** (`src/nougen_relay/core.py`, `src/nougen_relay/guard.py`, `tools/relay_daemon.py`) plus `tests/test_lease_control_plane.py`.
- `lease_id` appears in **1 source file** (`src/nougen_relay/core.py`) plus `tests/test_lease_control_plane.py`.

## 3. Single-Writer Discipline

Git commits remain the append-only audit log while `.relay/leases/` and `.relay/idempotency/` hold hot execution state. Run **one writer only** (`gorelay` or Python `nougen relay` — never both concurrently against the same working directory). Mutating `gorelay` subcommands acquire an atomic writer lock at `.relay/.gorelay.lock` and perform atomic temp-file writes (`write -> rename`).

## 4. Golden Fixtures

Frozen genericized protocol fixtures live under [`gorelay/testdata/protocol/`](../gorelay/testdata/protocol/manifest.json) and are verified by both Go (`go test ./...`) and Python cross-language comparison tests (`tests/test_gorelay_parity.py`).
