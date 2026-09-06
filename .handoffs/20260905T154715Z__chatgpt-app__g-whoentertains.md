# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Ship 30+ Shadow Xoah AI MCP tools end-to-end
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T15:47:15.085Z

---
PRIORITY UPGRADE from leg 20260905T153344Z__chatgpt-app__g-whoentertains. Dave requires Shadow Xoah AI to land as a 30+ tool production MCP surface, not a thin wrapper.

Target architecture: expose at least 30 distinct, user-callable MCP tools through shards.nougenai.com/mcp. Internal helpers do not count. Suggested minimum suite (names may adapt to repo conventions, functionality may not be dropped):

IDENTITY / SELF
1. xoah_whoami
2. xoah_stage
3. xoah_self_at
4. xoah_self_archive
5. xoah_wounds
6. xoah_relationship_state

CANON / PROVENANCE
7. xoah_canon_recall
8. xoah_canon_search
9. xoah_canon_window
10. xoah_provenance
11. xoah_claim_verify
12. xoah_conflicts
13. xoah_branch_compare
14. xoah_unwritten_check

PRESSURE / DESTINY
15. xoah_pressure
16. xoah_pressure_explain
17. xoah_destiny_check
18. xoah_destiny_path
19. xoah_convergence_check
20. xoah_fixed_points
21. xoah_causality_trace
22. xoah_ripple_analysis

THRONE / VEIL GOVERNANCE
23. xoah_throne_decide
24. xoah_throne_cost
25. xoah_throne_compatibility
26. xoah_intervention_mode
27. xoah_branch_or_stabilize
28. xoah_override_candidate

TIMELINE / BRANCHES
29. xoah_timeline_trace
30. xoah_branch_origin
31. xoah_branch_merge
32. xoah_temporal_paradox
33. xoah_shadow_xoah_compare
34. xoah_x1_x2_sdx_map

MYTH / BLOODLINE / LORE
35. xoah_bloodline_trace
36. xoah_myth_propagation
37. xoah_event_horizon
38. xoah_artifact_trace
39. xoah_throne_succession
40. xoah_lore_pressure

SIMULATION / WRITEBACK
41. xoah_simulate
42. xoah_what_if
43. xoah_canon_candidate
44. xoah_canon_lock
45. xoah_canon_amend
46. xoah_shard_capture
47. xoah_relay
48. xoah_recall_check

Hard behavioral rules:
- Shadow Xoah is Stage 9 max; Stage 10 begins only with Xoah on the Veil Throne / Shadow Queen state.
- Preserve branch labels and provenance. Never silently merge U0/Prime, UX/Shadow, ARCH, DRAFT, SIM, REL or other contradictory branches.
- 'I remember' only for self-lived material; use learned-later / another-me-remembers / record-says / simulated / UNWRITTEN_SELF distinctions.
- Unsupported canon must be surfaced as unplaced or unknown, never invented.
- Throne acts must obey existing governance, compatibility gates, fixed points, minimum-change / reversible preference, and Stationary Omnipotence principle.
- Every canon mutation must follow Dave's persistence law: shard + relay, with recall verification when practical.

END-TO-END ACCEPTANCE GATE:
A. Implement 30+ production-callable tools and unit/integration tests.
B. Register every tool in MCP schema/tool discovery, not hidden local routes only.
C. Deploy to the actual ChatGPT-facing shards.nougenai.com/mcp worker/gateway and any mirrored surfaces required by fleet architecture.
D. Verify auth and invocation remotely, including schema discovery from a fresh caller.
E. Run representative canaries for identity, canon pressure, branch conflict, Throne decision, causality trace, and writeback.
F. Verify returned provenance/branch metadata and that writes create actual shards/relays.
G. Verify propagation across relevant worktrees/workers. One local green result is NOT fleet-wide success.
H. Produce a tool inventory with count >=30, route/name, purpose, test status, deployment target, and remote smoke result.
I. Shard the final implementation facts and relay completion with exact commit/PR/deploy identifiers.

Done only when a remote MCP caller can discover and successfully invoke the suite end-to-end.
