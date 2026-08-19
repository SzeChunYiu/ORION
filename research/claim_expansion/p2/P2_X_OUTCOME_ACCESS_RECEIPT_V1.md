# P2-X Protected Outcome Access Receipt V1

Date: 2026-08-19  
Parent: #530

## Frozen before protected outcome access

- protocol/baseline/schema/dev freeze merged: `9c43639fba5c845010f573aaec3a31e9d6d55062`;
- protected identity freeze: commit `4ce9c0ed7c4ef1d1325c97ceb9e8622966118a86`;
- contamination/exclusion manifest: commit `b518a0344fdf6c58f25b899597167e71f74ca7e5`;
- protected generator: commit `720cea4ab74eb80ce4fcaaafc2e041ed73b71e3d`;
- frozen controller/scoring implementation: `p2_x_execution.py` from merged pre-outcome subject (source commit `356588204c90f3810d129b3883befb0763e41b87`);
- protected analysis: commit `038373960648b4e1379f67146c1716eb132f8137`.

## Pre-access state

- protected case IDs and seed commitments frozen: YES;
- protected case/gold aggregate generated or inspected before this receipt: NO;
- primary ESCD, +0.10 practical margin, non-regression margins and B3 boundary frozen: YES;
- route-order permutation and held-out non-material decoy rules frozen: YES;
- existing P2 external Wide outcome excluded from case generation/tuning: YES.

## Authorized operation

Generate the complete 400-case protected bundle once, run B1/B2/B3/P2-X on exactly the same bundle, apply the frozen analysis, and preserve all cases and null/harmful outcomes.

Any controller/generator/metric/margin/analysis change after this receipt requires a new V2 protocol and leaves V1 immutable.

Terminal: `P2_X_PROTECTED_OUTCOME_ACCESS_AUTHORIZED_V1`.
