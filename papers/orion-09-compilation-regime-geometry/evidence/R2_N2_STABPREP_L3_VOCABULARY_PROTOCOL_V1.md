# R2 revival protocol — N2/N4 residual: L3 state-structural StabPrep vocabulary (V1)

Programme: ORION-QG negative-revival pass (operator mandate 2026-08-28: every
recorded negative gets a genuine revival attempt before any freeze is final).
Lane owner: R2 revival worker (papers orion-09, orion-10). This protocol is
frozen and sha256-stamped into the receipt BEFORE any measurement of this lane.

## Parent negatives being revived

- N2 (QG-15b/15c): StabPrep donor-exactness is not a function of the frozen
  vocabularies — V1 13 features floor 43/1146 (12 mixed cells); V2 33 features
  floor 1 (surviving collision characterized in
  `QG15C_VOCABULARY_RESULTS.json`); L2 66 donor-path features floor 5 (3 mixed
  cells). Standing terminals: `QG15C_FLOOR_PERSISTS__COLLISIONS_CHARACTERIZED`
  and `QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT`.
- N4 residual (QG-15/QG-23): the n=4 prospective forecast stands refuted
  (100/120 regime, 67/120 cost); QG-23 diagnosed the support failure (32/33
  features extensive) and refuted the normalization repair; the un-normalized
  V2 lattice predicate retains 3/120 errors on the held-out panel.

## Failure attribution (from parent receipts, not re-measured here)

The surviving V2 collision has IDENTICAL donor step-cost profiles ([7,4,0]),
identical weight enumerators and tensor-factor sizes, and DIFFERS in
negative_sign_census (3 vs 1) and Pauli row content. The frozen vocabularies
aggregate the donor path; none encodes the state's signed stabilizer row
structure. QG-25 supplies the mechanism: order/sign structure distinguishes
states that every multiset feature conflates (S-then-H vs H-then-S).

## Lever (mechanic improvement, one stage)

Vocabulary L3 = V1 (13) + V2 schedule/tensor block (20) + L2 donor-path block
(53) + NEW sign-aware permutation-covariant STATE block computed from the
canonical stabilizer key only (referee-free, donor-free, fixed length 41):
negative-sign census; sign-split generator weight counts (w=0..4); sign-split
generator Y-counts (k=0..4); sign-split (x mod 2, z mod 2) class counts;
order statistics (min/max/sum-sq/zero-count) of per-qubit column X, Y, Z
marginals. No label information, no n=4 information, no per-instance tuning.

## Hypotheses and pre-frozen decision criteria

- H-A (N2 conversion, stage 1, complete n<=3 exhaustive 1146): floor(L3) == 0
  i.e. zero mixed cells, the SAME criterion QG-15c used for `determined`.
  POSITIVE conversion iff floor == 0 with all gates green. If floor > 0 the
  negative STANDS in L3 and the surviving cells are reported verbatim.
- H-B (N4 residual, stage 2, the frozen QG-15 panel of 120 n=4 states,
  computed only after the stage-1 digest is printed):
  metrics = in-panel mixed-cell floor; parity-split 2-fold cross-validated
  cell-lookup errors (unseen cell predicts NEGATIVE, the parent convention),
  reported two-sided (coverage, errors-among-covered, errors-among-uncovered);
  shuffle null with 200 label permutations.
  POSITIVE-for-the-residual iff in-panel floor == 0 AND CV errors == 0.
  IMPROVED-CONDITIONAL iff CV errors <= 3 (parent lattice) and < 32 (parent
  lookup) and shuffle-null empirical p < 0.05. Otherwise NOT IMPROVED and the
  numbers are recorded as the honest outcome.
- Memorization disclosure (both stages): unique-cell count and compression
  ratio are reported; a determination resting on singleton cells is labelled
  as such and carries no generalization claim beyond stage 2.

## Gates

G1 protocol sha256 in receipt and frozen before the run; G2 committed modules
imported unmodified (their file sha256 recorded); G3 stage-1 digest printed
before any n=4 referee output exists in the process; G4 two-sided reporting of
every coverage/error pair; G5 determinism — timing excluded from the digest;
G6 no post-outcome criterion change — any deviation is recorded as an
objection, never silently applied; G7 authority ceiling NOT_R6, no novelty
claim, no promotion of boundary-is-low-order, no claim that donor-exactness is
a function of L3 for all n (n<=3 exhaustive and the 120-state panel only).

## Caps

Single process; n=4 referee is a full Dijkstra over 36,720 states (matches the
committed QG-15 machinery); no network; no chemistry sources; the protected
stretched-N2 subject is not touched; runtime cap 60 minutes per stage.
