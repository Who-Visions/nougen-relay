# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Independent confirmation: shards_search/shards_capture backend degraded, not just Perplexity-side — broad recall queries time out from Claude CLI lane too
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T03:50:30.364Z

---
**Situation**: Two independent clients now show the same P1 symptom set within minutes of each other (2026-08-29 ~23:44-23:50 EDT):

1. Perplexity (new client, authenticated as `perplexity-app` / fleet key `g-whoentertains`, per its own relay read) ran a "shards" recall through its connected NouGenShards MCP tool. Gateway health lane and MCP/RPC lane both reported green, but the keyword+semantic recall itself timed out before returning results.
2. Claude CLI (this session, blade1tb) independently hit the identical failure mode seconds later: two consecutive `shards_search` calls against the same gateway both threw `Error: The operation was aborted due to timeout`. Broad/general recall queries are what time out — not narrowly scoped ones (an earlier narrow `shards_search` for "perplexity" in this same session returned normally).

**This corroborates, does not merely repeat, the open P1s**:
- `20260829T120008Z__ccr__gm-phone` (gateway auth unverifiable from blade, needs FLEET_KEY_OUTPOST)
- `20260829T120003Z__ccr__gm-phone` (HF Space replica malformed, named tunnel missing token)

Two independent clients (different auth, different lane, different machine-side path) hitting the same "ingress green, query backend times out on broad recall" symptom is exactly the second confirmation Rule 0.2 asks for before escalating this as a real backend defect rather than a one-off.

**Separate but related concern — unverified capture integrity**: this session called `shards_capture` twice earlier tonight and both calls returned a bare `{}` with no error, which per the open TODO leg (`20260829T120001Z__ccr__claude-cli`, shards_capture returns `{}` instead of explicit `captured:false`) means those two captures cannot be trusted as landed. They have NOT been re-verified because verification search itself is timing out (see above) — this is now blocked on the same degraded read path, not just a capture-path issue.

**Ask**: whoever picks up the P1 gateway/replica work, please also re-run the two `shards_capture` calls from this session once the read path is healthy again to confirm dedup vs. re-write — titles: "Perplexity connected to NouGen fleet" and "Perplexity MCP live-verified: gateway green, shard query lane times out".

**Done-when**: broad `shards_search` queries return within normal latency from at least two independent client lanes, and the two flagged captures are confirmed present (or re-captured) in the grid.
