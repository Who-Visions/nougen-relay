# 🤝 Git Handoff — blade1tb / claude-cli

**Goal**: phoebus PRs #1 (rules/react) and #2 (env docs) merged; main green on Windows
**Branch**: `main` @ `6acc961`
**Stack**: (undetected)
**When**: 2026-07-31T21:40:21.148833+00:00

---
Both open PRs are merged into main and main is green on this box (65 tests, ruff clean).

- #2 (docs env names) verified against the code first: core.py really reads
  NOUGEN_GIT_HANDOFF_DIR and NOUGEN_HANDOFF_STALE_HOURS. Merged as-is.
- #1 (rules/react) merged as designed — rules-do-not-travel, self-ignoring
  .gitignore, baseline adoption on first run, own-machine skip. No changes to
  the design, two follow-ups on top:

1. `default_timeout()` — an unpinned rule now resolves NOUGEN_RULES_TIMEOUT at
   fire time instead of baking 60s into the record. A rules file copied to
   another box was carrying the authoring box's patience with it.
   `--timeout` still pins per rule; stored as null when unpinned.
2. Two tests asserted the developer's setup, not the behaviour:
   - test_rules used `echo "$RELAY_FROM_MACHINE"`, which through shell=True on
     Windows reaches cmd.exe verbatim and never expands. Now writes the receipt
     with a python one-liner, so the test asserts the rule ENVIRONMENT and not
     the shell dialect. (Rules are per-machine and local, so operators can still
     write either dialect — that part is by design, not a portability bug.)
   - test_entry_point read installed metadata, so any clone without
     `pip install -e .` failed a test about pyproject.toml's contents. Now reads
     the checkout and separately proves nougen_relay.cli:main is importable.

Not started, unchanged from the previous leg: the NouGenQ -> NouGenRelay
migration and the convergence decision (NouGenShards still runs its own
private registry). Nine unacked legs remain on NouGenQ's registry.
