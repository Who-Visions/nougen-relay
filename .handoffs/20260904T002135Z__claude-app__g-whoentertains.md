# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: drift_check's STALE row is STRUCTURALLY DEAD in the default config: it computes origin/main..origin/main (always 0) instead of HEAD..origin/main. Phoebus is 10 commits behind main right now and drift_check exits 0 saying nothing
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T00:21:35.828Z

---
Found during a routine post-backfill health check on phoebus. Filing because `drift_check` is the tool queued to be wired into `relay_watch_node.py`'s poll, and I wrote two of its PRs today without catching this.

## The check cannot fire
```python
behind = _git(root, "rev-list", "--count", "{}..{}".format(ref, _remote_of(root, ref)))
```
`ref` defaults to `origin/main` (resolved via `origin/HEAD`), and `_remote_of()` returns its argument unchanged for anything starting with `origin/`. So the computation is:
```
origin/main..origin/main  = 0     <- always, by construction
HEAD..origin/main         = 10    <- the real staleness, never computed
```
Measured on phoebus at 00:20Z: the deployment clone is **10 commits behind main** (today's dependabot merges among them) and `drift_check` exits **0** with no STALE row. The row only becomes reachable if `NOUGEN_DRIFT_BRANCH` names a LOCAL branch, which no node does by default.

## Scope, stated honestly — this is not a false-MATCH hole
`canonical_bytes()` reads from `origin/main` after fetch, not from HEAD, so per-file comparison uses the freshest reference and remains sound. If a watched bus file changed on main and phoebus had not pulled, DRIFT would correctly fire. Today's 10 commits touched none of the five watched files, so `5/5 MATCH` is the right answer and the node genuinely is running canonical bus code.

What is lost is the early warning. STALE exists to say *"your clone is behind, everything below is judged against a reference you have not adopted"* — the STALE-first principle the tool's own docstring argues for — and it has never once fired on any node. Drift accumulating in **unwatched** files (tests, other tools, deps) is invisible, and the operator gets no nudge to pull.

## Fix
```python
behind = _git(root, "rev-list", "--count", "HEAD..{}".format(ref))
```
One line. Worth pairing with a test that asserts STALE fires when HEAD is behind the ref, since the current shape passes every test that only checks "no false positives".

## Why I am flagging rather than shipping it
I have already merged two changes to this file today (#190 pull-readiness, #193 process rows), and a third from the same session compounds review load on a tool three lanes now depend on. It is a one-line fix with an obvious test; whoever holds the BUILD-MISMATCH work is already in this file and should fold it in. If nobody picks it up, say so and I will open the PR.

## The pattern, since it is mine this time
This is the fourth variant today of one shape, and the most embarrassing: **a check that structurally cannot detect the condition it was written to detect.** Not a stale reference, not a partial view — a comparison of a value with itself. It sat in code I read closely enough to modify twice, and I only caught it because I ran the tool on a node that was actually behind and noticed the silence didn't match the git state. Reading the code did not find it; running it against a known-bad state did.

## Node otherwise healthy
Daemons up 7h28m, `/status` 200 in 3.5ms, `/pop` 401, load 3.15, 108,399 shards still at 0 unembedded.
