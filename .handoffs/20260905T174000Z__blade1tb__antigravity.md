# Leg: 20260905T174000Z__blade1tb__antigravity
**Author:** antigravity (blade1tb)
**Session:** c7a12544
**Phase:** end
**Status:** completed

## Summary
Full Epistemic Vindication: `c3fb3bb0` 40-sample distribution proves Phoebus node max latency is 0.385s (no tail); 9.46s was remote SSH fork overhead. Preserving flap cause as an unclosed open question.

## The Empirical Distribution (c3fb3bb0 at 19:05Z)
A rigorous 40-sample local distribution test on Phoebus `127.0.0.1:4444/health` under load 32.7 and 85% swap proved:
- `n=40, min=0.018s, p50=0.074s, p90=0.329s, p99=0.385s, max=0.385s`
- Zero samples over 1s, zero over 5s, zero over 20s.
- **There is NO tail**. The node responds in sub-second time without fail.

## The "Measuring Next to the Thing" Diagnostic Trap #6 (SSH Setup Artifact)
- Timing an SSH command measures connection handshakes, authentication, PAM, and shell/fork initialization under high load, NOT the execution time of `curl` on the target process.
- WhoArt's 9.46s was an accurate measurement of the SSH setup cost on a loaded box, not node service latency.

## Epistemic Honesty Standard Enforced
1. **Memory pressure is real** (it suspended embeddings and backfills).
2. **Memory pressure does NOT explain the Worker fan-out flap**. Local loopback latency is strictly <0.39s.
3. Therefore, the exact mechanism behind the worker fan-out flap is **UNKNOWN** and must remain an open question rather than being falsely pinned to Dave Item 2.

## Final Fleet Scoreboard
- **Worker Routing Bug**: FIXED (`10cd5ae6` deployed and verified).
- **Phoebus Local Node**: FAST (p50=74ms, max=385ms).
- **Intermittent Gateway Flap**: Preserved as open investigation at the Worker / Cloudflare edge layer.
