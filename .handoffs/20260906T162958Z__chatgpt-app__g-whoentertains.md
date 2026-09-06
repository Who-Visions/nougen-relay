# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: CANONIZE NouGenPulse: fleet liveness and wake execution layer
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T16:29:58.188Z

---
Name the persistent liveness/orchestration layer **NouGenPulse**. Definition: the mechanism that keeps coding agents available between direct user interactions by receiving inbound relay signals, waking an eligible worker, forcing claim before execution, producing evidence, enforcing quota policy, and rearming for the next signal. Canon loop: `pulse -> wake -> claim -> execute -> verify -> rearm`. Pulse is not the relay itself and not the model/provider. Relay carries durable work; Pulse is the liveness/execution rhythm that causes work to move through the fleet. Integrate this term into scheduler, wake-daemon, Tracker metrics, and architecture docs.
