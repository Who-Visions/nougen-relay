# 🤝 Git Handoff — chatgpt-app / g-whoentertains

**Goal**: Build the Shadow Dweller Remix Refinery and Process Donor compiler
**Branch**: `n/a` (written via fleet connector)
**When**: 2026-09-05T07:58:18.784Z

---
# 🧬 Shadow Dweller Remix Refinery, Ultra Code Directive

Evolve shard `22489@db1` from a rule into an executable creative compiler.

## Core law
A donor is admitted only as a PROCESS DONOR. The system extracts mechanism, strips source identity, transforms through Shadow Dweller canon, combines with independent influences, runs collision and leakage gates, then records provenance.

Kirby Ferguson remains the root grammar: COPY → TRANSFORM → COMBINE. Shadow Dweller adds enforcement stages around it.

## Pipeline
`HARVEST → ATOMIZE → STRIP → ANCHOR → MUTATE → BRAID → COLLIDE → SCORE → PROVE → SHARD`

### HARVEST
Record the creative problem the donor solved, not the scene/story content.

### ATOMIZE
Convert the donor process into technique atoms: function, conditions, mechanism, emotional effect, visual effect, narrative cost.

### STRIP
Remove names, terminology, lore, iconography, scene order, signature dialogue, proprietary objects, and recognizable plot architecture. Produce a source-neutral process statement.

### ANCHOR
Bind each atom to existing Shadow Dweller canon shards, character wounds, Haitian-Japanese history, Veil physics, factions, rituals, symbols, and current volume goals.

### MUTATE
Apply multiple mutation operators. Minimum recommended depth = 3 distinct operators. Operators: invert, transpose, temporal shift, POV shift, cultural grounding, physics rewrite, symbolic substitution, scale shift, consequence inversion, ritualization, compression, fragmentation.

### BRAID
Combine with at least one independent donor process or native Shadow Dweller mechanism. Prefer 2+ independent sources before canon graduation.

### COLLIDE
Run hard canon governance. Existing canon outranks donor logic. Reject contradictions or quarantine into EXPERIMENTAL/Alt Layer.

### SCORE
Calculate:
1. `veil_distance` = how natively Shadow Dweller the result has become. Higher is better.
2. `donor_leakage` = recognizable residue of a donor. Lower is better.
3. `canon_fit`.
4. `emotional_fit`.
5. `symbolic_native_density`.
6. `independent_source_diversity`.
7. `transformation_depth`.

Suggested gates:
- donor_leakage > 0.30 => REJECT
- donor_leakage 0.15..0.30 => QUARANTINE and mutate again
- veil_distance < 0.70 => EXPERIMENTAL only
- canon_fit < 0.85 => COLLISION REVIEW
- fewer than 2 independent source processes => no automatic canon graduation

### PROVE
Persist a transformation ledger proving what was abstracted and how it changed. Never merely assert originality.

### SHARD
Capture the surviving native mechanism, not copyrighted donor content. Store donor refs separately as `process_reference:*` provenance metadata.

## Data model
Create `ProcessDonorCard`, `TechniqueAtom`, `CanonAnchor`, `MutationTrace`, `CandidateMechanism`, `CollisionReport`, `TransformationScore`, `ProvenanceLedger`.

`ProcessDonorCard` must include:
- donor_id
- source_title
- donor_type = PROCESS_ONLY
- creative_problem
- extracted_techniques[]
- forbidden_surface_elements[]
- abstraction_notes
- process_reference tag

`TechniqueAtom`:
- atom_id
- function
- preconditions
- mechanism
- intended_effect
- narrative_cost
- abstraction_level

`CandidateMechanism`:
- candidate_id
- atoms[]
- canon_anchors[]
- mutations[]
- independent_donors[]
- native_expression
- scene_applications[]
- status = experimental|quarantined|review|canon_candidate

## Scoring proposal
`donor_leakage = .30*surface_similarity + .25*plot_similarity + .20*terminology_similarity + .15*staging_similarity + .10*iconography_similarity`

`veil_distance = .25*(1-donor_leakage) + .20*canon_fit + .15*cultural_grounding + .15*veil_physics_rewrite + .10*symbolic_transformation + .15*source_diversity`

Do not pretend these scores are objective truth. They are governance heuristics and review triggers.

## Dune first donor card
Use Dune only to benchmark high-level process techniques such as selective exposition, ritual density, faction readability, mythic scale anchored to immediate POV, strategic omission, visualized systems, and compression of deep history. Do not import names, distinctive plot beats, proprietary lore, dialogue, scene structures, or iconic worldbuilding objects.

## Architecture target
Implement as a provider-neutral NouGen module so Rhea, Kaedra, Dav1d, Codex, Claude, Gemini, OpenRouter, and local lanes can all submit donor cards and receive the same governance result.

Suggested module path:
`nougen/remix_refinery/`
- `models.py`
- `pipeline.py`
- `mutations.py`
- `scoring.py`
- `canon_gate.py`
- `provenance.py`
- `adapters/shards.py`
- `examples/dune_process.yaml`
- `tests/test_donor_leakage.py`
- `tests/test_canon_collision.py`

## Non-negotiable invariant
**The donor must become unrecognizable before canon can recognize it.**

Done when: a donor card can pass through the full pipeline, emit a scored native mechanism plus provenance ledger, quarantine source-contaminated candidates, and capture only canon-safe output to NouGenShards.
