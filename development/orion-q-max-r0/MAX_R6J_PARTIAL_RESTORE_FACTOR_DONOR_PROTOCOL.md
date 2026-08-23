# MAX-R6J partial Restore-factor donor absorption protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6J OPEN-SUBJECT OUTCOME.
Authority: donor-absorption development only; not R6 and no novelty authority.

## Residual and donor ownership

R6H gives the TARE donor the direct circuit factorization of a common Tag/Tag-dagger pair across two outer-LCU-selected TARE-3 blocks while keeping each block's Restore family branch-specific. The remaining R6H cost is dominated by those two Restore families.

R6J gives the donor the next direct common-subcircuit factorization before any original method receives credit:

> for each TARE label branch k, factor an arbitrary common Pauli component `G_k` from the two block-specific Restore Paulis, while preserving exact Hermitian-Pauli phases in the residual block-specific corrections.

This is donor-owned circuit factoring and receives zero novelty credit. It is not an original ORION-Q capability.

## Frozen subjects and batch

Use only already-open H4 and equilibrium-N2 evidence. Reconstruct exactly the R6B/R6D six-term batch from the first two deterministic disjoint R6B window champions and enumerate exactly the ten unordered 3+3 partitions. Fewer than six unique source terms is a clean negative; no substitute terms are permitted.

The stretched-N2 prospective discriminator remains unread.

## Representation grammar

Use exactly the complete R6H weight-one dependent TARE-3 donor grammar for each block:

- choose a system qubit q;
- enumerate all permutations of the weight-one `{X_q,Y_q,Z_q}` pairwise-anticommuting frame;
- enumerate all dependent distinct nonzero 2-bit label triples;
- solve the minimum-weight Tag strings `S0,S1` exactly;
- enumerate all target permutations;
- derive every Restore Pauli and exact Hermitian multiplication phase.

Two block representations may enter R6J only when they share exactly the R6H Tag key `K=(S0,S1,labels)`. Their frame permutations, target permutations, Restore strings and Restore phases may differ.

Unlike R6H, R6J must not retain only the individually minimum-Restore representation for a Tag key before pairing: it jointly enumerates every representation pair under the common Tag key because a locally more expensive Restore can expose more common Pauli factors and win globally.

## Exact branchwise Restore factorization

For each label branch k, let the original signed Hermitian Restore operations be

`i^(a_k) T_Ak` and `i^(b_k) T_Bk`.

Choose one common Hermitian Pauli `G_k` and residual Hermitian Paulis `U_Ak,U_Bk` such that exact signed identities hold:

`i^(g_Ak) G_k U_Ak = T_Ak`

`i^(g_Bk) G_k U_Bk = T_Bk`.

The residual controlled phases are serialized explicitly and are not discarded. Under the same frozen structural-support objective used by R6B/R6H, phase controls have no separate support coordinate; later circuit-level non-compensatory instantiation must account for any physical phase-control cost before R6 authority.

For fixed `T_Ak,T_Bk`, the support-minimizing common factor is exact and separable by system qubit. At each qubit:

- if both local Restore letters are the same non-identity Pauli, put that letter in `G_k` and identity in both residuals, reducing local support from 2 to 1;
- otherwise use identity in `G_k`, leaving the two original local letters in the residuals.

Any other non-identity common local choice is never cheaper: when the two letters differ it only transfers one support unit from a residual into `G_k` without reducing total support.

Therefore

`C_FACTOR_BRANCH(k) = w(T_Ak)+w(T_Bk)-M_k`,

where `M_k` is the number of qubits on which `T_Ak` and `T_Bk` contain the same non-identity Hermitian Pauli letter. The implementation must still reconstruct `G_k,U_Ak,U_Bk` and exact phases rather than relying only on this formula.

## R6J structural objective

For one compatible representation pair,

`C_R6J = 2(w(S0)+w(S1)) + sum_k [w(G_k)+w(U_Ak)+w(U_Bk)]`.

The weight-one frame family has zero Uanti parity-support charge. The common Tag pair is paid once, exactly as in R6H.

Minimize `C_R6J` jointly over all compatible representation pairs for each 3+3 partition.

## Strongest incumbent envelope

For every partition, independently recompute:

1. `B_FRAME_ONLY_STRONG` for both blocks;
2. proof-valid full R6B transformation reuse when available;
3. the exact R6H partial-Tag donor optimum.

The partition incumbent is the minimum of those costs. Compare every R6J point against the lower incumbent envelope over all partition points with `Lambda <= candidate Lambda + 1e-12`.

Concurrent pre-outcome R6F/R6G lanes remain live counterfactuals. If either later produces a stronger positive incumbent, that capability must be absorbed and R6J replayed against it before any prospective promotion.

## Hostile and proof gates

Before chemistry evaluation R6J must pass all of:

1. the R6B signed Hermitian-Pauli multiplication/Restore-phase hostile suite;
2. the R6H common-Tag / different-Restore hostile suite;
3. a synthetic branch where identical non-identity local Restore letters are factored and reduce support by exactly one;
4. a synthetic branch with two different non-identity local letters where factorization gives zero saving;
5. exact reconstruction `G_k U_jk = i^e T_jk` including phase for both blocks on every branch;
6. exactly ten unordered 3+3 partitions for each complete chemistry batch;
7. observed source blobs match frozen identities;
8. every retained frame is the frozen weight-one pairwise-anticommuting family and every Tag key reproduces its labels;
9. both selected blocks are disjoint;
10. cost recomputation equals one shared Tag pair plus all factored branch supports;
11. R6H/R6B/frame-only incumbent replay passes;
12. stretched-N2 remains unread.

## Development sign

A strict R6J point requires

`C_R6J < C_incumbent_envelope`

at matched-or-better Lambda.

`MAX_R6J_PARTIAL_RESTORE_FACTOR_DONOR_POSITIVE__ABSORB__NOT_R6` requires at least one strict point on both H4 and equilibrium N2 plus all integrity gates. Every positive saving is donor capability and receives zero novelty credit.

A one-subject positive is preserved as a matched counterfactual only. If neither subject is strict, this donor factoring route is closed and recursion continues to a new method-language atom.

## Authority ceiling

R6J can never set `r6_earned=true`. A positive R6J result is immediately absorbed into the incumbent. Any original successor must beat the absorbed R6J envelope, then pass circuit/non-compensatory resource instantiation, current donor/literature replay and final novelty subtraction. Only after those gates are frozen and passed may a new prospective stretched-N2 protocol be frozen and executed by primary plus structurally independent replay.
