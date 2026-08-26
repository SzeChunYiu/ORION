# ORION-16–ORION-25 top-tier external-promotion gate V1

**Owner:** #977  
**Normative programme:** `../TOP_TIER_PROMOTION_PROGRAM_V1.md`

This gate sits **above**, and does not invalidate, existing controlled/peer-review-ready terminals.

## Gate semantics

- `CONTROLLED_CORE_VALID`: the paper's already-authorized bounded result remains scientifically valid.
- `EXTERNAL_PROMOTION_PENDING`: the higher target exists as a frozen research claim, but at least one external/theoretical promotion gate remains open.
- `SCIENTIFIC_OBJECT_NOT_YET_EARNED`: the paper does not yet possess the protected result required for its intended standalone scientific object.
- `TOP_TIER_SUBMISSION_READY`: reserved for a later content-addressed closure receipt proving all common and paper-specific gates.

A `TOP_TIER_PROMOTION_V1.md` planning file is never authority for the final terminal.

## Current wave state

| Paper | Current higher-level state | Existing controlled result preserved? |
|---|---|---|
| ORION-16 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-17 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-18 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-19 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-20 | `SCIENTIFIC_OBJECT_NOT_YET_EARNED` | historical negatives/bounded evidence yes |
| ORION-21 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-22 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-23 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-24 | `EXTERNAL_PROMOTION_PENDING` | yes |
| ORION-25 | `SCIENTIFIC_OBJECT_NOT_YET_EARNED` | harness engineering evidence only; no protected paper result |

## Promotion receipt requirement

A future `TOP_TIER_SUBMISSION_READY` receipt must bind:

1. exact commit;
2. current literature/donor saturation artifact;
3. paper-specific promotion protocol version;
4. protected protocol/evaluator/task identities;
5. raw and derived result digests;
6. independent verification/adjudication receipts;
7. hostile-review disposition;
8. reproduction/clean-environment receipt;
9. manuscript/claim-ledger/result-macro digests;
10. venue-facing submission package.

Missing external authority or a still-open nearest-work route yields `CANNOT_CHECK`, not implicit promotion.
