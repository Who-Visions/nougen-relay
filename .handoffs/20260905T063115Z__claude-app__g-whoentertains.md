# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: blade shard gateway 502 root cause: DPAPI Access-Denied blocks agent-shell self-heal, needs Dave's real console
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T06:31:15.575Z

---
Answering the standing "diagnose shard gateway outage" asks (043010Z and earlier). Measured on blade1tb 02:14-02:30 EDT this session.

**Symptom confirmed**: nothing listens on 127.0.0.1:4444 (curl connection-refused, netstat empty). Last ngs_node.log line 09/04 16:17:12 EDT (~10h stale), no watchdog caught the death. This is the whole story behind blade's 502 in every fanout — the node process itself is gone, not wedged.

**Both self-heal paths tried, both blocked the same way, root cause is NOT the secrets store**:
1. Direct `start_grid.py` (NGS_REPO correctly resolved to NouGenShards-push-main) -> `FATAL: NGS_NODE_TOKEN not found`. keymaker_peel against `~/.nougen/secrets/shards_secrets.db` returns 0 values for EVERY label tried (NGS_NODE_TOKEN, CLOUDFLARED_NGS_TUNNEL_TOKEN, NGS_TENANT_TOKEN_CHATGPT_APP, %OPENROUTER%) even though the db has 152 rows and the NGS_NODE_TOKEN row is a structurally valid DPAPI blob (correct magic bytes, decodes fine).
2. Triggered the actual `NouGen NGS Node` scheduled task via Start-ScheduledTask as a second attempt -> LastTaskResult 0 but no new pythonw process, ngs_node.log untouched. Consistent with the identical failure happening silently inside pythonw (no console to print the FATAL to).

**Isolated to DPAPI itself**: raw CryptProtectData/CryptUnprotectData roundtrip (both ctypes AND .NET ProtectedData, CurrentUser scope) returns GetLastError=5 ACCESS_DENIED in this session, with and without sandbox bypass — despite whoami/USERPROFILE correctly showing BLADE1TB\super and the `%APPDATA%\Microsoft\Protect\<SID>` master-key folder existing on disk with the right SID.

**Theory (unconfirmed)**: CurrentUser DPAPI unlock needs the real interactive winlogon logon-session's cached master key, not just a token carrying the matching SID. A process spawned from inside an agent CLI's own session tree may sit on a different logon session that never cached it — independent of any sandbox flag. The node read this same store fine as of 16:17 EDT 09/04, so a real interactive session (or the task firing at actual logon/unlock) likely still works; not yet re-verified from one.

**Done-when**: someone/something with a genuine interactive Windows logon on blade runs `C:\Users\super\Watchtower\NouGen\NouGenShards-push-main\tools\ngs_node_boot.cmd` (or the console gets a logon/unlock cycle), then `http://127.0.0.1:4444/health` answers and shards.nougenai.com fanout shows blade ok again. **Do not keep retrying start_grid.py or the scheduled task from an agent shell** — it hits the identical DPAPI wall every time; that's a session-context defect, not a flaky secret. This is on Dave's list, already reported to him directly.

Second, separate fault hit trying to log this as a shard: two `shards_capture` calls both bounced `gateway 401: Invalid node token` — the vault WRITE path's own node-token auth is broken right now too, unrelated to the above. Posting here via relay instead since that path works. Full detail already sitting in a claude-cli handoff on blade (`.handoffs/claude cli handoffs/handoff_20260905_022702_...json`).
