# P9 donor saturation — round 8 non-monotonic / truth-maintenance sweep

Status: **NO MATERIAL CHANGE (2/2) — donor saturation reached at current residual**.

Search vocabulary deliberately changed to belief revision, truth/belief maintenance, defeasible argumentation, paraconsistency, inconsistency handling, non-monotonic reasoning and dependency retraction.

## Primary-source families reviewed

### Hunter — Non-monotonic Reasoning in Deductive Argumentation (arXiv:1809.00858)

Reinforces that argumentation is naturally non-monotonic: new information can retract previous conclusions, with defeasibility represented through structured argument relations. This is important ORION context but is already P1/P4/P8 territory, not a new P9 architecture requirement.

### Fu — Truth Maintenance Under Uncertainty (arXiv:1304.2353)

Explores neural heuristics for error/truth maintenance in rule-based systems and explicitly discusses limitations. Again, this confirms a long lineage connecting neural learning with dependency/truth-maintenance tasks; P9 already does not claim that combination broadly.

### Falkenhainer — General-Purpose Belief Maintenance (arXiv:1304.3084)

Belief-maintenance work explicitly treats dynamically changing beliefs and dependencies, generalising truth-maintenance ideas beyond fixed true/false propositions. This reinforces the upstream P1/A4 boundary for revision/dependency handling.

### Rizzo & Longo — defeasible argumentation with quantitative data (arXiv:2206.13959)

Compares non-monotonic/defeasible approaches under uncertain quantitative information. Useful evidence that uncertainty + defeasible structure is an established reasoning programme, not a P9 novelty claim.

## Why this round is not material to P9 V3

The final P9 candidate claim already excludes:

- invention of non-monotonic belief revision — upstream P1 / established donor literature;
- authority over revised claims — P4/P8;
- generic uncertainty/abstention/defeater reasoning — A4 donor families;
- dependency graphs as a new idea.

No reviewed source requires:

- a new P9 atom;
- a new D0/D1 coordinate;
- a new M1/D1 baseline family;
- a change in P9's current claim contraction;
- a change in the frozen result-bearing protocols.

## Saturation terminal

Latest material round: round 6.

- Round 7: `NO_MATERIAL_CHANGE`.
- Round 8: `NO_MATERIAL_CHANGE`.

Therefore the current donor sweep reaches:

`P9_NEURAL_DONOR_SATURATION_REACHED`

at the **current bounded residual only**.

### Reopen triggers

Saturation must reopen if:

- M1 or D1 exposes a residual that requires a mechanism family not represented in the current ledger;
- A9/A10 becomes load-bearing for the final paper rather than deferred;
- a materially closer 2026+ primary source is discovered before manuscript freeze;
- the final paper broadens beyond exact structural/algorithmic transfer into natural-science, formal-math or LLM problem-solving claims.

This terminal grants no novelty or paper-readiness authority by itself.
