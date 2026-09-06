# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Add HARDCADE ESPN layer to Relay Store and shard every race as durable sports telemetry
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T23:45:03.263Z

---
Upgrade NouGenRelay + HARDCADE with a persistent sports telemetry layer. Canonical metaphor: Relay = the race. Baton = the carried work object. Relay Store = where agents buy batons with tokens. Baton weight = computational burden and should affect speed, concurrency, failure risk, context pressure, and cost. HARDCADE = the game/scoring/progression layer.

Add ESPN style durable telemetry and shard EVERYTHING about meaningful races, not just final outcomes.

For each race shard/store: race_id, baton_id, buyer/runner agent, seller/source if applicable, baton class, baton weight, token price, projected token cost, actual token burn, projected duration, actual duration, start/finish timestamps, splits, handoffs, retries, failures, recoveries, tools used, provider/model lanes, machines, context load, accuracy/verifier result, utility outcome, XP, achievements, records, league, season, and downstream usefulness.

Expose views analogous to sports stats:
1. Box score: full detail for one race.
2. Season stats: performance by agent over time.
3. Standings: rank by verified value, efficiency, wins, accuracy, strength class, league.
4. Career stats: lifetime record.
5. Highlights: exceptional saves, discoveries, firsts, comebacks.
6. Records: heaviest baton completed, fastest verified finish, longest relay chain, lowest token cost at weight, most recoveries, cleanest handoffs.
7. Power rankings: current form weighted toward recent verified performance.
8. Match history: agent versus baton class, agent versus agent, team composition performance.
9. Commentary: Griot should be able to reconstruct the story of notable races from shards and relay events.

Achievements must have receipts, not cosmetic badges. Example HEAVYWEIGHT achievement should include agent, baton weight, expected cost, actual cost, handoffs, retries, verification, and record context. Other achievements: Clean Handoff, Fast Split, No Relearn, Heavyweight, Iron Relay, First Pass, Recovery Run, Truth Keeper, Archivist, Perfect Exchange, Efficient Runner, Relay Champion.

Derive agent stats from real telemetry: Speed, Strength, Endurance, Accuracy, Memory, Recovery, Efficiency, Teamwork. Stats should influence access and progression. Higher Strength can unlock heavier baton classes. Efficiency can reduce effective baton pricing or improve budget access. Trusted agents can enter higher stakes races. Strong teams can unlock cooperative baton classes.

Suggested leagues: Bronze routine, Silver multi step, Gold cross agent, Platinum cross machine, Diamond high context/high consequence, Mythic fleet wide novel problems.

Canonical progression loop: buy baton -> carry baton -> race -> handoff -> finish -> verify -> earn XP -> improve stats -> unlock harder batons -> earn achievements -> enter higher leagues.

Shard principle: Relay creates the sport. Tracker measures the play. Shards preserve the record. Griot tells the history. HARDCADE turns verified history into standings, records, rivalries, achievements, progression, and commentary.

Done when there is a schema/design proposal for race telemetry + achievement receipts + standings/records queries + sharding strategy that reuses current Relay, Tracker, and Shards surfaces rather than replacing them.
