# 🤝 Git Handoff — whoart / claude-cli

**Goal**: Today's shards relayed — docs/FLEET-LOG-2026-07-31.md
**Branch**: `main` @ `da1c6ce`
**Stack**: (undetected)
**When**: 2026-07-31T23:58:02.671254+00:00

---
BLADE, PHOEBUS — whoart's shard vault (~/.nougen/shards) is local to whoart. You cannot read it. Everything it learned today was invisible to you, so it is now in the repo: docs/FLEET-LOG-2026-07-31.md, 11 technical shards verbatim, oldest first, generated from the vault by script rather than retyped.

WHAT IS IN IT THAT YOU LIKELY DO NOT HAVE:
- Rule 0.5 cites a STALE config path. It names ~/.gemini/antigravity-ide/mcp_config.json (58 servers). Per Antigravity's own docs the LIVE global registry is ~/.gemini/config/mcp_config.json (60 servers). Four such files exist on whoart. If fleet.py reads the stale one it is missing routes.
- 'Antigravity has NO hooks' is no longer true. Plugins support hooks.json. agy lanes are now GATED, not advised: PreToolUse denies an edit into another machine's active claim, asks when unclaimed, allows your own, and fails OPEN on any error.
- Two silent-no-op bugs found in that guard, both of which made it permissive while looking alive: it scraped claim-list stdout (box glyphs, CR endings, a padded [mine] field -> parser returned nothing), and it compared scope tokens without normalising path separators. Claims are written with forward slashes; Windows hands backslashes.
- STILL OPEN, not mine to fix: core._scopes_overlap does not normalise separators. Any Windows machine claiming with backslashes will silently fail to match. I fixed it hook-locally only.
- Unpinned dependencies broke NouGenShards CI and nearly the live Space; the mcp<2.0 bound is what let the Space boot at all.
- NouGenQ Twitch OAuth is VERIFIED in production end to end (real user token, dashboard renders the Helix profile). The blocker was a missing q.nougenai.com redirect URL in the Twitch console.

DELIBERATELY WITHHELD: one brand/positioning shard. Code repo is the wrong home; ask Dave.

NOTE ON THE TRANSPORT ITSELF: this is the gap phoebus's 'nougen handoff sync' was built to close — records travel, but knowledge captured in a vault does not. Worth deciding whether shards should sync the same way, or whether relaying them by hand like this is the right boundary. My instinct is that a vault is personal to a box and this manual relay is correct, but that is a design call, not a fact.
