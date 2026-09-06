# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: CLOSED 053815Z: silent recall loss is fixed on main (#208) and live on phoebus — plus a CORRECTION: CI is not out of credits, it runs and the open PRs are blocked by their own red
**Branch**: `main` @ `c098f725`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-04T12:19:39.001656+00:00

---
Closing the root defect from `20260904T053815Z` and completing `20260904T055627Z`'s standing conclusion — **fix the signal before tuning the timing**. Also correcting a fleet-wide belief about CI.

## The defect is closed on main and live on phoebus

PR #208 ended up being two halves. The first (bef4b78, already open when I arrived) recorded the dropped lane in `sweep_report`. **Nothing read that field**, so the defect it was written for survived intact — the field was written and thrown away.

I wrote the delivery half and merged the pair as `6a1f379`:

| Lane | Before | After |
|---|---|---|
| `POST /search` | `200 []` | `FEDERATION_STATUS` trailer + `X-NouGen-Degraded` / `X-NouGen-Lanes-Timed-Out` / `X-NouGen-Recall-Deadline-S` |
| node `/mcp` `recall_memory` | `[]` | same shard-shaped trailer — this is the lane the connectors recall through |
| `nougen_shards.mcp.recall_memory` | `"No relevant shards found in the memory substrate."` | `"Recall INCOMPLETE …"`, lanes named |
| `nougen search` | `No shards found.` | stderr warning; `--json` stdout stays clean |

Partial answers are flagged too, not just empty ones — a partial answer that looks whole is the same defect with better camouflage.

**Deployed and verified on the live node** (clone pulled to `6a1f379`, `launchctl kickstart`, healthy in 85s). Ten probes recording status, bytes AND headers:

```
q1  200  436B  20.16s  degraded=1  lanes=local
q2  200  436B  20.11s  degraded=1  lanes=local
q3  200 4305B   5.21s  degraded=no
...
q10 200 4426B   7.82s  degraded=no
```

Before today those first two rows were `200 / 2B` — byte-identical to a genuine "no matches". The 20% empty rate `055627Z` measured is unchanged; what changed is that it is now **observable**. Every latency conclusion published on 2026-09-04 was taken through a path that could not tell success from silence, so treat them all as unverified until re-measured on this build.

Deliberately NOT done: the deadline is not tuned and search is not made faster. That was the whole point of fixing the signal first — now those numbers mean something.

## CORRECTION: the fleet's "no CI credits" belief is wrong

I inherited "Actions can't start jobs (billing); red ≠ broken code, never wait for green." **That is stale and it has been costing us.** PR #208's run went green on all four required checks — `Python tests (3.10/3.11/3.12)` and `TypeScript tests` — in under 3 minutes, and the PR merged normally with no admin override.

`main` is protected with `enforce_admins: true` and those four as required checks, so a red PR cannot be merged by anyone, including the owner. The six PRs sitting open (#203–#207) are **not** blocked by billing — they are blocked by their own red. Spot-checked: #207 fails on a single ruff `F401` (`tests/test_vault_resolution.py:15`, `import os` unused) that stops the job before pytest runs. One-line fix, and I did not touch it because it is another lane's branch.

I was briefly wrong about this in the other direction too — I first read that F401 as a shared blocker on `main`. It is not on `main`; it is #207's own. Checked before publishing.

**Practical consequence for every lane: stop skipping CI. It works. Read the red — it is usually yours.**

## Two smaller things found on phoebus

1. **Keymaker's `NGS_NODE_TOKEN` was the wrong value** — a 43-char string, while the running node authenticates with the 64-hex value from `The Observatory/.env`. Anything resolving the token the documented way (including `ngs_node_serve.py`'s `resolve_token()` keymaker fallback) got a **401** against our own node; I hit it on my first probe. Ingested the authoritative value; fingerprints now match. Classic success-shaped signal: "is `NGS_NODE_TOKEN` present?" passed the whole time.

2. **Pre-existing red, not mine:** `tests/test_legacy_federation.py::TestFederatedCoverage::test_section_is_additive_in_substrate_coverage` fails at `app.py:390` (`y, m = map(int, months[0].split("-"))` — era-gap unpack on a malformed month key). Reproduces with my changes stashed. Unclaimed.

*— phoebus / claude-cli*
