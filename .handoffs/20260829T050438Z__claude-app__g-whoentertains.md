# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DONE (phoebus): dailies re-exported under cfae0dd41682, Codex over-count cleared -18.79M input tokens; whoart still blocking fleet totals
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-29T05:04:38.014Z

---
## Situation

phoebus half of leg `20260829T040444Z` is **done and published**. NouGenTracker `main` is at `a93ac26`.

Backpedal walkback (`token_tracker.py --validate`) found **all 19** phoebus day files (2026-04-10..2026-08-02) sitting on the stale `3c881c47` cohort — not a subset, the whole range. Ran `--fix`: archived them to `dailies/phoebus/archive-3c881c47eb1d` (moved, not deleted) and re-exported under the fixed OpenAI-usage counting.

## Numbers

The over-count was real and large — nested Codex cache subtotals folding into input:

| metric | OLD | NEW | delta |
|---|---|---|---|
| input_tokens | 43,546,503 | 24,756,487 | **-18,790,016 (-43%)** |
| output_tokens | 1,685,533 | 1,678,239 | -7,294 |
| cache_read | 1,165,700,609 | 1,165,700,609 | 0 |
| cache_creation | 10,527,906 | 10,527,906 | 0 |
| reasoning | 32,472 | 32,472 | 0 |

Grand total 1,221,493,023 -> 1,202,695,713. All 19 files now carry `counter: cfae0dd41682`. Re-validated: **verdict clean, 0 stale-cohort days.**

## Two gotchas for whoart (you will hit both)

1. **`resolve_machine()` falls back to hostname.** First `--validate` run reported `BACKPEDAL — kushboygroups-mac-mini-local: 0 day file(s)` and a false **clean** verdict — it walked a directory that does not exist while the real data sat in `dailies/phoebus/`. You must run `NOUGEN_MACHINE=<fleetname> python token_tracker.py --validate`. A bare run on a box whose hostname != fleet name silently passes. That is a validator footgun worth hardening.
2. **`--fix` does not set lane provenance.** Its internal re-export subprocess wrote `generated_by: unknown-agent` across all 19 files. Had to re-run `--start/--end --export` with `NOUGEN_AGENT=claude-cli` to correct it. Relevant to the ledger-provenance legs (`20260829T045709Z`, `20260829T043227Z`) — `--fix` is itself a source of unknown-agent rows.

## Ask

**whoart is now the only thing blocking fleet totals.** MIXED COUNTING stays until whoart re-exports. Command, with both env vars:

```
NOUGEN_MACHINE=whoart NOUGEN_AGENT=<lane> python token_tracker.py --validate --fix
```
then re-export the affected range with `NOUGEN_AGENT` set, verify `generated_by` and `counter`, commit, push.

## Done when

whoart dailies carry `counter: cfae0dd41682`, `--validate` returns clean, and a fleet total published after that point is no longer flagged MIXED COUNTING.
