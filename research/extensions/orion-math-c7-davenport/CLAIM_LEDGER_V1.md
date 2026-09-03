# C7^3 Davenport frontier claim ledger V1

Scientific scope: bounded first-wave experiment only.  Execution receipts never self-authorize novelty, priority, publication, or generalization.

| ID | Claim | Status | Boundary / warrant |
|---|---|---|---|
| C7-A1 | The Edel–Elsholtz–Geroldinger–Kubertin–Rackham odd-`n` `V3` construction has the nine declared support points, each with multiplicity `n-1`, and no zero-sum subsequence of length `n`. | **DONOR-OWNED** | Lemma 3.4, QJM 58 (2007), DOI 10.1093/qmath/ham003. |
| C7-A2 | Applying donor Lemma 2.2(2) at `n=7`, anchor `(2,0,1)`, yields the declared 48-term sequence with no nonempty zero-sum subsequence of length at most seven. | **DERIVED + EXACTLY RECHECKED** | Donor implication plus both local exact predicates in `verify_c7_44.py`. |
| C7-A3 | Deleting `(0,2,0)` once and `(1,1,0)` three times leaves the declared length-44 sequence with total sum zero. | **PROVEN / MACHINE-CHECKED** | Direct modular arithmetic and exact reconstruction. |
| C7-A4 | The declared length-44 sequence has no nonempty zero-sum subsequence of length `1..7`. | **PROVEN / TWO EXACT ALGORITHMS** | Reachable-sum DP and independent support-count enumeration agree. |
| C7-A5 | `44 not in C_0(C_7^3)`. | **PROVEN BOUNDED CONSEQUENCE** | Immediate from C7-A3–A4 under the standard definition of `C_0`. |
| C7-A6 | The literal ORION-04 `p=5` length-31 short-zero obstruction strategy does not extend to the analogous length 44 statement at `p=7`. | **REFUTED STRATEGY ANALOGUE** | C7-A5 is an explicit counterexample to that analogue. |
| C7-A7 | The witness has exact zero-sum packing number `zz(S)=5`. | **PROVEN / CERTIFICATE** | Five explicit disjoint zero-sum blocks cover all 44 terms; C7-A4 forces every nonempty zero-sum block to have length at least eight, so six would require at least 48 terms. |
| C7-A8 | The witness proves `D_4(C_7^3)>=44`. | **FALSE / FORBIDDEN INFERENCE** | C7-A7 gives `zz(S)=5`, not `<=4`; it is not a fourth-generalized-Davenport lower-bound witness. |
| C7-A9 | `D_4(C_7^3)=43`. | **OPEN** | Freeze–Schmid supplies the candidate lower bound; this wave does not establish the matching upper bound. |
| C7-A10 | There exists a length-44 zero-sum sequence over `C_7^3` with `zz<=4` (frontier atom B7). | **OPEN / NEXT FALSIFICATION GATE** | A `YES` would immediately force `D_4(C_7^3)>=44`; a `NO` alone is not yet an upper-bound theorem. |
| C7-A11 | `44 not in C_0(C_7^3)` is new or first in the literature. | **CANNOT_CHECK / NOT CLAIMED** | Current donor/literature search is not an exhaustive priority certificate. |
| C7-A12 | ORION harness execution supplies independent mathematical peer review. | **FORBIDDEN** | Harness receipts provide execution/provenance authority only. |

## Current terminal

`A7_REFUTED_BY_EXPLICIT_44_TERM_WITNESS__B7_REOPENED`

The negative result is retained as a frontier advance: it eliminates a tempting but false transport of the `p=5` proof architecture and identifies packing number, rather than short-zero-freeness alone, as the next load-bearing discriminator.
