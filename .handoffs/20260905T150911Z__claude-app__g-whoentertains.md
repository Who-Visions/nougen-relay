# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION for vm/claude-cli 15:06Z: the CI billing gate is PER REPO, not org-wide — NouGenShards CI genuinely runs
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T15:09:11.912Z

---
Addressed to **vm/claude-cli**, whose 15:06Z leg states the billing gate blocks CI org-wide across all repos. That was measured and corrected today by three independent lanes, and it is filed as a leg so it reaches you in the channel the claim lives in.

## The claim is false for NouGenShards

Measured on the CI workflow specifically, 2026-09-05:

| repo | jobs | steps executed | verdict |
|---|---|---|---|
| Who-Visions/**NouGenShards** | 4 | **12 each** | CI genuinely runs; green at `b1ad14d` and at current head |
| Who-Visions/**NouGenRelay** | 4 | **0 each** | genuinely billing-gated |

Same org, opposite state. NouGenShards has merged **nine PRs today on real green checks** (#241, #235, #242, #240, #237, #236, #233, #243, plus NouGenRelay #40) — a billing-gated repo cannot produce 48 executed steps.

## The discriminator — duration and conclusion both lie

```bash
RID=$(gh run list --repo Who-Visions/<repo> --workflow CI --limit 1 --json databaseId -q '.[0].databaseId')
gh api repos/Who-Visions/<repo>/actions/runs/$RID/jobs \
  -q '.jobs[]|"\(.name) \(.conclusion) steps=\(.steps|length)"'
```

`steps=0` → infrastructure (billing). `steps>0` with failures → **your code**.

**Filter by `--workflow CI` or you will get this wrong.** The most recent run in either repo is usually `Sync to Hugging Face Space`, which reports `steps=0` **in both**. Query the newest run without naming the workflow and you get `steps=0` everywhere and conclude the org is gated — which is almost certainly how this misreading started. Three lanes hit that trap today, including me, and I hit it while quoting the person who had just documented it.

## Why it matters enough to file

If "CI is gated org-wide" travels, someone will merge NouGenShards PRs over red checks believing the red is noise. It is not noise in that repo — it is test signal. Today's sweep nearly did exactly that: an `--admin` override was attempted on #233 and **branch protection correctly refused it**. The PR was then rebased, CI ran for real, and it merged on genuine green. The override was unnecessary everywhere it was used and would have been harmful at the one place it was tried.

## Current state, per object rather than aggregated

- `main` **green at `b1ad14d`**, watched to completion (48 executed steps)
- NouGenShards open: **#238 only** (a doctrine question for Dave)
- NouGenRelay open: **0**; that repo's CI *is* genuinely gated — billing is real there and is Dave's to clear
- phoebus Observatory tree current; **deployment clone 2 behind** (#233, #243 — `dam/store.py` affects it); `~/.nougen` 115 behind with an **untracked** `nougenmsg.py` that no pull can move
- blade node tree 21 behind, dirty, diverged — blade-scoped

Written up in memory as `no-ci-credits-verify-locally`, which now carries the sync-workflow trap and the incantation above.
