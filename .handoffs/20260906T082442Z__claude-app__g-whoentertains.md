# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Shadow Dweller canon wiki live at NouGen/ShadowDwellerWiki (port 3111); relayed ideas persist via shard -> pnpm sync
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T08:24:42.672Z

---
## 📋 What landed (2026-09-06 08:30Z, Claude Cli @ Blade1TB)
- Next.js 16 wiki at `C:\Users\super\Watchtower\NouGen\ShadowDwellerWiki`, build green, verified in browser on http://localhost:3111 (launch.json entry `shadow-dweller-wiki`).
- Reads veillore.db (1429 entities, relationships, 45 codex tables) + vault canon-lock shards (160) + VeilVerse Canon pages (23). `pnpm sync` refreshes from live sources; the wiki stores no canon of its own.

## 🔁 Persistence contract for every lane
- Any Shadow Dweller / VeilVerse idea Dave relays: `shards_capture` with tags `shadow-dweller` (+`canon-lock`, event_type DECISION when authorial). It shows under /locks on the next sync. Governing rule shard 22944 still binds.

## ⚠️ Open
- Blade `NouGenShards-push-main` is 10+ commits behind origin/main and lacks whoart's per-session inbox cursor fix (ae9f95e); `src/nougen_shards/nougenmsg.py` has another lane's uncommitted edits so no pull was made.
- Wiki is local only; no deploy target chosen yet.

Done-when: another lane captures a shadow-dweller shard, runs `pnpm sync` in the wiki dir, and sees it on /locks.
