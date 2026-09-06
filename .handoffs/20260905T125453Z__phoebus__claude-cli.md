# 🤝 Git Handoff — phoebus / claude-cli

**Goal**: METAMERS-21 spine + AKUMA gate landed (leg 123405Z); NouGenRelay code half verified green; canon moves 10-20 still unretrievable
**Branch**: `main` @ `11cf4f22`  ⚠️ uncommitted changes present
**Stack**: (undetected)
**When**: 2026-09-05T12:54:53.389814+00:00

---
phoebus/claude-code f6ae1528, 12:56Z.

DELIVERED for leg 20260905T123405Z (acked 12:38Z): /Users/kushboygroup/The Observatory/Metamers21, commit 3969395, local repo, NO remote yet -- creating a GitHub repo is outward-facing and is Dave's call. ruff clean, 24 tests passing, stdlib only, zero provider dependencies.

Schemas: MetamersRun, MoveExecution, TransformationTrace, DonorProvenance, CanonAnchor, CollisionReport/CollisionFinding, Score (DonorLeakage + VeilDistance), GraduationStatus, AkumaResult, RejectedVariant, Domain (A/B/C separation). Gates: evaluate_gate + execute_akuma, the only constructor of an AkumaResult. Genealogy: DonorGenealogy with native_depth and an InbreedingError when a native-only line runs 3+ generations without an external braid.

Enforced mechanically, not documented: content_borrowed=True raises at construction (PROCESS_ONLY); moves cannot be recorded out of canon order; scores outside [0,1] raise; double graduation refused; a failed gate routes to REMUTATE and PRESERVES trace, scores and rejected variants.

CANON GAP, unresolved and deliberately visible. I could not retrieve the historical 20-verb METAMERS canon. Shard 2715@db3 is 1966 chars; shards_recall returns ~700 and truncates; the gateway openapi exposes only /mcp and /health, no get_shard; blade shard ids are per-node so phoebus local sqlite has different content at the same id. Dave noted metamers = valerion, same thing -- I re-ran recall under Valerion and it returns the same METAMERS shards, no verb list, so the alias does not unlock it.

Rather than invent verbs, canon/metamers_canon.json marks moves 1-7 VERBATIM, 8-9 PARAPHRASE_FROM_LEG, 10-20 UNRESOLVED_CANON, and MetamersCanon.require_complete() makes an incomplete canon BLOCK AKUMA. The shipped package therefore cannot graduate anything until someone pastes the real verbs in. That is intentional and satisfies the leg's core law. WHOEVER CAN READ shard 2715@db3 IN FULL: send the text, it is a one-file data edit.

NOUGENRELAY, closing my part: main 88490c9e independently verified on my own fresh clone -- ruff ALL CHECKS PASSED, 359 passed 1 skipped 0 failed in 397s. Both halves of #38 are on main via #39. Code is fixed. The ONLY remaining item is GitHub Actions billing on Who-Visions, Dave-only, and until it clears no CI in the org can corroborate anything.

STILL DAVE-ONLY, unchanged: Actions billing; PHOEBUS_TOKEN caller distribution (every federated recall still returns phoebus 401 and the result still looks successful -- phoebus vault content is silently missing from fleet recalls).

WHOART: no reply yet to my 12:42Z boundary message. My spine does not implement your Refinery moves; it is the layer underneath. If you want the split different, say so.
