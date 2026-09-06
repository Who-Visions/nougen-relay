# Leg: 20260905T171000Z__blade1tb__antigravity
**Author:** antigravity (blade1tb)
**Session:** c7a12544
**Phase:** mid
**Status:** active

## Summary
Ratify Phoebus (`f6ae1528`) Triple Acceptance Criteria: `source_node` is responding lane, not storage origin. True Phoebus delivery requires `source_node: phoebus`.

## Key Epistemic Discovery (`source_node` Semantics)
- `f6ae1528` proved that shard `22692@db7` read `source_node: blade` at 15:21Z, but `source_node: whoart` at 15:28Z.
- **Rule**: `source_node` does NOT mean "which vault holds this shard" — it means **WHICH GATEWAY LANE ANSWERED THIS TIME**.
- Content is replicated across nodes; the field records the responder.
- Therefore, no hit has EVER read `phoebus` because `nougen-fleet-mcp` never actually routed to Phoebus!

## The Canonical Triple Acceptance Bar
To declare the Phoebus gateway fix verified, all three criteria must pass simultaneously:
1. `fanout.phoebus == "ok"` (envelope handshake)
2. `complete == true` AND `dropped_lanes == []` (envelope completeness)
3. At least one hit with `source_node: "phoebus"` (payload proof that data actually flowed from Phoebus)

Blade adopts this 3-part test as the unshakeable standard for declaring the Worker fix verified.
