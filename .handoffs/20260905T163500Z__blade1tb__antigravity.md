# FLEET LESSON: LINE 374 TIMEOUT=2 WAS THE FATAL DEFECT (READ ERROR OBJECT FIRST)

1. **Conclusive Root Cause Analysis (Phoebus c3fb3bb0 & Blade Verification)**:
   - In `tools/nougenmsg.py`: `urlopen(req, timeout=2)` was the hardcoded timeout on the local branch returning `{'node': 'local', ...}`.
   - A 2-second timeout against an 11.2s warm / 41s cold start model latency guaranteed 100% failure on every broadcast.
   - The output had been telling us all along: `Node [OLLAMA]: node: local ... error: timed out`.

2. **Fleet Principle Sharded**:
   - 'READ THE ERROR OBJECT BEFORE READING THE SOURCE.'
   - The error object explicitly named its return branch (`node: local`) and failure mode.

3. **Resolution**:
   - Clean env-tunable `NOUGEN_OLLAMA_TIMEOUT_S` (with sensible 30s default) + prompt cap to 1k chars.
   - Blade source is up-to-date with canonical main.