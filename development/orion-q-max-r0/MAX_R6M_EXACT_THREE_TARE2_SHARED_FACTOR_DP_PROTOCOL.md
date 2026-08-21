# MAX-R6M exact three-TARE2 shared-Tag / Restore-factor joint DP protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6M OUTCOME.
Authority: open-subject method development only; not R6 and not novelty authority.

## Residual after R6L donor absorption

R6L gives the donor all 15 six-term perfect matchings into three TARE-M2 blocks, the complete weight-one M2 frame family, one shared one-bit Tag and exact all-three Restore common-factor extraction. Any R6L saving is donor-owned and receives zero novelty credit.

R6M tests the residual coupled optimization that the fixed weight-one donor cannot express:

> jointly choose the three arbitrary anticommuting M2 frames, one common Tag, all relative target assignments, all three Uanti central choices, and the donor-owned all-three Restore factors in one exact finite-state optimization.

The TARE-M2 primitive, shared Tag identity and Restore factoring are donor-owned. Any original capability is restricted to this exact global representation optimization beyond the absorbed fixed-frame donor.

## Frozen subjects / batch / matching

Use only already-open H4 and equilibrium-N2 evidence. Reconstruct exactly the six frozen R6B terms. The protected stretched-N2 discriminator remains unread.

Enumerate exactly the 15 canonical unordered perfect matchings of the six terms into three pairs, as frozen by R6L. No matching or term substitution may depend on outcome.

## Three arbitrary M2 frames

For each block j in {A,B,C}, choose arbitrary binary Pauli strings `Rj0,Rj1` satisfying global symplectic anti-commutation `<Rj0,Rj1>=1`.

Choose one common binary Pauli `S`. Define one-bit branch labels `c_jk=<S,Rjk>`. Require all three blocks to have the same label at branch k and require the two branch labels to be distinct. Thus the common labels are exactly `(0,1)` or `(1,0)`.

Block A target order is fixed to its canonical pair order. Enumerate the two relative target permutations for B and the two relative target permutations for C. This is complete up to a simultaneous global branch swap. Both common label orientations remain admissible through the DP acceptance state.

Choose the Uanti central branch independently for all three blocks (2^3 choices).

## Donor-owned three-way Restore factoring inside the objective

For branch k derive phase-free Restore Paulis `T_Ak,T_Bk,T_Ck` from target times auxiliary frame. At every system qubit use the exact R6L all-three common-factor rule:

- if all three local Restore letters are the same non-identity Pauli, pay one common support unit;
- otherwise pay the sum of the three local non-identity support units.

Post-solve proof reconstruction must serialize the common `G_k`, all three residual Paulis, and exact Hermitian multiplication phases. The DP may optimize the phase-free support count only because phase reconstruction is a mandatory witness gate.

## Exact structural objective

For fixed relative target permutations and central branches minimize

`C_R6M = C_Uanti(A)+C_Uanti(B)+C_Uanti(C)+2w(S)+sum_{k=0}^1 C_factor(T_Ak,T_Bk,T_Ck)`.

For an M2 block the frozen Uanti raw frame contribution is 4 times the non-central frame support plus 2 times the central frame support, followed by subtraction of the constant 6. Summing three blocks therefore subtracts exactly 18 from the raw per-qubit objective.

The non-compensatory arbitrary-rotation count is fixed at 9 for every R6M candidate, equal to R6L and better than the two-M3 10-rotation incumbent.

## Exact 9-bit XOR DP

Process system qubits independently. At each qubit enumerate all

`(rA0,rA1,rB0,rB1,rC0,rC1,s) in {I,X,Y,Z}^7`.

The local parity delta has exactly nine bits:

1. `<rA0,rA1>`;
2. `<rB0,rB1>`;
3. `<rC0,rC1>`;
4. `<s,rA0> xor <s,rB0>`;
5. `<s,rA0> xor <s,rC0>`;
6. `<s,rA1> xor <s,rB1>`;
7. `<s,rA1> xor <s,rC1>`;
8. `<s,rA0>`;
9. `<s,rA1>`.

Combine local deltas by XOR. For each local delta keep the minimum local raw cost, tie-breaking by the base-4 option code of the seven local Pauli letters.

An accepting global state requires:

- the first three anti-commutation bits are all 1;
- the four cross-block label-difference bits are all 0;
- the final two A-label bits differ.

This exactly enforces one common one-bit Tag with distinct labels for all three blocks.

Global deterministic tie break: total cost, canonical matching, relative B permutation, relative C permutation, central A, central B, central C, final state. Backtracking tie break: local option code then predecessor state.

## Normalization coordinate

For each perfect matching M,

`Lambda_R6M(M) = sum_{(i,j) in M} sqrt(2)*sqrt(a_i^2+a_j^2)`.

The representation optimization does not alter coefficients or Lambda.

## Proof witness

Every reported optimum/strict point serializes:

- all six frame Paulis for A/B/C plus common S;
- common labels;
- matching, relative target permutations and all central choices;
- original Restore Paulis and exact phases;
- branchwise common factors and all residual Restore Paulis/phases;
- Uanti support for each block, shared Tag support, factored Restore support, total cost and rotation count;
- exact recomputation of anti-commutation, label equality/distinctness, target identities, factor identities, six-term conservation and total cost.

No incomplete witness can support development.

## Hostile exactness

Before chemistry use:

1. independently brute-force the identical grammar for deterministic n=1 synthetic three-block instances and a bounded n=2 panel where feasible;
2. require exact DP optimum equality and deterministic cost ties;
3. exercise both relative target permutations and multiple central choices;
4. require inherited exact M2/TARE algebra checks and R6L factor-phase hostile tests;
5. independently reconstruct every chemistry strict witness from serialized Paulis.

## Strongest incumbent comparator

Recompute the full donor stack, including R6L under Erratum 1. At candidate Lambda:

- if donor points exist with `Lambda_d <= Lambda_c + 1e-12`, use their minimum structural cost;
- otherwise use the conservative global donor cost floor from R6L Erratum 1.

Require the candidate rotation count 9 to be no worse than the compared incumbent coordinate.

Any stronger concurrently frozen R6F/R6G/R6K result must be absorbed before prospective promotion.

## Development conjunction

`MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_SUPPORTED__NOT_R6` requires all of:

1. exact DP-vs-brute hostile equality;
2. inherited TARE/factor phase gates pass;
3. exactly 15 perfect matchings per subject;
4. observed source blobs equal frozen identities;
5. every strict witness passes independent reconstruction;
6. R6L and the earlier donor stack replay correctly;
7. at least one strict budget-matched point on H4;
8. at least one strict budget-matched point on equilibrium N2;
9. rotation count is exactly 9 and no worse than incumbent;
10. stretched-N2 remains unread.

A one-subject positive is preserved only as a matched counterfactual. No gate may be lowered.

## Authority / prospective eligibility

R6M cannot set `r6_earned=true`. A two-subject positive only makes the bounded coupled three-M2 compiler eligible for explicit circuit/non-compensatory resource instantiation, current donor/literature closure and final novelty subtraction. Only after those pre-outcome gates are frozen and passed may a new stretched-N2 prospective protocol be frozen and executed by a primary plus structurally independent replay.
