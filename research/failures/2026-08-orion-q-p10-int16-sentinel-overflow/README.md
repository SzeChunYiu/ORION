# ORION-Q P10 candidate-blind optimizer — NumPy sentinel overflow

## Observed

GitHub Actions run `32399157610`, job `96522950228`, failed before candidate generation at module initialization:

`np.full((4,4,4,3,32), 1_000_000_000, dtype=np.int16)`

NumPy 2.5.2 raises `OverflowError` because the sentinel is outside the signed int16 range.

## Failure

The scientific search space, discriminator, protected-data boundary and result gates were never executed. This is not a scientific negative. The implementation chose a storage dtype inconsistent with its declared infinity sentinel.

## Failure class

`EXECUTION_NUMERIC_REPRESENTATION_BOUNDARY -> SENTINEL_DTYPE_RANGE_MISMATCH`

## Correct response

- preserve the failed run;
- do not alter any scientific protocol/gate;
- widen only the local cost table from int16 to int32 (the same dtype already used by the dynamic-programming accumulators);
- rerun the frozen optimizer;
- treat any later scientific negative separately from this execution failure.

## General lesson candidate

Exact-search harnesses should assert sentinel representability in every storage dtype. Library upgrades that tighten integer-casting behavior can expose latent fail-open/undefined numeric assumptions before the scientific algorithm starts.
