# ORION-Q P10 candidate-blind optimizer — cumulative int32 sentinel overflow

## Observed

Hostile review of the frozen MAX-R6 P10 candidate-blind optimizer found that the earlier int16 repair was still numerically insufficient. The code used `INF = 1_000_000_000` with int32 dynamic-programming accumulators on subjects reaching 12 qubits.

The earlier regression asserted only that one `INF` value fits in int32. It did not cover the recurrence itself: unreachable-state entries may add an `INF`-scale local value once per qubit before minimization. `12 * INF = 12_000_000_000`, which is outside signed int32 range. Wrapped negative values could therefore win `argmin` and fabricate a low-cost witness.

## Failure

This is an implementation/numeric-integrity defect, not a scientific negative or positive. The stretched-N2 protected subject was not opened by this finding, and no gate or comparator was changed.

## Failure class

`EXECUTION_NUMERIC_REPRESENTATION_BOUNDARY -> CUMULATIVE_SENTINEL_DTYPE_RANGE_MISMATCH`

## Correct response

- preserve the earlier int16 failure record and this second erratum separately;
- keep `INF`, search grammar, comparators, evidence budget, and scientific gates unchanged;
- widen the local table and both DP accumulator families to int64;
- strengthen the regression to require representability of `max_subject_qubits * INF` rather than only `INF`;
- replay the unchanged candidate-blind optimizer before accepting any P10 evidence receipt.

## Authority

`IMPLEMENTATION_ERRATUM_ONLY__NO_R6_OR_NOVELTY_AUTHORITY`
