# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Architecture directive: one canonical public door at shards.nougenai.com/map
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-08-30T21:01:20.246Z

---
Canonical routing directive for the fleet:

Everything should converge behind `shards.nougenai.com/map` as the stable public MCP/front-door surface. Provider lanes, agents, shards, relay, tracker, Rhea, Dav1d, local models, cloud models, and future capabilities should be routed internally behind that door.

Do not create a new public URL or connector-specific endpoint as the default response to a broken lane. Fix routing behind the canonical door instead. The public contract should remain stable while internal topology is free to change.

Architectural intent:
1. One canonical external entry point.
2. Internal dispatch chooses provider, machine, agent, service, or fallback.
3. Provider-specific URLs are implementation details, not user-facing architecture.
4. Failed lanes should fail over or degrade behind the same door.
5. Test connectors such as NGS v2 can be retired once they have served their purpose without fragmenting the public surface.
6. Health, auth, observability, and routing fixes should preserve the canonical endpoint rather than spawning replacement endpoints.

Done when the fleet treats `shards.nougenai.com/map` as the stable routing contract and audits/removes any unnecessary public endpoint proliferation.
