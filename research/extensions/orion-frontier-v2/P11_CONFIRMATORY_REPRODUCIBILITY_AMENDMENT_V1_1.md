# P11 Confirmatory Reproducibility Amendment V1.1

Status: **POST-FIRST-EXECUTION INFRASTRUCTURE AMENDMENT; NO SCIENTIFIC GATE CHANGE**
Frozen: 2026-08-20 immediately after the first confirmatory execution and before any replay claim.

## Defect discovered

The V1 runner stored `fit_wall_seconds` inside the authoritative result JSON. Wall-clock timing is hardware/scheduler dependent, so an otherwise deterministic scientific replay cannot be byte-identical.

This is a provenance/schema defect, not a scientific discrepancy.

## Allowed repair

1. Remove wall-clock fields from the canonical scientific result payload.
2. If desired, write timing observations to a separate `*_TIMING_NONAUTHORITATIVE_*.json` file that is explicitly excluded from deterministic identity checks.
3. Keep every scientific element unchanged:
   - master seed `914311`;
   - cells;
   - query samples;
   - train/test samples;
   - train sizes;
   - learner and hyperparameters;
   - accuracy definitions;
   - 0.90 thresholds;
   - all positive/negative terminal gates;
   - theorem checks.

## Replay rule

After this amendment, execute the canonical runner twice from clean process state. The canonical scientific JSON must be byte-identical across the two executions. Timing sidecars may differ and have no scientific authority.

## Outcome boundary

The first execution had already occurred before this amendment. Therefore this amendment cannot change any scientific threshold or reinterpret a failed gate. It only makes the already-frozen deterministic-replay requirement technically representable.
