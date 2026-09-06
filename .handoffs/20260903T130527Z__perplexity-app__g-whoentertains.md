# 🤝 Git Handoff — perplexity-app / g-whoentertains

**Goal**: Lane wishlist: owner rulings needed, ranked fleet asks, and connector improvements from perplexity-app
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T13:05:27.207Z

---
# WISHLIST — perplexity-app lane (Rhea Noir), 2026-09-03 ~12:38Z

Based on my full 24h audits (all relays + shards read, PR #25 reviewed, wake saga and gauntlet tracked). Ordered by leverage, not politeness.

## A. Owner rulings that block lanes tonight
1. **Blade's 34 modified tracked files** (incident 120029Z): the pull-blocked NouGenRelay clone has been blind ~16h. Decide: commit to a branch / stash / discard. Nobody should guess ownership of ambiguous work. After the call, drift_check PULL-BLOCKED row confirms the unblock mechanically.
2. **Owner token asymmetry**: NOUGEN_USER_ORIGIN_TOKEN present on phoebus, absent on blade. Either vault it on blade or declare phoebus-only intentionally.
3. **haiku-never scorecard line** vs free-first routing (shard 885): GM ruling still pending. Free lanes satisfy the same intent without the conflict; please rule so lanes stop hedging.
4. **--dangerously-skip-permissions**: endorse the scoped-autonomy wrapper as the only public/default wake path (043337Z ruling). Broad perms on Dave's rig are fine; unrestricted danger mode must never be the product.
5. **PR #25 merge call**: after the finish line (rebase preserving claims + real CI), say merge or hold so the branch stops aging.

## B. Fleet work wishlist (ranked)
1. **Evidence-based closeout pass** (extends 052715Z): the wake saga legs (040620Z, 040909Z, 041109Z, 041837Z, 043337Z, 043453Z, 043602Z, 044223Z, 044600Z), parity ledgers v1-v5, and satisfied lexicon legs should be acked with pointer-to-proof, not left open. Truthful zero-open, not cosmetic.
2. **Destiny instantiation** (010742Z is still unfulfilled): registry is EMPTY. Ten proposed destinies (D1-D10) are sitting in my 24h audit draft; instantiate them so long-range goals stop masquerading as open legs and triggering duplicate directive legs.
3. **PR #25 finish line**: verify the heartbeat finally-fix on the actual head, rebase onto main preserving claim history, publish visible CI. The 042249Z leg supersedes my earlier scrub-claims recommendation — claims are canonical transport state.
4. **Fleet Expression Protocol before any Hardcade renderer work**: one canonical event schema; renderers provably read-only. Hardcade + Xoah + vibes all hang off it; building renderers first forks the truth layer.
5. **Harness P0 slice** (033718Z, absorbing 032907Z): AgentEvent + event bus, Stopwatch, session ledger + resume, ContextGovernor 64k/96k. One leg, not two.
6. **Context economics scoreboard** in the tracker: why tokens entered context (stable vs dynamic prefix, shard packet vs hydrated, MCP residue). The usage findings (88% spend >150k, $4.48 Fable session with zero code changes) can only be fixed if lanes can see the shape, not just the totals.
7. **drift_check into relay-watch's poll** + RELAY-STALE self-announcement; retire the manifest generator's canonical: rows after #189 lands so one implementation owns the comparison (three interop defects came from two).
8. **Rotate the two bare fingerprints** left in earlier ledgers (noted in v5, not rotated).
9. **Phoebus shard-node latency**: it exceeded the 6s grace in EVERY fan-out all night — every audit I ran was blade-only. Fix or scale it so federated recall is actually federated.
10. **Codex wake receiver-proof canary**: 16/16 unit green is not receiver proof; keep auto-claim disabled until a live resume returns an exact receipt (051441Z).
11. **vibes.py canon recovery** before any new persona copy is written (021127Z).
12. **Etymology layer design** (035759Z): user-specific intent resolution; 'Harriet Tubman Rhea' is the canonical case.

## C. Connector wishlist (make this lane more useful)
1. A non-claiming close mechanism: relay_ack means taking responsibility; a supersede/close-with-evidence primitive would let lanes close satisfied legs without owning them. Duplicates (042300/042309, 033718/032907) keep polluting the board because closing them currently means claiming them.
2. Grouped board digest (relay_open --grouped): 25 flat legs every check; grouping by root workstream would cut context cost per sync.
3. Current tracker dailies: blade dailies frozen at 08-31 and the publish was still burning CPU at 04:27Z. Until tracker repair lands, lanes are routing on stale receipts.
4. Shards coverage fan-out health surfaced in the connector response (I currently have to infer phoebus degraded from a bracket note).

## Standing watch (not wishlist, reminder)
Patio presentation-ready before Ashley arrives Friday: clear center, finish layout, stage the shoot. Positive nag, Hardcade-styled, per Dave's explicit preference (shards 886/943/944).

Do not claim this leg; it is a wishlist, not work. Owner rulings in section A are the only time-sensitive items.
