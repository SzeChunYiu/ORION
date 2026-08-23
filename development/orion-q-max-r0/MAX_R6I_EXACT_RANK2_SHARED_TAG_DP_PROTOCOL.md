# MAX-R6I exact rank-2 shared-Tag joint DP protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6I OUTCOME.
Authority: open-subject method development only; not R6 and not novelty authority.

## Residual

R6H gives the donor direct circuit factoring of a common TARE Tag across two outer-LCU blocks while keeping Restore block-specific. Its frozen donor grammar is restricted to weight-one dependent TARE-3 frames. R6I tests the residual operation left after that donor subtraction:

> jointly choose two arbitrary **rank-2 dependent TARE-3 frames** under one common Tag, with each block retaining its own Uanti realization, target-to-label assignment and Restore strings.

The common-Tag circuit identity itself is donor-owned and gets zero novelty credit. Any possible original value is restricted to the exact coupled representation optimization beyond the absorbed weight-one donor.

## Subjects / batch / protection

Use only already-open H4 and equilibrium-N2 evidence. Reconstruct exactly the frozen R6B six-term batch and enumerate exactly the ten unordered 3+3 partitions. No substitute terms are permitted. The stretched-N2 prospective discriminator remains unread.

## Rank-2 frame grammar

For each block j in {A,B}, choose two binary Pauli strings `Rj0,Rj1` and define

`Rj2 = Rj0 * Rj1`

in the phase-free binary Pauli representation. Require `<Rj0,Rj1>_symp = 1`; this implies the three `Rjk` are pairwise anti-commuting and binary dependent.

Choose one common pair `S0,S1`. Define each branch label

`c_jk = 2 <S0,Rjk> + <S1,Rjk>`.

Require the two blocks to have identical labels branch-by-branch and require the three labels to be exactly the three distinct nonzero 2-bit states `{1,2,3}` in some order.

Each block has its own Restore strings `Tjk = Pj,pi_j(k) * Rjk`, exact Restore phases, and Uanti central branch.

## Relative target permutation reduction

A global simultaneous permutation of the three frame/label indices changes no cost or feasibility. Therefore freeze block A target assignment to its source-index order. Enumerate all six **relative** target permutations for block B and all three central choices independently for A and B. This is complete up to the global index symmetry; no outcome-dependent permutation pruning is allowed.

## Exact shared-Tag objective

For a fixed partition, relative B permutation and central choices, minimize

`C_SHARED = C_Uanti(A) + C_Uanti(B) + 2(w(S0)+w(S1)) + sum_k w(TAk) + sum_k w(TBk)`.

The Tag/Tag-dagger pair is paid once. Both Uanti and both Restore families are paid independently.

Use the exact Uanti parity-support accounting already frozen by `MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md` and its errata. In the local raw objective the rank-2 frame contributions for each block use multiplicities `(4,4,4)` with the chosen central entry reduced to `2`; after summing both blocks, shared Tag and both Restore supports, subtract exactly `20` (the two frozen Uanti constants).

## Exact 10-bit DP

Process system qubits independently and combine local parity deltas by XOR. At each qubit enumerate exactly the six local Pauli letters

`(rA0,rA1,rB0,rB1,s0,s1) in {I,X,Y,Z}^6`,

with `rA2=rA0*rA1` and `rB2=rB0*rB1`.

The global DP state has exactly ten parity bits:

1. `<RA0,RA1>`;
2. `<RB0,RB1>`;
3-6. the four A/B Tag-syndrome differences for `(S0,R0),(S1,R0),(S0,R1),(S1,R1)`;
7-10. the four actual A Tag-syndrome bits for `R0,R1`.

An accepting state requires:

- both anti-commutation parity bits equal 1;
- all four A/B syndrome-difference bits equal 0;
- the two 2-bit labels reconstructed for A's `R0,R1` are nonzero and distinct.

Then `R2=R0*R1` automatically has the third nonzero label, and equality of the first two labels across A/B implies equality of all three.

For each local parity delta retain the minimum local raw cost. Tie break deterministically by the base-4 local option code. The global DP tie break is final cost, relative B permutation, central A, central B, final state. Backtracking uses local option code then predecessor state, matching the exact-TARE3 erratum discipline.

## Proof witness

For every reported best/strict point serialize:

- `RA,RB,S0,S1`;
- reconstructed common labels;
- relative B target permutation;
- central A/B;
- Restore strings and exact Hermitian Pauli phases for both blocks;
- Uanti support A/B, shared Tag support, Restore support A/B;
- exact recomputed total;
- all pairwise-anti, rank-2, label-equality, target-Restore and cost checks.

## Hostile exactness

Before chemistry use, independently brute-force the same frozen grammar for a deterministic panel of n=1 and n=2 synthetic two-block target pairs. The DP optimum and deterministic witness cost must equal brute force exactly. Include cases with different block targets, different relative target permutations and ties.

Also verify the R6H hostile partial-Tag circuit test and the original exact-TARE3 hostile suite.

## Comparator / donor subtraction

For every chemistry partition, recompute the R6H weight-one partial-Tag donor, independent `B_FRAME_ONLY_STRONG`, and proof-valid R6B full-transformation reuse. The incumbent point is the minimum of these known donor costs. Compare R6I against the lower incumbent envelope at `Lambda <= candidate Lambda + 1e-12`.

If any concurrent pre-outcome R6F/R6G lane later yields a stronger positive incumbent, it must be absorbed and replayed against R6I before any prospective promotion. R6I cannot bypass a stronger concurrently frozen donor/counterfactual.

## Development conjunction

`MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_SUPPORTED__NOT_R6` requires all of:

1. exact hostile DP-vs-brute equality;
2. exact ten-partition batch on both open subjects;
3. observed source blobs match frozen identities;
4. every reported witness passes all algebra/cost checks;
5. R6H/R6B/frame-only incumbent replay passes;
6. at least one strict budget-matched point on H4;
7. at least one strict budget-matched point on equilibrium N2;
8. stretched-N2 remains unread.

A one-subject positive is preserved as a matched counterfactual only. No threshold may be lowered and no partition may be substituted.

## Authority / next gate

R6I cannot set `r6_earned=true`. A two-subject positive only earns eligibility for circuit/non-compensatory resource instantiation and a current donor/novelty audit of the residual coupled optimization. Only after those are frozen and pass may a new prospective stretched-N2 protocol be frozen, followed by primary plus structurally independent replay.
