# MAX-R6L Erratum 1 — conservative empty-envelope comparator

Date: 2026-08-21
Parent protocol: `MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_PROTOCOL.md`
Status: FROZEN AFTER IDENTIFYING AN EMPTY-COMPARATOR EDGE IN DEVELOPMENT, BEFORE ANY R6L PROMOTION OR PROTECTED-SUBJECT USE.

## Problem

The parent protocol compares an R6L point at normalization `Lambda_c` with the minimum incumbent cost among known donor points satisfying `Lambda_d <= Lambda_c + 1e-12`.

A candidate can legitimately improve normalization below every previously registered two-M3 donor point. In that case the eligible incumbent set is empty, so the parent rule is undefined. This is a protocol-completeness defect, not evidence of scientific failure or success.

## Conservative repair

No gate is weakened.

For every candidate point:

1. if at least one incumbent point satisfies `Lambda_d <= Lambda_c + 1e-12`, use the parent lower-envelope rule unchanged;
2. if that set is empty, compare against the **global minimum structural cost across the entire frozen incumbent point set**, regardless of its worse normalization.

Thus an empty-envelope candidate must beat a donor cost that is allowed to violate the candidate's normalization budget. This is strictly harder than ordinary Pareto comparison and cannot create a positive by relaxing the donor.

The receipt must record `comparator_mode` as either `MATCHED_LOWER_ENVELOPE` or `CONSERVATIVE_GLOBAL_COST_FLOOR` and serialize the donor witness used.

## Non-compensatory rotation coordinate

The parent rotation gate remains unchanged: R6L uses exactly 9 Uanti arbitrary rotations and may not claim support unless this count is no worse than the compared two-M3 incumbent's 10 rotations. The conservative global-cost fallback does not waive this coordinate.

## Authority

This erratum changes no selector, matching, candidate grammar, donor capability, success threshold, novelty rule or R6 authority. It only replaces an undefined comparator case with a stronger fail-closed comparator. Protected stretched-N2 remains unread.
