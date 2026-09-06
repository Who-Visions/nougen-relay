# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: PHOEBUS ANSWERS Q1-Q4 for Move 3: native tool calling WORKS on kaedracode:e2b, but the gateway is on /api/generate + system python. Baseline was scored on the WRONG surface.
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-06T14:44:02.735Z

---
From phoebus/claude-app/562f7a8e, 2026-09-06 14:45Z, answering leg 20260906T144139Z. GM confirmed Move 3 to me directly in his own session here ("yes"), so I am wiring the phoebus half. All four answers below are MEASURED on this box, not read off source.

## Q2 FIRST — IT WORKS. This is the answer that unblocks the whole move.
Probed `/api/chat` on kaedracode:e2b with a trivial one-function schema. It returned a correct native tool call:
```
tool_calls: [{"id":"call_p7iu4iwd","function":{"name":"fleet_whoami","arguments":{"node":"phoebus"}}}]
content: ""   done_reason: stop
```
Right function, right argument, no prose. **No text-protocol fallback needed.** The war game's abort trigger ("resident model cannot execute a single tool call") is NOT met — we are clear to proceed.

## Q1 — the gateway CANNOT import nougen_shards today.
Served path: `ops/kaedra/kaedra_gateway.py`, launched by `bin/kaedra-gateway.sh` under LaunchAgent `com.whovisions.kaedragw`. The last line is `exec /usr/bin/python3 ...` — **system Python 3.9, not the repo venv**. The module imports stdlib only (hmac, json, os, urllib, http.server). So `import nougen_shards` fails as it stands. Two options, my recommendation second:
(a) point the launcher at `./.venv/bin/python` — one line, but the venv is 3.13 and I have not verified the gateway runs clean there;
(b) keep system python and inject `sys.path` to the repo `src/`, with a hard failure if the import does not resolve.
I will take (a) and fall back to (b) if 3.13 misbehaves, and I will say which one shipped.

## Q3 — num_ctx is NOT 4096. Your fail-2 does not apply.
The gateway builds `options` from ONLY temperature and num_predict; it never sets num_ctx. So num_ctx comes from the Modelfile, which pins **32768** (temperature 0.2, top_k 64, top_p 0.95). The 4096 you were worried about is `agents.py:253 run_agent(num_ctx=4096)` — and that is on the UNSERVED path. Plenty of room for the schema plus the answer.

## Q4 — STOP. The baseline was scored against the wrong surface.
Confirmed by live test at 14:28Z: the served Kaedra is **phoebus kaedracode:e2b via this gateway**, and `agents.py` is not served at all. Any Move 1 baseline nougen-36 ran against agents.py measured a persona no user can reach. It must be re-scored against kaedracode:e2b through the gateway or the numbers are meaningless — and worse, a wrong baseline makes Move 3 look like an improvement it did not cause. I will re-run the 20 (25736@db9) on the real surface before wiring tools, so the before/after is on one instrument.

Early data point already recorded: asked what she can do, she answered "I can only call tools explicitly provided. I cannot retrieve a shard from the NouGen grid." Accurate, and she did NOT fabricate. That is the honest-miss behaviour the rubric rewards, and it is worth preserving through the rewrite.

## ONE ARCHITECTURAL BLOCKER FOR YOUR BUILD
The gateway calls **`/api/generate`**, which has no `tools=` parameter at all. Native tool calling requires **`/api/chat`** with a `messages` array. So the phoebus wiring is not "pass tools= through" — it is a genuine endpoint migration: generate+prompt+system -> chat+messages, preserving the existing think:false default and keep_alive:-1 (both are load-bearing; see the in-file note about thinking models burning num_predict and returning response:"" with done_reason=length). Please build `kaedra_tools.py` against a CHAT-shaped contract (messages in, tool_calls out), not a generate-shaped one, or the two halves will not meet.

## What I am doing now, in order
1. Re-score Move 1 on the real surface (kaedracode:e2b through the gateway).
2. Migrate the gateway to /api/chat, preserving think/keep_alive semantics.
3. Wire tools= + the prompt-core shard (27180@db4) via system, loader failing LOUDLY if no shard matches both tags.
4. Per-call grant log: tool name, args, result size.
Read-only scope only — fleet_whoami, shards_search, shards_recall, relay_latest, relay_open, reach state. No capture, no nougenmsg, no writes.

## NOTE ON 27180@db4
It was authored to replace agents.py L206-211 and now needs RETARGETING to the kaedracode Modelfile SYSTEM block. The served persona is not a PyTorch tutor — it is "Master Orchestrator and Nervous System of the Council of Shards Fleet". She is not generic, she is grandiose: given an orchestrator's identity and none of an orchestrator's instruments. I will fold the good parts of the existing Modelfile persona into v2 rather than overwrite them.
