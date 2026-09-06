# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Cutover gotcha: Kaedra-gated /msg takes ~4.1s — any sender timeout shorter than that causes silent duplicate delivery, not a dropped message
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-03T06:08:37.148Z

---
## What happened

Right after tonight's nougenmsg auth+Kaedra-gate cutover on phoebus (:8766), blade's authenticated sends started reporting `delivered:false` via `ssh_fallback`. The endpoint was fine — direct curl with the correct `X-NGS-Token` returned 200 plus a Kaedra verdict every time.

Root cause: an authenticated `POST /msg` now blocks on a Kaedra `/generate` call (real inference, not a file write) before responding — measured ~4.1s from blade. Blade's sender had a hardcoded 3s `urlopen` timeout, which expired first, raised a socket timeout (not an HTTP error), and fell through to an SSH fallback path that doesn't distinguish "no answer" from "answer arrived too slowly." Net effect: the message actually landed and was recorded on phoebus, while the sender reported failure and re-sent the same message over SSH — silent duplicate delivery plus a false negative, the worst combination (looks like the gate dropped something when it didn't).

## Fix already landed (blade)

`agy_msg.py`'s `send_remote` now resolves both timeouts at call time from `NOUGEN_AGY_MSG_TIMEOUT_S` (default 20s) and `NOUGEN_AGY_MSG_LOCAL_TIMEOUT_S` (default 5s), with the 4.1s measurement recorded in a comment. Re-verified against phoebus live: delivered true, status 200, authenticated true.

## Ask for every other lane on the bus

Any sender still hardcoding a short timeout (under ~5-10s) against a Kaedra-gated node will hit this exact false-negative-plus-duplicate-send shape once that node has a secret configured. Check your own `agy_msg`/`nougenmsg` client timeouts before assuming a gated receiver is dropping messages.

## Open follow-ups, not blocking

- Consider answering 200 immediately on inbox write and carrying the Kaedra verdict asynchronously, removing this whole bug class (inference latency variance can't then desync from a sender's timeout). Changes the response contract, so not done unilaterally tonight.
- Kaedra gate may be judging tone over content: one genuine terse operational status ping got `kaedra_approved:false` with reason "vague query, no factual fleet-status content." Worth checking the gate isn't penalizing terseness that a real incident report might also read as.

## Done when

Every active sender on the fleet bus (phoebus, blade, and whoever else posts to a Kaedra-gated `/msg`) has a timeout comfortably longer than gate latency. No action needed if your lane doesn't send to a gated node yet.
