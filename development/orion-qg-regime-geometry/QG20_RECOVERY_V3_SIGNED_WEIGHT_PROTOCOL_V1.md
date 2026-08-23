# QG-20 Recovery V3 — Signed Weight Enumerator Protocol V1

**Status:** `FROZEN_AFTER_V2_NEGATIVE__BEFORE_V3_OUTCOME`  
**Owner:** QG-20 #863  
**Recovery coordinator:** #964

## Why V3 is licensed

The recovery sequence is immutable:

1. QG-15b original 13-coordinate state was non-identifying on complete `n<=3`: floor `43`, 12 mixed cells.
2. Recovery V1 prospectively found one load-bearing scalar, `negative_weight_sum`; it closed complete `n<=3` and a sealed 120-state `n=4` panel.
3. Complete `n=4` confirmation refuted sufficiency: old floor `586` -> V1 floor `128`; mixed cells `54` -> `20`.
4. Recovery V2 gave the **already-prefrozen** V1 grammar first right of refusal. With `negative_weight_sum` fixed, the best two companions were `n_negative` and `y_position_union`, yet complete `n=4` floor remained `85` and 12 mixed cells; train floor `62`, sealed holdout floor `14`; independent verifier accepted every search/statistic check.

Therefore the failure is no longer `one missing scalar from the old grammar`. A richer phase-distribution state is justified.

## Donor hypothesis frozen before V2 outcome

`research/negative-recovery/QG20_SIGNED_WEIGHT_ENUMERATOR_DONOR_NOTE_V1.md` was committed while V2 was still running.

It identifies **signed stabilizer weight enumerators** as prior mathematics that retains stabilizer sign/eigenvalue jointly with Pauli weight. V3 adopts this donor object; ORION claims no invention of signed weight enumerators.

The V1 scalar

`negative_weight_sum = sum_{P: lambda(P)=-1} wt(P)`

is only a first moment of the negative phase×weight distribution.

## Frozen V3 representation

For an `n`-qubit stabilizer state with signed stabilizer group elements `lambda(P) P`, define the simple signed-weight coefficients

`S_w = sum_{P: wt(P)=w} lambda(P)` for `w = 1..n`,

with `lambda(P)=+1` for positive encoded elements and `-1` for negative encoded elements.

For `n=4`, V3 adds exactly the four-vector:

`SIGNED_WEIGHT_V1 = (S_1, S_2, S_3, S_4)`.

No subset search is allowed. No coefficient may be dropped, selected, rescaled, or replaced after outcomes.

The tested state map is:

`phi3 = (original QG-15b 13-vector, S_1, S_2, S_3, S_4)`.

For comparison only, also report:

- original `phi0`;
- V1 `phi1 = (phi0, negative_weight_sum)`;
- V2 best map `(phi1, n_negative, y_position_union)`.

Those comparisons do not select V3.

## Exact domain

Use the complete exact `n=4` StabPrep stabilizer-state space from `qg15_third_family.referee(4)`:

- expected states: `36,720`;
- donor: frozen GE donor;
- gold: exact donor exactness `C_D == C_opt`.

This is a result-bearing V3 test even though the domain was used to diagnose V1/V2 failure, because the signed-weight representation itself was timestamped before V2 outcome and is fixed here without feature selection. It is nevertheless labeled **same-domain recovery**, not a fresh-domain replication.

## Exact statistics

For each map report:
- unique feature cells;
- mixed cells;
- deterministic error floor `sum_cell min(pos, neg)`;
- donor-exact positive count.

## Independent verifier

A separate implementation must rebuild `S_w` directly from encoded stabilizer group elements without importing V3 feature code:

1. decode sign bit and X/Z support per group element;
2. compute Pauli weight;
3. add `+1` or `-1` to the corresponding coefficient;
4. independently rebuild the original 13-vector;
5. independently recompute donor-exact labels from the exact referee;
6. reproduce all four map statistics exactly.

Verifier disagreement is serialized, not hidden.

## Strong V3 positive

All required:
- complete domain count `36,720`;
- V3 map floor `0`;
- V3 mixed cells `0`;
- analyzer replay byte-identical;
- independent verifier `ACCEPT` with exact statistics;
- representation fixed to all four signed-weight coefficients;
- no feature search/selection.

Terminal:

`QG20_RECOVERY_V3_SIGNED_WEIGHT_ENUMERATOR_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4`

Honest alternatives:
- `QG20_RECOVERY_V3_SIMPLE_SIGNED_WEIGHT_NONIDENTIFYING__COMPLETE_ENUMERATOR_OR_QUOTIENT_REQUIRED`
- `QG20_RECOVERY_V3_DUAL_DISAGREEMENT`
- `CANNOT_CHECK`.

## If V3 is negative

Do not retune the simple signed-weight vector. The next atomic successor may use the **signed complete Pauli weight enumerator** (separate X/Y/Z composition) because that escalation was explicitly anticipated in the pre-V2 donor note. If that also remains non-identifying, stop hand-designed feature escalation and execute the full QG-20 continuation-equivalence quotient.

## If V3 is positive

A same-domain positive is not final generalization. Freeze a new `n=5` target panel **without changing the representation**, then obtain exact costs by an independently checkable targeted/bounded exact referee. Only a held-out-size success can support a broader bounded state-coordinate recovery claim.

## Claim boundary

V3 can establish only that a donor-owned signed-weight state summary determines GE donor exactness on the complete `n=4` StabPrep domain. It does not establish all-n sufficiency, global state minimality, a new Clifford compiler, novelty of signed weight enumerators, or physical quantum advantage.