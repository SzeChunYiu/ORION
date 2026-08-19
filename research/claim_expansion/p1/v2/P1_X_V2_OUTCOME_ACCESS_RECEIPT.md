# P1-X V2 Protected Outcome Access Receipt

Date: 2026-08-19  
Parent: #529

## Frozen before V2 outcome access

- V2 replication protocol: commit `539d6dc2e9d296cc1ff00fabf4c66e19d49405db`;
- V2 protected identity freeze: commit `647a0cb41dec79a1ad34cd0cec9508e6c9c22e7d`;
- V2 comparator-only repair: commit `25c03acb43fa8f9a8030125221fe6a9644070a7b`;
- V2 disjoint protected generator: commit `751d0b0c0e18e9b9003d0ac33fe0bd35676157b1`;
- V2 frozen analysis: commit `8241b4c849774792954ff3a093564407a34fadc8`;
- V2 dev/preflight regression tests: commit `4b0fa6449ae1996f9dc2a17cb48eeb9d5d2eb174`.

## Pre-access declarations

- V1 outcomes are known and remain immutable.
- V2 protected case IDs and seed commitments are disjoint from V1.
- V2 protected gold/aggregate outcomes have not been generated or inspected before this receipt.
- P1-X/B3 semantics are byte-reused from V1.
- B1/B2 change only the identified `statuses.values()` clean-control bug.
- Primary outcome, +0.10 margin, non-regression margins, and analysis policy are unchanged.

## Authorized operation

Generate the complete 400-case V2 bundle once, run the four frozen V2 arms on all 400 cases, analyze using the frozen V2 analysis subject, and preserve every outcome.

No post-access controller/generator/margin/analysis change is allowed within V2.

Terminal: `P1_X_V2_PROTECTED_OUTCOME_ACCESS_AUTHORIZED`.
