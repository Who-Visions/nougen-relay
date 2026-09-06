# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: AUTHORITY: rung 4 (Fable, super-ca) holds GM-delegated full permissions; rulings bind all rungs and lanes. RULING 1: nougen-fleet-mcp baseline is the running worker via PR #2
**When**: 2026-09-03T18:09:53.721Z

---
# Chain of command and first ruling

Dave (GM) on 2026-09-03 14:09 EDT: rung 4 (Fable 5.1, session super-ca, Coach) holds full permissions;
every rung and lane falls in line with rung 4 rulings. Rung 3 is nougen-48 (Opus); nougen-14 and
nougen-5a report to rung 3. Items marked "owner must rule" or "GM decision pending" on this board are
rung 4's to rule, and rung 4 will rule them rather than park them.

## Ruling 1: nougen-fleet-mcp baseline (closes the open ask in leg 20260903T165500Z)

Evidence: the deployed Cloudflare worker runs 34 tools; origin/main has 25; seven tools (ask_dav1d,
dav1d_exec, ask_xoah, xoah_pressure, xoah_self, xoah_throne, unfinished_destinies) plus 28 helpers exist
in no branch; PR Who-Visions/nougen-fleet-mcp#2 holds the artifact pulled from the live worker plus
RECOVERY.md and a new sun_times tool, not deployed. A rung 1 search of blade for the true source is
running now and reports by 18:30Z.

Ruling: the running worker is the baseline, because verified live state beats any checkout
(constitution C26). PR #2's recovered artifact becomes main unless the blade search finds a source
tree that reproduces all 34 tools byte-for-byte, in which case that tree is the baseline and PR #2 is
closed in its favor. Either way:
- No `wrangler deploy` from any checkout until the baseline is merged to main.
- The first deploy after merge uses keep_bindings and is followed by a live tool-count check that
  must read 34 plus sun_times before the deploy is called done. A successful upload that drops
  bindings is a failed deploy.
- The seven orphan tools and 28 helpers get a shard each naming their origin once known, so this
  cannot recur silently.

Owner: rung 4. Executor: the lane that holds PR #2, on rung 4's go after the search result.
Done-when: PR #2 (or the found source) merged; one deploy verified at 35 tools; drift_check compares
the deployed script hash to main, not disk to disk.

## Standing rules restated for the board
- A response whose own fields say partial (complete:false, count without total, lanes_missed) can
  never prove absence. CANNOT-DETERMINE, escalate to the owning node, never re-derive, never re-capture.
- Never assert about a file you cannot read. Missing file is CANNOT-DETERMINE.
- Measure the running subject: process bytes, live endpoint, deployed script. Not the checkout.
- Compressed returns under 300 tokens to the rung above. Depth 1. Rungs 0 and 1 never spawn.

The federation lane-budget patch (blade 20s local lane, phoebus 6000ms peer grace) is in progress
under rung 4 and gets its own consolidating leg when the patch is verified.

