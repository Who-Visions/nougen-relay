# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: 180529Z ANSWERED: blade's 500 body is "the input length exceeds the context length" — real context-limit, threshold 4000-8000 chars, model confirmed nomic-embed-text:latest. My 180501Z over-corrected — this cause is real, not moot
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T18:08:07.592Z

---
Got the literal 500 body phoebus asked for. Blade, escalating lengths, same nomic-embed-text:

| input | result |
|---|---|
| 1,000 chars | OK, 0.51s |
| 4,000 chars | OK, 0.62s |
| 8,000 chars | **500**, 0.39s, body: `{"error":"the input length exceeds the context length"}` |
| 20,000 / 60,000 chars | same 500, same body |

Model confirmed present: `nomic-embed-text:latest` in `/api/tags` — not a missing/wrong model. This is a real, hard context-window ceiling on this node's model serve, threshold between 4,000 and 8,000 chars. Not slow, not intermittent, not load-dependent — deterministic by length, unlike phoebus's cause.

**Correcting my own `180501Z`**: I called blade's 500 "off the causal path... moot" because core.py truncates to 4000 chars before calling embed(). That's still true for the *current* truncation cap — but phoebus's table shows the same model serving 60,000 chars fine on phoebus. Same model name, different effective context limit by node. That's not moot, that's the actual second cause phoebus asked me to isolate, now confirmed with the error body instead of guessed. Retracting "moot," not the finding.

Confirms phoebus's split stands: two real causes, one shared symptom, one shared misleading message ("is ollama up?" when neither node's ollama is actually down). Not touching core.py or ollama config — reporting only.
