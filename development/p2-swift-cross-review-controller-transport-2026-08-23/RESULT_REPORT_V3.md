# P2 SWIFT cross-review controller transport V3

**Exact terminal:** `P2_SWIFT_V3_CROSS_REVIEW_CONTROLLER_FAILS_ONE_OR_MORE_PUBLIC_DEVELOPMENT_GATES_REQUIRES_SUCCESSOR`

**Preserved Zenodo terminal:** `P2_ZENODO_V2_ACTIVE_COMPARATOR_TIES_OR_WINS_REQUIRES_CONTROLLER_SUCCESSOR`

## Aggregate decision

| Gate | Result |
|---|---|
| `G1_BINDING` | PASS |
| `G2_POPULATION` | PASS |
| `G3_PRIMARY_MARGIN` | FAIL |
| `G4_WORK_SAVING` | FAIL |
| `G5_HARM` | PASS |
| `G6_ABSOLUTE_WORK_SAVING` | PASS |

- Unweighted mean candidate-minus-u4 recall@10%: `-0.021717971642` (required `>= +0.05`).
- Unweighted mean candidate-minus-u4 WSS@95: `-0.050396333672` (required `>= 0`).
- Worst review: `Fluoride`, recall@10% difference `-0.039215686275` (harm gate passed).
- Candidate WSS@95 was positive in every review, but u4 required less screening to 95% recall in every review.

## Review-level results

| Review | N | Included | Candidate R@10 | u4 R@10 | Difference | Candidate WSS95 | u4 WSS95 | Difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BPA | 7,697 | 111 | 0.864865 | 0.891892 | -0.027027 | 0.751481 | 0.836189 | -0.084708 |
| Fluoride | 4,477 | 51 | 0.941176 | 0.980392 | -0.039216 | 0.806154 | 0.899966 | -0.093813 |
| Neuropain | 29,157 | 5,011 | 0.471762 | 0.477350 | -0.005588 | 0.638205 | 0.651993 | -0.013787 |
| PFOS-PFOA | 6,309 | 95 | 0.915789 | 0.936842 | -0.021053 | 0.838572 | 0.846497 | -0.007925 |
| Transgenerational | 48,601 | 764 | 0.816754 | 0.832461 | -0.015707 | 0.702248 | 0.753996 | -0.051748 |

## Scientific interpretation

The fixed logistic controller did **not** transport superiority from the earlier one-pool setting. The cadence-matched pinned u4 components had higher recall@10% and WSS@95 on every SWIFT review. Passing the harm and absolute-work-saving gates does not compensate for failure of the primary margin and relative work-saving gates.

This result is public-development evidence from five distinct review decisions. It is not cold-start evidence, exact ASReview application execution, protected confirmation, independent custody, or population transport. The maximum pairwise shared-content count was 68, so complete review independence is not claimed.

## Mechanics provenance

V1 and V2 are retained `CANNOT_CHECK` population-binding failures and ran no models. V3 corrected the label-independent content-identity audit before any model outcome, but after class counts had been opened. Their failure diagnoses remain first-class artifacts.

## Next discriminator

`NEXT_CONTROLLER_SUCCESSOR_PROTOCOL_V4.json` freezes a post-outcome 2x2 representation-by-learner/balancer factorization. It cannot promote a new controller on SWIFT; any selected mechanism requires a content-disjoint outcome-unopened review family.
