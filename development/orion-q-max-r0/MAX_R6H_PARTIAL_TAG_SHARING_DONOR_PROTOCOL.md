# MAX-R6H partial Tag-sharing donor absorption protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6H OPEN-SUBJECT OUTCOME.
Authority: donor-absorption development only; not R6 and no novelty authority.

## Motivation and donor ownership

The TARE v4 circuit is ordered `Tag -> Uanti -> Tag^dagger -> Restore` and the authors explicitly state that larger operators may be split into separate TARE block encodings and combined through an additional LCU step (arXiv:2601.05740v4, Sec. 4 / Fig. 2-3 and conclusion). R6B tested the stronger reuse condition in which two outer-LCU blocks shared the complete Tag plus signed Restore transformation. That route was negative because forcing the second block onto the same full transformation produced large Uanti support.

R6H gives the TARE donor a strictly weaker and therefore stronger reuse capability: **only the Tag basis and branch labels must be common; Restore remains block-specific.** This is direct circuit factoring of a common donor subcircuit and receives zero novelty credit.

If block `j` has the form `Restore_j Tag^dagger Uanti_j Tag`, and all selected blocks use the same `Tag`, then the outer selector can factor the common `Tag` and `Tag^dagger` outside the block-select operation while leaving `Uanti_j` and `Restore_j` branch-specific. R6H tests this donor capability before any original successor may claim value.

## Subjects and frozen batch

Use only already-open H4 and equilibrium-N2 evidence. The protected stretched-N2 discriminator remains unread.

For each subject reconstruct exactly the R6B/R6D six-term batch from the first two deterministic disjoint R6B window champions and enumerate exactly the ten unordered 3+3 partitions. Fewer than six unique terms is a clean negative; no substitute terms are permitted.

## Frozen representation grammar

For each three-term block, enumerate the complete **weight-one dependent TARE-3 donor family** already frozen in R6B:

- choose one system qubit `q`;
- use every permutation of the weight-one `{X_q,Y_q,Z_q}` anti-commuting frame;
- use every dependent distinct 2-bit label triple frozen by the exact TARE-3 protocol;
- solve minimum-weight Tag strings `S0,S1` exactly for that frame/label assignment;
- use every target permutation;
- derive each Restore string and exact Hermitian Pauli phase from the target/frame identity.

The grammar is fixed before outcome and is not enlarged post hoc.

## Partial Tag-sharing key and exact cost

A representation has Tag key

`K = (S0, S1, labels)`.

Two disjoint blocks are Tag-share compatible iff they have the same `K`. Their frames, target permutations, Restore strings and Restore phases may differ.

For a compatible pair, with weight-one frames so `C_Uanti_A=C_Uanti_B=0`, define

`C_PARTIAL_TAG = 2(w(S0)+w(S1)) + sum_k w(T_A,k) + sum_k w(T_B,k)`.

The Tag pair is paid exactly once for the two-block outer selection. This is compared with the independently implemented frame-only and full-transformation-reuse incumbents under the same structural support accounting.

For each Tag key and block keep only the minimum Restore-support representation, breaking ties lexicographically by frame/provenance and signed Restore witness. Then minimize `C_PARTIAL_TAG` over common keys.

## Strongest current donor comparator

For every one of the ten partitions, replay R6D and retain

- independent `B_FRAME_ONLY_STRONG` cost;
- proof-valid full R6B transformation-reuse cost when available.

The partition incumbent is the smaller of those costs. At each R6H candidate Lambda, compare against the lower envelope of all incumbent partition points with `Lambda <= candidate Lambda + 1e-12`.

R6F/R6G are concurrent pre-outcome recursive atoms. If either later produces a stronger positive donor/incumbent, it must be absorbed before any prospective promotion; R6H cannot bypass it.

## Hostile / proof gates

R6H must verify:

1. the signed Hermitian Pauli multiplication/Restore phase table from R6B;
2. exactly ten unordered 3+3 partitions for each complete batch;
3. source blob identity on both open subjects;
4. every retained frame is pairwise anti-commuting and weight one on a single qubit;
5. every retained `(S0,S1)` reproduces its three labels;
6. every signed Restore witness satisfies the exact Pauli identity;
7. the two selected blocks are disjoint;
8. the shared-cost recomputation equals one Tag pair plus both block-specific Restore supports;
9. the R6D incumbent replay has valid witnesses;
10. stretched-N2 remains unread.

A synthetic hostile pair with the same Tag but deliberately different Restore strings must be accepted, while a pair with a mismatched Tag key must be rejected. This prevents accidental reintroduction of R6B's full-Restore equality requirement.

## Development sign

For each subject a strict point requires

`C_PARTIAL_TAG < C_incumbent_envelope`

at matched-or-better Lambda.

`MAX_R6H_PARTIAL_TAG_SHARING_DONOR_POSITIVE__ABSORB__NOT_R6` requires at least one strict point on **both** H4 and equilibrium N2 plus all integrity gates. Any positive saving is donor capability and gets zero novelty credit.

If only one subject is strict, preserve a partial counterfactual but do not promote. If neither is strict, close this donor factorization route and recurse to the next method-language atom.

## Authority ceiling

R6H can never set `r6_earned=true`. A positive R6H result must first be absorbed into the incumbent. Any original successor must beat the absorbed R6H comparator, pass circuit/non-compensatory resource accounting, final donor/novelty subtraction, then a separately frozen prospective protocol and structurally independent protected-subject replay.
