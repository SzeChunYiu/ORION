# P10 Cross-Revision Analysis Amendment V1

Status: **FROZEN BEFORE SOURCE OR TARGET NATIVE OUTCOMES**

Frozen: 2026-08-20

This amendment makes the comparison in `P10_CROSS_REVISION_TARGET_FREEZE_V1.md` exact.

## Matched held-module training

For every target top module `d` with eligible target transitions:

- B1 is trained only on **source-revision V2.1 source transitions from modules other than `d`**;
- B4 is trained only on **source-revision native-state-eligible transitions from modules other than `d`**;
- B4 regularization is selected using the already-frozen nested leave-one-training-module-out source log-loss procedure;
- the resulting source-trained B1/B4 are evaluated both on source-revision eligible transitions from held module `d` and target-revision eligible transitions from held module `d`;
- no target label, state, module statistic or result participates in fitting or C selection.

This preserves the original leave-top-module-out challenge while adding temporal/ecosystem shift.

## Aggregate source and target metrics

Pool predictions over all evaluable held-module folds, with every transition counted once in its own held-module fold.

Define:

- `source_B1`, `source_B4`: pooled source-revision held-module accuracies under the matched training rule;
- `target_B1`, `target_B4`: pooled target-revision held-module accuracies;
- `B1_absolute_degradation = abs(target_B1 - source_B1)`;
- `B4_absolute_degradation = abs(target_B4 - source_B4)`.

Use a deterministic 10,000-resample target-module block bootstrap with seed `914039` for target `B4-B1`.

## Target population and coverage

The target population is every corrected V2.1 transition projected at target revision `d77ef0741c6da1ff12df68fb4145ea0ae0850c54` from the surviving paths in the exact 457-path source manifest. Missing paths count against path coverage. Native eligibility is eligible target traces divided by target projected transitions in surviving paths.

Require both:

- path coverage >=80% of the 457 frozen paths;
- native target transition coverage >=80%.

## Positive terminal

`STRUCTURAL_COORDINATES_CROSS_REVISION_ROBUSTNESS_SUPPORTED` requires:

1. the source native-state primary result itself is positive under its frozen gate;
2. target path coverage >=80%;
3. target native transition coverage >=80%;
4. target B4 accuracy > target B1 accuracy;
5. B4 absolute degradation < B1 absolute degradation;
6. target module-block bootstrap lower 95% bound for B4-B1 >0;
7. all target revision/toolchain/source/receipt checks pass;
8. no target refitting.

All source and target metrics are reported even when the terminal fails.
