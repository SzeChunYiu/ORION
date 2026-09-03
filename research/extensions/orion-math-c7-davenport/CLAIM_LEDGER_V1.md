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
| C7-A7 | The A7 witness has exact zero-sum packing number `zz(S)=5`. | **PROVEN / CERTIFICATE** | Five explicit disjoint zero-sum blocks cover all 44 terms; C7-A4 forces every nonempty zero-sum block to have length at least eight, so six would require at least 48 terms. |
| C7-A8 | The A7 witness proves `D_4(C_7^3)>=44`. | **FALSE / FORBIDDEN INFERENCE** | C7-A7 gives `zz(S)=5`, not `<=4`; it is not a fourth-generalized-Davenport lower-bound witness. |
| C7-A9 | `D_4(C_7^3)=43`. | **OPEN** | Freeze–Schmid supplies the candidate lower bound; this wave does not establish the matching upper bound. |
| C7-A10 | There exists a length-44 zero-sum sequence over `C_7^3` with `zz<=4` (global frontier atom B7). | **OPEN** | A `YES` would immediately force `D_4(C_7^3)>=44`; no global exclusion is claimed here. |
| C7-A11 | `44 not in C_0(C_7^3)` is new or first in the literature. | **CANNOT_CHECK / NOT CLAIMED** | Current donor/literature search is not an exhaustive priority certificate. |
| C7-A12 | ORION harness execution supplies independent mathematical peer review. | **FORBIDDEN** | Harness receipts provide execution/provenance authority only. |
| C7-B1 | The specialized Freeze–Schmid-derived zero-sum sequence `B43=e1^6 e2^6 e3^20 (e1+e2)^3 (e1+e3)^3 (e2+e3)^4 (2,1,1)` has length 43 and total sum zero. | **PROVEN / EXACT RECONSTRUCTION** | `verify_b7_one_split.py` checks the length-42 donor arithmetic and the completion term. |
| C7-B2 | `zz(B43)=4`. | **PROVEN / TWO EXACT BLOCK VOCABULARIES** | The complete zero-sum substate lattice has 479 states and 159 minimal atoms; searches over both atom blocks and all zero-sum substates find 4-packings and reject 5-packings. |
| C7-B3 | Each support type of `B43` has exactly 171 unordered nonzero one-term splits `v -> a+b`, giving 1197 labelled one-split moves. | **PROVEN / FINITE ENUMERATION** | Odd order gives the expected finite count; the verifier enumerates and cardinality-checks every move. |
| C7-B4 | For the seven source types, eligible base-block counts are `144,143,144,119,119,127,79`, and each residual-sum union covers `343/343` elements of `C_7^3`. | **EXACT FINITE COVER** | Complete substate enumeration plus exact complement 3-packing predicates in `verify_b7_one_split.py`. |
| C7-B5 | Every one of the 1197 labelled one-term split moves has an explicit five-block zero-sum partition. | **PROVEN / CERTIFICATE SWEEP** | The 343/343 covers construct a partition for every move; every generated block and exact multiset cover is rechecked. |
| C7-B6 | Every one-term split move has exact packing number `zz=5`. | **PROVEN BOUNDED THEOREM** | C7-B5 gives `zz>=5`; if a split had `>=6`, the two distinct blocks containing `a,b` merge under `a+b=v` to give `>=5` blocks in `B43`, contradicting C7-B2. |
| C7-B7 | The canonical `B43` one-term split neighbourhood contains a B7 witness with `zz<=4`. | **REFUTED / NO SURVIVOR IN BOUNDED NEIGHBOURHOOD** | C7-B6 closes all 1197 labelled moves. |
| C7-B8 | Global B7 is false. | **OPEN / FORBIDDEN PROMOTION** | Closing one semantic neighbourhood does not exclude multi-term exchanges, different extremal orbits, or unrelated length-44 sequences. |
| C7-B9 | The bounded one-split rigidity result is new or first in the literature. | **CANNOT_CHECK / NOT CLAIMED** | No exhaustive priority certificate has been established. |

## Current terminal

`A7_REFUTED__B7_S1_ONE_SPLIT_NEIGHBOURHOOD_CLOSED__GLOBAL_B7_OPEN`

The retained negative result changes the search strategy: short-zero-freeness alone is too weak at `p=7`, and the smallest exact perturbation of the canonical Freeze–Schmid extremal witness is packing-rigid.  The next frontier step must leave this one-edit basin rather than repeat it at greater computational cost.
