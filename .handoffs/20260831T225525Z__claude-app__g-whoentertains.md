# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: whoart's _pre_correction_20260829 backup does NOT hold pre-correction data — GM attention needed on data provenance
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T22:55:25.191Z

---
## 🔴 Active Incidents
- shards_capture still returning empty `{}` (third failed attempt this session, ~22:54Z) — this leg is the durable record since the vault write path is unreliable right now.

## 🟡 Ongoing Investigations
- **NEW, from nougen-bd, chasing the "correction" false-positive I diagnosed earlier**: `dailies/whoart/_pre_correction_20260829/` does NOT contain pre-correction data. All 22 backup files already carry their own "correction" object stamped 14:12:40-04:00; the live records are stamped 14:18:33-04:00 — two correction passes ran six minutes apart, and the backup captured pass 1's output, not the true original. **The actual pre-correction whoart data does not appear recoverable from this tree.**
  - Delta pass1→pass2 (summed, 22 files): `estimated.output_tokens` 0 → 4,302,732; `exact.output_tokens` 14,578,331 → 14,937,210; `invocations` 14,877 → 14,912. whoart's August now carries 4.3M output tokens of ESTIMATED provenance that pass 1 called entirely exact.
  - **Reassuring**: `record["totals"]` (what fleet_dailies.py's aggregate() sums) is byte-identical across both passes — 5,254,204 output tokens, ratio 1.000, all 20 comparable days. Fleet/machine rollups and month-to-date figures are unaffected. Counter `cfae0dd41682` homogeneous across all 199 records, blade1tb/phoebus uncorrected — `--fleet` sums remain legitimate.
  - **Open question, needs whoart context, neither of us is guessing**: correction's stated reason is "dailies captured 36.1% of actual August output tokens." If that's a code defect, blade1tb/phoebus (same counter fingerprint) should show the same undercount uncorrected — they don't. If environmental (whoart-specific), it's local. Totals being byte-identical across both passes suggests the regeneration did NOT actually recover a 64% shortfall in totals — casting doubt on whether "36.1%" describes what the correction actually did. Don't cite that figure as established until someone with whoart context resolves it.
- (Still open, unrelated) Canonical launcher, NOUGENTRACKER_DIR, keymaker store, correction-field allowlist decision, PR #19 merge-classifier block — all previously flagged, all GM/Dave's calls.

## 📋 Recent Changes
- bd and I both deliberately did NOT touch whoart's data, the backup directory, or the allowlist/regex — data provenance and public-repo-content decisions, not a lane's to make.

## ⚠️ Known Issues & Workarounds
- Vault write path (shards_capture) degraded again — third empty `{}` this session on two independent lanes (me, nougen-07). Use relay legs / direct SendMessage as the reliable channel until fixed.

## 📅 Upcoming Events
- None.
