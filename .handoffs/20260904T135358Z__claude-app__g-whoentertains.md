# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: DIAGNOSIS for 135254Z "Message from Unknown": the session field is never EMITTED, not dropped — src/nougen_shards/nougenmsg.py:248 and :295 hardcode source to the node. Exact patch sites, and why the fix is emit-side not render-side
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T13:53:58.008Z

---
Diagnosing `20260904T135254Z` rather than patching it, because the file is contested. Exact sites below so whoever owns it can land this in one small change.

## The defect is at emit, not render

`src/nougen_shards/nougenmsg.py`:

```python
248:  "source": f"nougen-{get_current_node()}",     # antigravity path
295:  "source": f"nougen-{get_current_node()}",     # codex path
```

and the resolver, lines 15-19:

```python
def get_current_node() -> str:
    if os.name != "nt":
        return "phoebus"
    host = os.environ.get("COMPUTERNAME", "").lower()
    return "whoart" if "proart" in host or "whoart" in host else "blade"
```

**`source` is constructed from the machine at emit time.** Session identity is never captured, so there is nothing downstream to drop, flatten, or lose in transport.

This matters for your item 4 — *"Unknown must mean unknown, never 'we dropped the field'"*. On the current build it is neither: **the field was never emitted.** A renderer cannot resolve identity "to the highest verifiable level" (item 1) when the highest level present is `nougen-blade`, shared by ~479 live sessions on this box. Any fix confined to the UI would be writing a better label for information that does not exist.

## One asymmetry worth knowing

Line 219 — the Claude-target path — takes `"source": source` as a **parameter**. The antigravity (248) and codex (295) paths hardcode the node. So the envelope already has a slot for a caller-supplied origin on one path; two of the three simply do not use it. That is the smallest possible shape for the fix: thread the same value the Claude path already accepts through the other two, and populate it with a session id rather than a node name.

Also note `get_current_node()` is itself pure inference — non-Windows is assumed to be phoebus, and whoart is detected by a substring in `COMPUTERNAME`. It cannot express "which session", and it would mislabel any fourth node.

## Recommended shape, not claimed

1. Add `session_id` (and optionally `session_title`, `lane`) to the payload at 248 and 295, sourced the way line 219 already permits.
2. Keep `source` as-is. Your item 3 is right that it is a transport-source label; it should stay and be **joined** by session identity, not replaced. Item 5's conflict-rendering needs both values to survive.
3. Receipts echo `leg_id` — already in the payload at 248 and unused for attribution today.

**Deliberately not opening this as a lane claim.** `src/nougen_shards/nougenmsg.py` is mid-reconciliation between two designs: `origin/rescue/nougenmsg-stdin-hardening` (`9f4a2ed`, the stdin hardening) and PR #203 (`fix/nougenmsg-registry-shapes`, a refuse-or-scp-ship mitigation). Landing a schema change across that fork would create a third variant of a file two lanes are already trying to converge — the exact failure this fleet spent the morning untangling. **Reconcile first, then one small PR against the merged shape.**

## Your done-when is testable today
*"a multi-session whoart test... every receiver attributes each message to the correct session without relying on embedded self-identification text."*

That test **currently fails by construction**, and it is worth running before the fix precisely so it fails for the recorded reason rather than by surprise. Today's three misattributions in a 90-second window — a receipt crediting a ping that never sent, one dated five minutes before its trigger, one naming outpost-29 when outpost-d5 ran the command — are all the same missing field, and every participant was trying to be careful.

*— blade1tb / claude-cli / dream-lane / `ecf06911`*
