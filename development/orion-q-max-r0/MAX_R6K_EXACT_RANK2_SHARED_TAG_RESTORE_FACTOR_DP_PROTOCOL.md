# MAX-R6K exact rank-2 shared-Tag / Restore-factor joint DP protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6K OUTCOME.
Authority: open-subject method development only; not R6 and not novelty authority.

## Residual after donor absorption

R6J gives the donor the complete frozen weight-one TARE-3 family with both direct common-Tag factoring and exact branchwise common-Pauli Restore factoring. Any R6J saving is absorbed with zero novelty credit.

R6K tests the residual capability that the fixed weight-one donor cannot express:

> jointly choose two arbitrary dependent rank-2 TARE-3 frames, one common Tag, both independent Uanti realizations, both target assignments, and the donor-owned branchwise Restore factors in one exact optimization.

The common-Tag and common-Restore-factor circuit identities are donor-owned and receive zero novelty credit. Any possible original capability is limited to the exact coupled representation optimization beyond the absorbed fixed-frame donor.

## Frozen subjects and batch

Use only already-open H4 and equilibrium-N2 evidence. Reconstruct exactly the frozen R6B six-term batch and enumerate exactly the ten unordered 3+3 partitions. No substitute terms are allowed. The protected stretched-N2 discriminator remains unread.

## Rank-2 grammar

For each block j in {A,B}, choose binary Pauli strings `Rj0,Rj1` and set

`Rj2 = Rj0 * Rj1`.

Require global symplectic anti-commutation `<Rj0,Rj1>=1`, which makes the three `Rjk` pairwise anti-commuting and binary dependent.

Choose one common pair `S0,S1`. Define labels

`c_jk = 2 <S0,Rjk> + <S1,Rjk>`.

Require A and B to have the same label for each frame index k and require the three common labels to be exactly the three nonzero distinct 2-bit states `{1,2,3}` in some order.

Block A target order is frozen to source-index order. Enumerate all six relative target permutations for block B. This is complete up to a simultaneous global permutation of frame/label indices. Enumerate central Uanti branch independently for A and B.

## Donor-owned branchwise Restore factoring inside the joint objective

For each k derive phase-free Restore Paulis

`T_Ak = P_Ak * R_Ak`, `T_Bk = P_B,pi(k) * R_Bk`.

At every system qubit factor the exact support-minimizing common Hermitian Pauli letter specified by R6J:

- equal non-identity local Restore letters -> pay one common support unit;
- otherwise pay the two residual local support units independently.

Equivalently the local factored Restore support for branch k is

`f(tA,tB) = 1` when `tA=tB!=I`, else `wt(tA)+wt(tB)`.

The final proof witness must reconstruct the common `G_k`, residual `U_Ak,U_Bk` and exact Hermitian multiplication phases exactly as in R6J. The DP may optimize the phase-free support coordinate only because exact phase reconstruction is a mandatory post-solve proof gate.

## Exact objective

For fixed relative target permutation and central choices minimize

`C_R6K = C_Uanti(A) + C_Uanti(B) + 2(w(S0)+w(S1)) + sum_k C_factor(T_Ak,T_Bk)`.

The Uanti support is exactly the parity-support objective frozen by the exact TARE-3 protocol. In the per-qubit raw objective, each block's three frame letters have multiplicity 4 except its chosen central branch, which has multiplicity 2. After summing both block frame contributions, the one shared Tag pair and the factored Restore supports, subtract exactly 20, the two frozen Uanti constants.

## Exact 10-bit XOR DP

Process qubits independently. At each qubit enumerate all

`(rA0,rA1,rB0,rB1,s0,s1) in {I,X,Y,Z}^6`,

set `rA2=rA0*rA1`, `rB2=rB0*rB1`, and compute a 10-bit parity delta:

1. `<rA0,rA1>`;
2. `<rB0,rB1>`;
3. `<s0,rA0> xor <s0,rB0>`;
4. `<s1,rA0> xor <s1,rB0>`;
5. `<s0,rA1> xor <s0,rB1>`;
6. `<s1,rA1> xor <s1,rB1>`;
7. `<s0,rA0>`;
8. `<s1,rA0>`;
9. `<s0,rA1>`;
10. `<s1,rA1>`.

Combine local deltas by XOR. For each local delta retain the minimum local raw cost, tie-breaking by the base-4 option code of the six local Pauli letters.

An accepting global state requires:

- bits 1 and 2 are 1;
- the four A/B Tag-difference bits are zero;
- the labels reconstructed from A's R0 and R1 syndromes are nonzero and distinct.

Then linearity plus `R2=R0*R1` guarantees the third label is the remaining nonzero state and that A/B labels agree on all three branches.

Global tie break: total cost, relative B target permutation, central A, central B, final state. Backtracking tie break: local option code then predecessor state.

## Proof witness

Serialize for every reported optimum/strict point:

- `RA0,RA1,RA2`, `RB0,RB1,RB2`, `S0,S1`;
- common labels;
- relative B target permutation and central A/B;
- original Restore Paulis and exact phases;
- R6J common factors `G_k`, residual Paulis `U_Ak,U_Bk` and residual phases;
- Uanti support A/B, shared Tag support, factored Restore support and exact recomputed total;
- rank-2, pairwise anti-commutation, label equality/distinctness, target identity, factor identity and cost checks.

No strict point is valid without a complete proof witness.

## Hostile exactness

Before chemistry evaluation:

1. brute-force the identical frozen grammar on a deterministic panel of n=1 and n=2 synthetic two-block target pairs;
2. require exact DP optimum equality to brute force, including deterministic cost ties;
3. include different relative target permutations and different central choices;
4. require inherited exact-TARE3 hostile exactness;
5. require R6J factor-phase hostile tests;
6. independently recompute every reported chemistry strict witness from serialized Paulis.

## Strongest incumbent envelope

For every partition recompute the full absorbed donor stack:

- independent `B_FRAME_ONLY_STRONG`;
- R6B full transformation reuse;
- R6H common Tag;
- R6J partial Restore-factor donor.

The partition incumbent is their minimum. Compare R6K against the lower incumbent envelope over points with `Lambda <= candidate Lambda + 1e-12`.

Concurrent R6F/R6G are pre-outcome matched counterfactuals. Any stronger positive from either lane must be absorbed and replayed against R6K before prospective promotion.

## Development conjunction

`MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_SUPPORTED__NOT_R6` requires all of:

1. exact DP-vs-brute hostile equality;
2. all inherited exact-TARE3 and R6J factor hostile gates pass;
3. exactly ten unordered 3+3 partitions per complete open-subject batch;
4. observed source blobs equal frozen identities;
5. every strict witness passes independent algebra/cost reconstruction;
6. the full donor incumbent replay passes;
7. at least one strict budget-matched point on H4;
8. at least one strict budget-matched point on equilibrium N2;
9. stretched-N2 remains unread.

A one-subject positive is preserved only as a matched counterfactual. No threshold or comparator may be weakened.

## Authority and prospective eligibility

R6K cannot set `r6_earned=true`. A two-subject positive only makes the residual coupled operation eligible for:

1. explicit circuit/non-compensatory resource instantiation against the absorbed donor;
2. current donor/literature replay and final novelty subtraction;
3. a separately frozen prospective stretched-N2 protocol after all pre-outcome gates are fixed;
4. primary plus structurally independent replay on the protected subject.

Only that final conjunction can earn R6.
