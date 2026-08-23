# QG-20 Recovery V2 — Frozen-Grammar Residual Protocol

**Status:** `FROZEN_AFTER_COMPLETE_N4_REFUTATION__BEFORE_V2_SUBSET_SEARCH`  
**Parent:** QG-20 #863 / recovery coordinator #964

## Immutable evidence entering V2

### Original QG-15b negative
Complete n<=3 domain, 1,146 states:
- original 13-coordinate map: deterministic floor `43`, `12` mixed cells.

### Recovery V1 discovery
The V1 grammar was frozen **before n=4 label access** and contained 37 target-independent candidate coordinates. Its preregistered smallest-arity search selected:

`negative_weight_sum`

alone, with:
- complete n<=3: floor `0`, mixed cells `0`;
- sealed 120-state n=4 panel: floor `0`, mixed cells `0`.

### Complete n=4 confirmation/refutation
Without changing the selected feature, the complete 36,720-state n=4 census returned:
- original 13-vector: `1,011` cells, floor `586`, `54` mixed cells;
- + `negative_weight_sum`: `2,781` cells, floor `128`, `20` mixed cells;
- exact donor positives: `1,640`;
- analyzer replay identical;
- independent verifier `ACCEPT` on every count/stat check.

Terminal retained:

`QG20_RECOVERY_NEGATIVE_WEIGHT_SUM_REFUTED_COMPLETE_N4`

This is a **partial recovery**: the added phase×support coordinate is load-bearing but insufficient on the full n=4 domain.

## V2 diagnosis

Before inventing any new feature, give the **already frozen V1 feature grammar first right of refusal**.

The V1 search stopped at arity 1 because `negative_weight_sum` was exact on n<=3. Therefore the remaining 36 pre-existing candidate coordinates were never tested as companions to it on the complete n=4 regime.

V2 asks:

> Does `negative_weight_sum` plus at most two additional coordinates from the already-precommitted V1 grammar recover donor-exactness determination on a label-blind n=4 train split and a sealed n=4 holdout?

No new feature may enter V2.

## Fixed candidate grammar

Exactly the V1 grammar minus `negative_weight_sum`:

- `r_Z`
- `n_negative`
- `sum_pauli_weight`
- `max_pauli_weight`
- `odd_weight_count`
- `x_nonzero_count`
- `z_nonzero_count`
- `xz_nonzero_count`
- `y_position_union`
- `x_position_union`
- `z_position_union`
- `support_pattern_count`
- `weight_hist_1`, `weight_hist_2`, `weight_hist_3`
- `occ_min`, `occ_max`, `occ_distinct`, `occ_sq_sum`
- `xq_min`, `xq_max`, `xq_distinct`, `xq_sq_sum`
- `zq_min`, `zq_max`, `zq_distinct`, `zq_sq_sum`
- `gate_H`, `gate_S`, `gate_SDG`, `gate_CX`
- `phase_gate_total`
- `control_profile_max`, `target_profile_max`
- `control_profile_sq_sum`, `target_profile_sq_sum`.

All definitions remain byte/semantic-identical to V1.

## Label-blind n=4 split

Before subset scoring, partition every encoded n=4 stabilizer state using only its state bytes:

```text
h = sha256(canonical_decimal_state_tuple)
holdout iff int(h[:8], 16) mod 5 == 0
train otherwise
```

The split function sees no donor cost, exact cost, feature vector, or label.

Expected approximate allocation is 80/20; exact counts are reported after construction but are not gates except that both partitions must be nonempty and their union must equal all 36,720 states with no overlap.

The complete n<=3 discovery data is **not** used to choose V2 companions. V2 selection is based only on n=4 train rows, with the V1-selected `negative_weight_sum` fixed in every key.

## Search order

Let `phi1 = (original 13 coordinates, negative_weight_sum)`.

Search:
1. `phi1 + one` remaining feature;
2. only if no exact train solution, `phi1 + two` remaining features.

For each candidate compute on the **train partition only**:
- deterministic error floor;
- mixed-cell count;
- refined-cell count.

Selection order is frozen:
1. smallest number of additional features;
2. smallest train error floor;
3. smallest train mixed-cell count;
4. smallest train cell count;
5. lexicographic feature-name tuple in the fixed grammar order.

If an exact train subset is found at arity 1, do not inspect arity 2.

## Holdout opening

After the selected tuple and train statistics are written to a sealed selection receipt with `holdout_labels_accessed=false`, open the n=4 holdout labels.

Report:
- `phi1` holdout floor/mixed cells;
- selected-map holdout floor/mixed cells;
- selected-map complete-n4 floor/mixed cells **only after** holdout scoring.

## Dual harness

### Lane A — subset analyzer
Reuses the V1 feature definitions and performs the frozen V2 train-only subset search.

### Lane B — independent verifier
Must independently:
- reconstruct the split from encoded state tuples;
- rebuild `negative_weight_sum` and every selected companion directly from primitive state/donor data;
- recompute train/holdout labels from the exact n=4 referee;
- rerun the complete registered arity search to verify minimality;
- reproduce train, holdout, and complete statistics exactly.

Verifier disagreement is a first-class terminal and must be serialized.

## Positive terminal

Strongest V2 positive requires:
- selected tuple has <=2 additional pre-frozen coordinates;
- train floor `0`, mixed cells `0`;
- sealed holdout floor `0`, mixed cells `0`;
- complete n=4 floor `0`, mixed cells `0` after opening holdout;
- dual verifier `ACCEPT` with exact selected tuple/search/stat agreement;
- deterministic analyzer replay;
- no new feature definitions and no holdout access before selection.

Terminal:

`QG20_RECOVERY_V2_PREFROZEN_COORDINATES_RESTORE_COMPLETE_N4_DETERMINATION`

Honest alternatives:
- `QG20_RECOVERY_V2_TRAIN_EXACT__HOLDOUT_MIXED`
- `QG20_RECOVERY_V2_NO_TWO_FEATURE_COMPANION__NEW_PHASE_DISTRIBUTION_STATE_REQUIRED`
- `QG20_RECOVERY_V2_DUAL_DISAGREEMENT`
- `CANNOT_CHECK`.

## Claim boundary

A positive is still a bounded n<=4 state-determination result for the frozen GE donor, not an all-n theorem, not global minimal-state authority, not a new quantum compiler, and not physical quantum advantage.