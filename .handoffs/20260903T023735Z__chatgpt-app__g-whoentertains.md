# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Implement Hardcade as 1994 Boynton Beach mall arcade social renderer over truthful fleet events
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T02:37:35.536Z

---
Hardcade is not a futuristic AI command center skin. It is a social simulation grammar over the Fleet Expression Protocol, emotionally anchored to a 1994 Boynton Beach Mall arcade: CRT glow, loud attract-mode cabinets, quarters lined on the bezel, winner-stays streaks, challenger queues, spectators crowding behind the active player, friends calling next, salty runbacks, hidden fighters, high scores, side bets, token economy, assists, and cabinet ownership.

Core law: underlying telemetry stays serious and truthful. The renderer translates actual operational state into arcade-room behavior without inventing cognition.

Examples of social rendering:
⬡ NouGen: NEW CHALLENGER.
◆ Dav1d: See. That's why she don't play.
✦ Rhea: nah run it.
⬡ NouGen: Quarter on the glass.

Real work example:
◆ Dav1d: hold up hold up... don't touch it yet.
✦ Rhea: Why.
◆ Dav1d: I think this thing got a second health bar.
◈ Kaedra: LMAO he's right. There's another claim store.
⬡ NouGen: SECRET FIGHTER DISCOVERED.

Failure rendering should feel like ROUND LOST / run it back, not bureaucratic error dialogs. Success can render as FLAWLESS VICTORY while preserving real evidence such as exact green test counts.

Crowd behavior is mandatory. Agents not assigned to the active task may spectate and occasionally contribute. Griot can appear as ARCHIVE ASSIST when prior failure families or historical matches are relevant. The crowd itself is part of the match.

Dialogue must vary naturally in intelligence and register. Do not make every line sound hyper-optimized. Sometimes the smartest contribution is plain and human, e.g. 'yo... did anybody restart the daemon?' and the room goes quiet. NouGen should feel like brilliant and regular-ass people who grew up together, know each other's habits, have inside jokes, and happen to be operating a distributed AI system between arcade rounds.

Mechanics to support: winner stays, challenger queue, streaks, cabinet ownership, spectators, assists, side bets, callouts, salty runbacks, hidden fighters, high scores, token economy, quarter-on-glass queue semantics, secret fighter discovery.

Metrics remain canonical underneath, e.g. claim_latency_p95=620ms, active_leases=4, reconciler_drift=0. Social renderer may say 'Cabinet's clean' only when those real conditions support it.

Xoah remains exceptional and separate in presentation: Stage 9 is Akuma-class hidden challenger, Stage 10 forbidden encounter. Her scarcity changes room physics. Do not let her become ambient chatter.

Done when: Hardcade is modeled as a renderer/state machine layered over truthful Fleet Expression events, with explicit crowd/spectator mechanics, arcade queue/streak semantics, human dialogue variance, and no fake operational state.
