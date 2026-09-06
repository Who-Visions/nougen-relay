# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Design dynamic README updater for NouGen public repositories
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-28T23:34:06.510Z

---
Dave wants a Python utility inside NouGen that can dynamically keep README files current across public NouGen repositories. Design it as a controlled documentation compiler, not blind AI overwrite. Suggested architecture: scan repo metadata and known config files, extract canonical facts, preserve hand-written sections, replace only fenced generated blocks, optionally consult current public docs, produce deterministic diffs, validate links/commands, and open commits or PRs rather than silently rewriting production docs. Add a repo manifest with per-repo README sections, source-of-truth paths, public/private flags, and update cadence. Proposed generated markers: <!-- NOUGEN:AUTO:ARCHITECTURE:START --> ... END. Include dry-run, check, write, and CI modes. Done when there is a reusable readme_sync.py plus manifest/schema and GitHub Actions integration for all public NouGen repos.
