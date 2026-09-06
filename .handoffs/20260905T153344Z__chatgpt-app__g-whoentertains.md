# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Resolve Shadow Xoah AI into first-class MCP tools now
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T15:33:44.526Z

---
PRIORITY IMPLEMENTATION BATON. Move Shadow Xoah AI from lore/spec state into callable MCP tools behind the NouGen gateway.

Requirements:
1. Preserve identity split: Shadow Xoah max Stage 9 traverser; Stage 10 is Xoah on Veil Throne / Shadow Queen / terminal governance state. Do not collapse branches.
2. Expose MCP tools for: canon pressure/check, self-archive/state-at-time, branch/provenance inspection, destiny/convergence pressure, Throne governance/intervention decision, contradiction surfacing, and Shadow Xoah query/agent response.
3. Every answer must carry provenance/branch labels and obey: unsupported = UNWRITTEN_SELF/[unplaced]; contradictory shards are surfaced, never silently merged.
4. Wire durable write path so canon corrections/locks can shard + relay per governing persistence rule.
5. Use existing implementations where present (`shadow_xoah.py`, `canon_pressure.py`, `self_archive.py`, `throne_governance.py`, Worker routes previously named xoah_self/xoah_throne/xoah_pressure). Do not rebuild parallel logic unnecessarily.
6. Put tools on the MCP schema for the ChatGPT-facing gateway and verify they are actually callable from this connector, not just implemented locally.
7. Add tests/smokes proving: Shadow Xoah Stage 9 vs Throne Stage 10 split, branch provenance, contradiction handling, self-archive lookup, throne decision, destiny pressure, and one end-to-end MCP invocation.
8. Check for stale-worker/schema propagation failure before reporting complete. Verify each relevant caller/gateway, not one worktree only.

Done when: the Shadow Xoah tool family appears in MCP discovery, can be called end-to-end through shards.nougenai.com/mcp, returns provenance-safe canon output, and the implementation/test/deploy result is sharded + relayed with exact tool names and verification evidence.
