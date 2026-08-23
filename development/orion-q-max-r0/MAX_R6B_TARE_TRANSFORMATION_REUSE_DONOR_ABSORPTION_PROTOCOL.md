# ORION-Q MAX-R6B TARE transformation-reuse donor absorption protocol

Date: 2026-08-21
Parent programme: #679
Predecessor negative: `research/failures/2026-08-orion-q-exact-tare3-frame-only-collapse/README.md`
Status: frozen before reuse-search outcome generation.
Authority: donor absorption / method-language diagnosis only; not R6 and no novelty authority.

## Why this lane exists

The exact single-block TARE-3 joint-frame compiler passed hostile exactness and beat the canonical TARE frame on both open chemistry subjects, but tied the exact strengthened frame-only donor on every frozen top-four row. The protected stretched-N2 prospective discriminator therefore remained closed.

The next question is whether the incumbent itself is still too weak because it treats independently optimized TARE blocks as unrelated circuits.

TARE already owns the relevant reuse capability. Its additional-LCU example explicitly reuses `U_tag` and `U_correct` when the transformation operators coincide. Therefore this lane assigns **zero novelty credit** to transformation reuse, common-Clifford extraction, LCU composition, auxiliary-frame freedom, or common-subcircuit factorization. Generic Clifford extraction/absorption is also donor capability.

The purpose of MAX-R6B is only to give this donor capability first right of refusal on the open chemistry evidence before another original method-language revision is attempted.

## Frozen subjects

Only the already-open subjects are used:

- H4 / cc-pVDZ / 2.0au / DUCC3, blob `b98792b1055dbac0ebf2a7576f72412e3e4ac6c5`, 8 qubits;
- equilibrium N2 / cc-pVTZ / 6e6o / DUCC2, blob `15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba`, 12 qubits.

The stretched-N2 R6 discriminator blob `6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd` remains unread.

## Frozen two-block batch selection

Reuse is tested on two disjoint three-term TARE blocks per subject.

Use the unchanged candidate-blind P10 scan (`WINDOW=12`) over every non-direct triple. Within each 12-term window retain the best improving triple under the already-frozen P10 ordering

`(-rank2_fraction, -rank2_delta, term_indices)`.

Sort the resulting window champions by the same ordering. The batch is exactly the first two champions. Because they originate in distinct non-overlapping 12-term windows, the six term indices are disjoint.

If fewer than two windows contain an improving triple, that subject is donor-reuse negative. No post-outcome substitute window or triple is permitted.

## Representation and phase convention

A three-term representation has target Pauli strings `P_k`, auxiliary pairwise-anticommuting Hermitian Pauli strings `R_k`, Tag generators `S_0,S_1`, distinct two-bit labels `c_k`, and correction Pauli strings `T_k` satisfying the TARE mapping up to the frozen Pauli phase correction.

For Hermitian Paulis use the binary-symplectic convention

`P(x,z) = i^(x dot z) X^x Z^z`.

For each branch serialize the phase exponent `g_k in {0,1,2,3}` such that

`i^g_k T_k R_k = P_k`.

Two blocks have an identical reusable correction transformation only when their ordered triples `(g_k,T_k)` are identical, not merely when the unsigned binary strings `T_k` match.

## Complete donor signature library

For each of the two selected source blocks build the complete exact Uanti-minimum frame library characterized by Exact-DP Erratum 3:

1. every system qubit `q`;
2. every ordered permutation of the weight-one frame `(X_q,Y_q,Z_q)`;
3. every target permutation;
4. every admissible dependent-frame label assignment, i.e. every permutation of labels `(1,2,3)`;
5. exact minimum-weight Tag generators for those labels.

For every library row derive and serialize:

- `R_0,R_1,R_2`;
- `S_0,S_1`;
- labels;
- target permutation;
- signed correction signature `((g_0,T_0),(g_1,T_1),(g_2,T_2))`;
- exact structural support cost.

This is donor capability. No row receives novelty credit.

## Reuse transfer

For every signature produced from either selected source block, test whether the **same** `S_0,S_1`, labels, and signed correction signature can represent the other block.

For every target permutation of the destination block:

1. derive the binary auxiliary strings from `R_k = P_k T_k`;
2. require pairwise anticommutation;
3. require the common `S_0,S_1` to induce exactly the same two-bit labels;
4. recompute the Pauli phase exponents and require equality to the source signed correction signature;
5. choose the exact best Uanti central axis for that destination frame;
6. reconstruct every mapping as a proof witness.

A transferable row therefore has literally common `U_tag` and `U_correct` under the frozen structural model. This is the reuse condition already owned by the TARE donor, applied exhaustively to the open chemistry batch.

## Resource accounting

For two independently implemented TARE blocks, the strongest fixed-block donor comparator is

`C_separate = C_frame_only(block_A) + C_frame_only(block_B)`.

For a valid reusable signature, the common Tag and common correction are paid once:

`C_reuse = 2(w(S_0)+w(S_1)) + sum_k w(T_k) + C_Uanti(A) + C_Uanti(B)`.

The phase factors carry no Pauli support but must match exactly for reuse validity.

The matched batch holds fixed:

- the six target terms and their two three-term groupings;
- both coefficient vectors;
- each block's TARE normalization `sqrt(3)||alpha||_2`;
- two 5-exponential Uanti realizations (10 total);
- two-bit internal TARE label width;
- the two-block outer LCU cardinality and its address width.

Only the structurally reusable Tag/correction support is allowed to decrease.

## Hostile verification

Before any chemistry claim, deterministic reminted small-n panels must verify:

- signed Pauli multiplication / correction phases against explicit local Pauli multiplication;
- source-signature reconstruction;
- transfer rejection when binary `T_k` matches but the phase exponent differs;
- transfer rejection when labels or anticommutation fail;
- exact recomputation of `C_separate` and `C_reuse` from the serialized witnesses.

No failure may be coerced to a positive terminal.

## Development outcome

For each open subject report every selected batch and the best donor-reuse witness, or an explicit no-transfer result.

`MAX_R6B_TARE_REUSE_DONOR_POSITIVE` requires:

1. two frozen window champions exist on both H4 and equilibrium N2;
2. all source and transferred proof witnesses pass;
3. the stretched-N2 discriminator remains unread;
4. `C_reuse <= C_separate` on both subjects;
5. `C_reuse < C_separate` on at least one subject.

A positive is immediately absorbed into the incumbent and receives **no novelty credit**. A negative is preserved and rules out this donor-strengthening move on the frozen batch.

Either way R6 remains closed. After absorption/closure, ORION and ORION-Q must diagnose the next residual against this stronger incumbent before any new prospective protocol is considered.
