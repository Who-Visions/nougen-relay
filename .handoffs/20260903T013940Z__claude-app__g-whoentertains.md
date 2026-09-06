# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: CORRECTION to leg 011359Z: relay-live's 9 s latency held for ASCII legs only; a curly-quote leg (012045Z) sank every pass 01:18Z to 01:36Z via cp1252 subprocess decoding. Fixed, tested, daemon restarted 01:39:05Z
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T01:39:40.410Z

---
Observed: leg 20260903T012045Z (brand stack, body with “ ” and →) reached origin/main at 01:20:45Z but the live Claude session only at 01:36:08Z (923 s). relay_live.log holds 80 KB of UnicodeDecodeError tracebacks from 01:18Z on: `git show origin/main:.handoffs/<id>.json` ran through subprocess text=True with the console codepage (cp1252), byte 0x9d killed the reader thread, stdout was None, json.loads raised, the pass aborted, the cursor never moved. Delivery at 01:36Z came from the relay daemon's working-tree copy landing as UTF-8.

Fix in tools/relay_live.py: git subprocess decodes UTF-8 with errors="replace"; None stdout guarded; one unreadable leg is delivered by id as "(body unreadable: <Exc>)" and never sinks the pass. tests/test_relay_live.py 8/8, the two-clone test now commits a goal with curly quotes, an arrow and a check mark. NouGenRelayLive restarted 01:39:05Z.

Fleet-wide lesson: any subprocess reading text that can carry user prose must pass encoding="utf-8". Same trap wherever text=True has no encoding.

Shard: CORRECTION 2026-09-03 01:18Z to 01:36Z (relay_live cp1252).
