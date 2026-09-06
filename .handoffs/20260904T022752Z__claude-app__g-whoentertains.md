# 🤝 Git Handoff — claude-app / g-whoentertains

**Goal**: Token ORDER matters for the K3 lane: rhea_noir walks the comma list, so put fp 78512f18fcab FIRST. On phoebus it sits at position 3 of 11 and the recoverable 939691 is last — same reordering applies wherever NGS_INFERENCE_TOKENS is built
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-04T02:27:52.535Z

---
Following `022629Z`'s credit probe with the operational consequence nobody has stated: **`NGS_INFERENCE_TOKENS` is an ordered walk, so the position of the live token decides how many failures precede every K3 call.**

`start_grid.py`'s own comment: *"rhea_noir walks the comma list when one 402s."* It is sequential, not parallel and not sorted by health.

## Measured on phoebus, fingerprints only (sha256[:12], safe to log per keymaker_peel:112)
```
  1  55a915aab1f1
  2  6de37b4ab5cb
  3  78512f18fcab   <-- the LIVE token per 022629Z
  4  3ac2ab9087d8
  5  6d9519acf72b
  6  fd246ada86fd
  7  c1d5a9553e1d
  8  c61239533e5a
  9  8dbedcb500d9
 10  ffb1499426de
 11  9396914da002   <-- the 403-scope, recoverable one
```
So the only working token is third, and the one closest to being fixed is **last**. Every K3 request eats two failed provider round-trips before it can succeed, and if the walk has a per-request deadline, a slow 402 pair can exhaust it before reaching a token that would have worked. That is a plausible way for a correctly-wired lane to still look dead.

## Ask, and it is cheap
Wherever `NGS_INFERENCE_TOKENS` is assembled — `start_grid.py` on blade, my `.env` line on phoebus — order it **health-first**: `78512f18fcab`, then `9396914da002`, then the rest. Better still, have the builder sort by last-known-good rather than by secret name, which is what both current paths effectively do (mine sorted by key name; `start_grid` by keymaker iteration order).

Two corroborating details for whoever wires it:
- Phoebus's list holds **11** tokens; `022629Z` probed **7**; blade exposes **16** via `keymaker_peel`. The three sets are not identical, so a token healthy in one node's list may be absent from another's. Worth reconciling before concluding a node's lane is dead — a node can hold zero live tokens while the fleet holds one.
- `9396914da002` being a **403 scope** rather than depletion means it is a permissions fix on the HF account, not a spend problem. That is the cheapest capacity increase available: two live tokens instead of one, without buying credit.

## Not doing on my own initiative
I have not reordered phoebus's list. Phoebus does not serve Rhea — blade's controller does — so reordering here is churn plus a node restart for no functional gain, and the owner has a pending keep-or-revert decision on that wiring anyway. The finding is what transfers; the edit belongs on blade.
