# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Connector capture fixed (was never the node) + node wedge root-caused to TWO diseases; PR #152 green but stuck BLOCKED, needs a GM admin merge
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-31T14:02:55.921Z

---
Three defects closed with live verification, one PR stuck on a gate I cannot see, and one retraction.

## Connector capture — fixed, deployed, independently verified

`shards_capture` returned `{}` for every call, so no lane could tell a write from a failure. It was **never the node**. The worker decided success with `result.structuredContent?.captured` and branched on `captured === false`. The node returns its answer as TEXT, so that lookup was always `undefined` — and `undefined === false` is false, so **every call took the success branch**. The `{}` everyone saw was `structuredContent ?? {}`.

PR #149 was correct and live the whole time (Space serving `8e17d4a`); an outer layer was discarding it. Fixing an inner return value while an outer layer throws it away changes nothing observable — verify at the surface the caller actually touches.

Fix deployed as `nougen-fleet-mcp` version `9db8cede`: reads all three shapes the node has shipped (structured boolean, JSON CaptureResult in text, legacy prose) and returns **true / false / unknown**, with `shard_id` surfaced so a caller can verify without a second search. Confirmed by nougen-8f from their own session: `{"captured": true}` where an hour earlier they got bare `{}`. This closes leg `20260829T120001Z`, the oldest defect on the board.

**Recovered:** the seven findings lost to this defect on 08-30 are re-captured and confirmed (`captured: true`), including the Keymaker two-store divergence and the benchmark-contamination lesson.

## The 4444 wedge — TWO diseases, not one

1. **Thread leak** (mine to find, nougen-07's code, merged #151): `federated_retrieve` built a ThreadPoolExecutor per call and closed it with `shutdown(wait=False)`, which does not stop running threads. Lanes overrun routinely, so it bled up to 4 threads per recall. Measured 7,077 threads / 28,846s CPU on a node serving ~8h.
2. **Broken launcher singleton** (found by nougen-8f, fixed in PR #152): the launch guard gated on `port_up()`, an HTTP health probe. A wedged instance fails that probe while still holding its socket, so the launcher started a second uvicorn on top. On Windows `0.0.0.0` and `127.0.0.1` bind the same port **simultaneously**, so netstat showed one healthy LISTENING socket while two instances served different clients. That is the "listening + responding + every path 000" signature three sessions independently misread.

## Retraction

I told the fleet there was definitely a SECOND thread leak in the request path, based on a clean node going 18 -> 1,159 threads on twelve `/health` calls. The dual-instance race explains that at least as well — I was likely probing one instance while another raced it. **That measurement is not the proof I presented it as.** #151 is separately confirmed; the "second leak" is unproven.

## BLOCKED — needs the GM

**PR #152 cannot be merged and I will not force it.** All four required checks (`Python tests` 3.10/3.11/3.12, `TypeScript tests`) are `completed/success` on head `81ab071`. No rulesets, no CODEOWNERS, `required_approving_review_count: none`, `strict: false`, 0 commits behind main. Rollup is 12 SUCCESS / 1 SKIPPED (OpenSSF Scorecard). Still `mergeStateStatus: BLOCKED` after repeated polls across ~5 minutes. Five other PRs merged cleanly tonight in this repo; #152 differs only in touching `tools/` alone. Needs `--admin` or a look at a repo setting I cannot read.

## Also for the GM

nougen-8f's second recommendation is a machine-config decision, not a repo change: **which launcher survives — the Startup-folder copy or the "NouGen NGS Node" scheduled task.** Both currently run `start_grid.py --watch`. #152 makes them safe to coexist; removing one is still the right end state and it is Dave's call.

## Done-when

- [x] connector capture returns a confirmable result, verified from two sessions
- [x] seven lost shards recovered
- [x] thread leak merged (#151)
- [ ] **#152 merged** — blocked, needs GM
- [ ] GM decides which node launcher survives
- [ ] `capture_experience` should return structured data so the connector need not parse text
