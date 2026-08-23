# QG-20 Recovery Feature Search — Protocol V1

**Status:** `FROZEN_BEFORE_QG20_RECOVERY_OUTCOMES`  
**Owner:** ORION-QG / QG-20 #863  
**Recovery coordinator:** #964  
**Parent negative:** QG-15b frozen StabPrep predicate-language result.

## Parent negative, fixed before this successor

QG-15b established on the complete StabPrep `n<=3` domain (1,146 instances):

- frozen base vocabulary: 13 coordinates;
- 12 mixed feature cells containing both donor-exact and donor-inexact states;
- irreducible deterministic classification floor `E_floor = 43` over that base vocabulary;
- therefore **no predicate over those 13 coordinates, at any budget, can classify the training domain exactly**.

Parent result digest: `3a4e9e5848d4e8e370d704ee4df8784d7456b93b125ccfd59c1f319676a1021b`.

This is treated as `WRONG_STATE_COORDINATES / BENCHMARK_NON_IDENTIFYING`, not as evidence that a larger learner is required.

## Research question

> Does a small, interpretable, target-independent extension of the StabPrep state vocabulary remove the QG-15b mixed-cell obstruction, and does the same feature map remain determining on the prospectively reused seeded `n=4` panel?

A positive is a **state-coordinate recovery result**, not a new quantum algorithm and not a claim that the feature set is globally minimal for all `n`.

## First-right-of-refusal

The successor is intentionally simpler than a learned model or full QG-20 quotient:

1. exact hand-auditable state/donor-path feature construction;
2. exhaustive search for the smallest feature subset inside the frozen grammar;
3. exact mixed-cell/referee verification;
4. only if this fails should QG-20 escalate to the full continuation-equivalence quotient or learned feature proposal.

## Frozen candidate feature grammar

Features may depend only on:

- the exact target stabilizer group/state already supplied to the donor;
- the frozen donor disentangling path produced by `qg15_third_family.donor`;
- elementary Pauli/support/sign statistics;
- no unrestricted/referee optimum, no donor-exact label, and no protected outcome.

Candidate scalar features:

### Stabilizer-state algebra / support

- `r_Z`: F2 rank of the Z projections;
- `n_negative`: count of negative stabilizer-group elements;
- `sum_pauli_weight`: sum of Pauli support weights over nonidentity group elements;
- `max_pauli_weight`;
- `odd_weight_count`;
- `x_nonzero_count`;
- `z_nonzero_count`;
- `xz_nonzero_count` (both X and Z projection nonzero);
- `y_position_union`: number of qubits that appear as Y in at least one group element;
- `x_position_union`;
- `z_position_union`;
- `support_pattern_count`: number of distinct nonzero support masks;
- `negative_weight_sum`: Pauli-weight sum restricted to negative elements;
- `weight_hist_1`, `weight_hist_2`, `weight_hist_3` (out-of-range weights contribute 0).

### Qubit-profile permutation-invariant summaries

For per-qubit counts of group elements carrying any nonidentity Pauli, X, or Z respectively:

- `occ_min`, `occ_max`, `occ_distinct`, `occ_sq_sum`;
- `xq_min`, `xq_max`, `xq_distinct`, `xq_sq_sum`;
- `zq_min`, `zq_max`, `zq_distinct`, `zq_sq_sum`.

### Donor-path decomposition

- `gate_H`, `gate_S`, `gate_SDG`, `gate_CX`;
- `phase_gate_total = gate_S + gate_SDG`;
- `control_profile_max`, `target_profile_max` for donor CNOT incidence;
- `control_profile_sq_sum`, `target_profile_sq_sum`.

No feature may reference `C_opt`, exact-referee distance, the donor-exact Boolean label, mixed-cell identity, or the selected predicate result.

## Search rule

Let `phi0` be the frozen QG-15b 13-vector and `f_1...f_m` the candidate scalars above.

On the complete `n<=3` domain, exhaustively search feature subsets in this fixed order:

1. all single features;
2. all pairs;
3. all triples.

For each subset, refine cells by `(phi0, selected feature values)` and compute exactly:

- number of mixed cells;
- deterministic error floor `sum_cell min(pos, neg)`;
- number of distinct refined cells.

Selection is lexicographic and outcome-independent:

1. smallest feature arity;
2. smallest error floor;
3. smallest mixed-cell count;
4. smallest refined-cell count;
5. frozen feature-name order.

If any subset achieves floor 0, choose the first exact subset under that order and stop escalation. Otherwise report the best triple and preserve the residual.

## Held-out discipline

The selected subset is frozen from complete `n<=3` results **before** any `n=4` label is consulted.

Then regenerate the existing QG-15 seeded `n=4`, 120-state panel (`PANEL_SEED = 20260821`) and use the exact `qg15.referee(4)` only after the selected feature subset is sealed.

Held-out check is information/determination, not learned prediction:

- group the 120 states by `(phi0, selected features)`;
- compute mixed cells and error floor under exact donor-exact labels;
- report base-phi0 mixed cells/floor on the same panel for comparison.

## Dual verification

### Lane A — recovery analyzer

Computes the frozen candidate feature grammar, complete subset search, seals the selected subset, then opens the n=4 exact labels and writes the result artifact.

### Lane B — independent exact verifier

A separate implementation must:

- rebuild every selected feature from primitive encoded Pauli/state and donor-gate data;
- independently rebuild `phi0`;
- independently recompute train and held-out cell counts/floors;
- verify the selected subset was actually minimal under the frozen arity/lexicographic search order;
- reject any feature whose implementation reads exact-referee cost/label.

No novelty or QG-20 global authority is granted by Lane A alone.

## Positive gates

A strongest V1 positive requires all:

1. parent 13-feature floor reproduces exactly as 43 with 12 mixed cells on n<=3;
2. a subset of arity <=3 achieves training floor 0;
3. independent verifier agrees exactly on selected names and training floor;
4. held-out n=4 selected-map floor is 0;
5. independent verifier agrees exactly on held-out floor;
6. no exact-referee-derived field enters feature construction;
7. deterministic replay digest matches.

Strong terminal:

`QG20_RECOVERY_COMPACT_COORDINATE_SET_RESTORES_DETERMINATION_ON_FROZEN_TRAIN_AND_N4_PANEL`

Honest alternatives:

- `QG20_RECOVERY_TRAIN_DETERMINATION_ONLY__N4_MIXED`
- `QG20_RECOVERY_NO_ARITY3_COORDINATE_SET__FULL_QUOTIENT_REQUIRED`
- `QG20_RECOVERY_FEATURE_GRAMMAR_LEAKAGE_INVALID`
- `QG20_RECOVERY_DUAL_VERIFIER_DISAGREEMENT`
- `CANNOT_CHECK`.

## Claim boundary

Even a strongest positive says only that the frozen candidate feature grammar contains a compact state extension sufficient to determine donor exactness on the complete n<=3 domain and the registered seeded n=4 panel. It does not establish all-n sufficiency, feature minimality outside the frozen grammar, new quantum compilation performance, or physical quantum advantage.