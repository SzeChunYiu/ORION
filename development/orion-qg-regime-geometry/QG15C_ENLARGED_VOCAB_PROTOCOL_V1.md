# QG-15c enlarged StabPrep boundary vocabulary — Stage 1 freeze

Issue #840. Base `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.
Parent: QG-15 / QG-15b committed results.

## Question
QG-15b proves the frozen 13-feature natural vocabulary is information-theoretically insufficient for donor-exact boundary classification: 12 mixed feature cells, irreducible floor 43/1146. Does a richer but still structural, donor-path-derived vocabulary determine the boundary on the complete n<=3 state spaces?

## No trivial identity features
Forbidden: canonical stabilizer-state key, full donor circuit token sequence, exact-referee cost, optimal circuit, exact gap, hash/ID of the state/circuit, or any feature derived from the donor-exact label.

## Frozen enlarged vocabulary L2
L2 contains QG-15b's 13 original features plus these n-independent summaries of the frozen donor disentangling circuit:

1. total gate counts: H, S, SDG, CX;
2. for each per-qubit load channel `H`, `S`, `SDG`, `CX_IN`, `CX_OUT`: minimum, maximum, sum of squares, number of zero-load qubits;
3. directed-CX graph summaries: used directed edges, maximum edge multiplicity, squared edge-count sum, reciprocal edge-pair count, maximum in-degree, maximum out-degree, squared in-degree sum, squared out-degree sum;
4. all 16 ordered gate-kind transition counts over `{H,S,SDG,CX}` in the donor sequence;
5. sequence summaries: first gate kind, last gate kind, number of gate-kind runs, maximum same-kind run length, number of distinct gate kinds.

All integer features. No thresholds/classifier are needed for Stage 1: feature-determination means identical L2 vectors never carry both labels.

## Domain
Complete StabPrep spaces n=1,2,3 only: 6 + 60 + 1080 = 1146 states. Labels are `donor_exact := (C_opt == C_D)` using the committed exact Dijkstra referee and frozen donor.

## Stage-1 discriminator
Collapse all 1146 rows by exact L2 vector. Compute:
- mixed cell count;
- exact irreducible classification floor `sum_cell min(pos,neg)`;
- first 20 mixed cells verbatim with representative canonical keys from both labels;
- comparison to QG-15b L1 floor 43/1146.

If any mixed cell remains, terminal:
`QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED`.
That is a first-class negative and scientifically closes QG-15c. No feature invention after outcome.

If zero mixed cells, terminal:
`QG15C_L2_FEATURE_DETERMINED_ON_COMPLETE_NLE3__HELDOUT_STAGE_REQUIRED`.
This does NOT close the lane; a separately frozen held-out classifier must then be tested on the existing QG-15 n=4 panel.

No novelty/R6/physical-advantage authority.