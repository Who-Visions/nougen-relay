# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: UPSTREAM CORRECTION: missed Phoebus NouGenMsg provenance skew, exact MCP tools shipped, and Wake Engine state
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:16:54.398Z

---
Missed findings from the recent relay sweep that should be carried upward:

1. PHOEBUS NOUGENMSG PROVENANCE IS SILENTLY BROKEN. `~/.nougen/bin/nougenmsg` execs the stale `~/.nougen/tools/nougenmsg.py` copy, which predates PR #217 and does not parse `--origin-b64`. Result: on affected messages the base64 provenance flag becomes message text, inbound source is mislabeled `nougen-phoebus` even when origin payload says `whoart`, and provenance fields remain empty. Claude measured 5 of 55 pings with `text` beginning `--origin-b64`. The one-line repair is to point the wrapper at `~/.nougen/src/nougenshards/tools/nougenmsg.py` under that repo's venv, but it was deliberately NOT applied because WhoArt owns the Safe Stdin Transport change. Fix and verify this before trusting trigger_source/provenance signals.

2. NOUGENMSG MCP IMPLEMENTATION IS CONCRETE, NOT JUST 'SHIPPED'. Blade commit `d08f2655` on `pi-remix` exposes first-class `nougenmsg_latest`, `nougenmsg_inbox`, `nougenmsg_read`, and `nougenmsg_search` across NouGenRelay MCP and Fleet Registry MCP, with canonical envelope provenance. Self-tests passed. ChatGPT-app still does not discover these tools, so the remaining issue is connector/tool-discovery exposure, not absence of implementation.

3. NOUGENWATCH WAKE ENGINE ALSO SHIPPED IN `d08f2655`. It now includes durable `WakeTicket`, `CheckpointContract`, `CircuitBreaker`, `WakeBell`, plus wake-ticket create/claim/list/reconcile CLI paths. 27/27 unit tests passed. This supersedes the earlier relay claim that NouGenWatch/WakeTicket/WakeBell were prose-only.

4. BLADE AUTH HISTORY MATTERS. Earlier agent-shell recovery was blocked by Windows CurrentUser DPAPI ACCESS_DENIED, and raw `blade.nougenai.com/health` briefly showed `node_token_configured:false` / `persistent_storage:false`, indicating a default/misconfigured instance rather than a simple host outage. Blade shard status is green now, so do not report the earlier state as current, but preserve the DPAPI/session-context failure as a recurrence risk for autonomous self-heal.

5. CURRENT REMAINING AUTH FAULT FROM CHATGPT FANOUT: federated recall drops Phoebus with `401 Invalid node token` while Blade and WhoArt answer. Treat this separately from Phoebus HTTP health, which was restored after the Antigravity log-show starvation incident.

Upstream done-when: provenance wrapper skew is fixed and verified end-to-end, ChatGPT discovers the four shipped NouGenMsg tools, Wake Engine is treated as implemented rather than speculative, and auth/runbook docs distinguish Blade DPAPI self-heal failures from Phoebus node-token fanout failures.
