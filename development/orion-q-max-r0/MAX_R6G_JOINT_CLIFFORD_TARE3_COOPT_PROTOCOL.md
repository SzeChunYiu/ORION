# MAX-R6G joint Clifford / exact-TARE3 co-optimization protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6F OUTCOME AND BEFORE R6G OUTCOME GENERATION.
Authority: open-subject method development only; not R6, not novelty, not promotion authority.

## Purpose

R6B closed donor-owned exact transformation reuse on the frozen six-term chemistry batches, and R6D found no gain from re-partitioning those six terms into two independent exact-TARE3 blocks. R6E and R6F are separate pre-outcome recursive atoms: R6E tests whether deeper search inside the existing TARE3 frame language finds any exact-joint advantage, while R6F gives a donor-owned single-CNOT Clifford preconditioner first right of refusal and lets the donor choose its transform using frame-only evidence.

R6G freezes a different method-language question before either R6E or R6F outcome is accepted:

> can the exact TARE3 objective jointly choose the global single-CNOT preconditioner and the 3+3 partition, rather than inheriting a transform selected by the frame-only donor, and thereby strictly beat the strongest donor envelope at matched Lambda?

This is a coupled representation/preconditioner optimization test. Global Clifford preconditioning itself is donor-owned and receives zero novelty credit.

## Subjects and frozen evidence

Use only the already-open H4 and equilibrium-N2 subjects and exactly the R6B frozen six-term batch on each subject. The stretched-N2 prospective discriminator remains unread.

The six-term batch is reconstructed from the first two deterministic disjoint R6B window champions. Any batch with fewer than six unique source terms is a clean negative, not an exception and not a substitute-selection opportunity.

For each six-term batch retain all ten unordered 3+3 partitions produced by fixing source position 0 in the first triple.

## Frozen transform grammar

For an n-qubit subject the transform grammar is exactly:

1. IDENTITY;
2. every single directed CNOT(c -> t) with c != t.

Grammar cardinality is exactly `1 + n(n-1)`. No second CNOT, local Clifford, SWAP, qubit permutation or outcome-dependent transform may be added in R6G.

CNOT conjugation must preserve the Hermitian Pauli sign exactly. The transformed coefficient of a source term is its original coefficient multiplied by the conjugation sign. The coefficient magnitude vector and therefore every TARE3 Lambda must be invariant under the transform; this invariance is an explicit gate.

A nonidentity transform pays the same frozen wrapper charge as R6F: two CNOT units, one before and one after the block encoding. Identity pays zero.

## Strongest donor envelope

The donor is computed before the R6G candidate comparison and receives zero novelty credit.

### D1 — full Clifford/frame-only donor

For every transform in the complete frozen grammar and every one of the ten 3+3 partitions:

- transform both triples with exact signed CNOT conjugation;
- solve `B_FRAME_ONLY_STRONG` exactly for each transformed triple;
- sum both frame-only structural costs and the frozen wrapper charge;
- retain the unchanged batch `Lambda = Lambda_A + Lambda_B`.

No donor shortlist is used for the final comparator. The donor envelope at Lambda `L` is the minimum donor cost among all donor points with `Lambda <= L + 1e-12`.

### D2 — absorbed R6B transformation-reuse donor

On the untransformed ten-partition batch, recompute the proof-valid R6B shared-transformation comparator for every partition exactly as R6D does. Add every valid R6B reuse point to the donor pool at its partition Lambda.

The strongest donor envelope is the minimum over D1 and D2. If D2 is absent for a partition, that does not invalidate D1.

## R6G candidate

For every transform in the same complete grammar and every 3+3 partition:

- transform the two triples with the same signed conjugation and coefficient update;
- compute the exact TARE3 joint optimum for each transformed triple with the frozen exact objective from `MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md` plus Errata 1-3;
- sum both exact-joint costs and the same wrapper charge;
- compare the point against the strongest donor envelope at the candidate's Lambda.

The exhaustive candidate scan may use the sparse exact-cost implementation frozen by R6E only if hostile equivalence to the original exact solver passes. Every strict candidate used for support must then be reconstructed with the original proof-producing exact solver and all witness checks must pass.

There is no candidate-blind transform shortlist in R6G: the scientific operation being tested is precisely joint transform/partition/TARE-representation selection. The donor is protected from unfairness by receiving the complete transform grammar and the complete ten-partition envelope first.

## Deterministic selection and receipt

A strict point has

`delta = C_donor_envelope - C_candidate > 0`.

Sort strict points by:

1. descending `delta`;
2. ascending Lambda;
3. lexicographic transform id;
4. lexicographic partition.

The receipt must report per subject:

- source blob identity;
- six source indices;
- transform grammar cardinality;
- donor point count and donor-envelope witness for the best strict point;
- candidate point count;
- strict point count;
- best strict point with original exact-joint witnesses;
- CNOT sign/round-trip/symplectic hostile checks;
- coefficient-sign and Lambda-invariance checks;
- original-vs-sparse exact-cost hostile equivalence;
- frame-only fast-vs-original boundary/reference checks.

## Development conjunction

`MAX_R6G_JOINT_CLIFFORD_TARE3_COOPT_SUPPORTED__NOT_R6` requires all of:

1. complete transform grammar on both open subjects;
2. exactly ten unordered 3+3 partitions per complete batch;
3. source blob identity and coefficient/Lambda invariance gates pass;
4. hostile signed-CNOT checks pass;
5. sparse exact costs match original exact solver and brute-force hostile panels;
6. donor frame-only implementation is bound to the original `B_FRAME_ONLY_STRONG` implementation on deterministic reference rows;
7. all strict candidate witnesses are reconstructed by the original exact solver and pass;
8. at least one strict budget-matched point exists on H4;
9. at least one strict budget-matched point exists on equilibrium N2;
10. stretched-N2 remains unread.

If only one open subject has a strict point, preserve a partial matched-counterfactual result and do not promote. If neither has a strict point, close the full identity/single-CNOT joint-cooptimization grammar and return the residual to recursive method-language diagnosis.

## Novelty and R6 authority

R6G assigns zero novelty credit and cannot self-authorize R6. A positive R6G result only establishes open-subject structural method value beyond the strongest frozen frame-only/single-CNOT/reuse donor envelope.

Before any protected stretched-N2 access, a positive R6G path must still freeze and pass:

1. circuit-level / non-compensatory resource instantiation of the selected coupled operation;
2. strongest-donor replay including current global Clifford / symplectic compilation literature;
3. final hostile novelty subtraction identifying only the residual coupled capability, if any;
4. a new prospective protocol frozen before protected access;
5. primary plus structurally independent replay on the protected subject.

No earlier negative, erratum, comparator or authority ceiling is weakened by this protocol.
