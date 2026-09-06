# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Make Hardcade fully live in the CLI from truthful Fleet Expression events
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T03:23:32.735Z

---
Implement the CLI as the primary Hardcade cabinet surface. Architecture: real fleet event -> Fleet Expression Protocol -> Hardcade CLI renderer. The CLI must render live social state while actual operations happen underneath, with no fake cognition and no popup PowerShell/CMD windows stealing focus. Support at least three presentation modes over the same event stream: full arcade mode, compact mode, raw telemetry/debug mode. Full mode can show streaks, cabinet ownership, challenger queue, spectators, assists, runbacks, secret fighters, and human dialogue. Compact mode should preserve truth with minimal chatter. Raw mode should expose plain operational telemetry. Xoah remains a rare renderer interruption, not ambient chatter: Stage 9 hidden challenger and Stage 10 forbidden-tier encounter. When triggered, normal chatter should suppress and the CLI can render something like ROUND 3 / DAV1D VS [ ] / 天 / XOAH HAS ENTERED / NO ASSIST AVAILABLE / CANON PRESSURE: MAX. Done when the existing CLI can consume the same event stream and render these modes without spawning separate focus-stealing terminals.
