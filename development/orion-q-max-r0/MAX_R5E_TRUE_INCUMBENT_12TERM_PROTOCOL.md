# ORION-Q MAX-R5E true-incumbent 12-term controlled matching protocol

Date: 2026-08-20
Parent: #679 / #698
Branch: `shadow/orion-q-max-r0`
Status: frozen before MAX-R5E outcome generation.
Authority ceiling: N2 development only; cannot authorize fresh R5/R6.

## Reopen cause

MAX-R5D exposed useful larger-neighborhood structure but failed hostile baseline binding: its non-compensatory T gate was checked against pure adjacent all-TARE pairing instead of the already-absorbed R5C quartet incumbent. The first R5D `pass` is invalid and preserved in `MAX_R5D_BASELINE_BINDING_ERRATUM.md`.

## Incumbent object

The single jointly realizable baseline B* is the R5C **zero-slack quartet incumbent**:

1. terms sorted by descending coefficient magnitude with deterministic Pauli-key tie break;
2. every consecutive four-term quartet considers all three perfect matchings;
3. choose the matching with lexicographic `(Lambda, projected_T, controlled_CNOT, pattern_id)` minimum;
4. every TARE edge uses the exact controlled-CNOT auxiliary representation (`8 symplectic parity states x 2 Restore-base branches x 2 orientations`);
5. direct anticommuting edges use their own direct normalization and circuit.

All promotion coordinates are measured against this same B* object. No coordinate may use pure adjacent pairing or R5B's uncontrolled-optimal representation as its reference.

## Atomic questions

1. Does exact larger-neighborhood matching improve controlled CNOT by >=0.5% while keeping projected T <= B* and total normalization <=1% above B*?
2. Can the improvement be found without reducing B*'s direct anticommuting-block count?
3. Does exact controlled auxiliary optimization remain valid for every TARE edge in the selected matching?
4. Is the result robust to the R5D donor-baseline correction?

## Frozen search

### Aligned windows

Use contiguous **12-term windows**, beginning at term 0. Twelve is frozen because it is a multiple of the incumbent quartet size (3 complete quartets/window), so no B* pair is cut by an interior window boundary. The final even tail is one smaller exact window.

A full 12-term window has 10,395 perfect matchings; enumerate all of them.

### Local edge vector

For every candidate pair compute exactly:

`(Lambda, controlled_CNOT, projected_T, direct_flag)`

under R5C semantics. No scalarized weighted reward is permitted.

### Local frontier

Retain the exact nondominated set over:

- lower `Delta Lambda`;
- lower `Delta controlled_CNOT`;
- lower `Delta projected_T` (equivalently higher direct count).

Use an exact grouped Pareto algorithm; do not use quadratic pairwise pruning over all 10,395 rows if avoidable.

### Global composition

Compose one option from each disjoint window with an exact sparse DP. Key discrete states by `(direct_count_delta, CNOT_delta)` and retain the minimum total `Delta Lambda` for each key. Final admissibility:

- `direct_count_delta >= 0` versus B*;
- `Delta Lambda <= 0.01 * Lambda(B*)`;
- minimize total controlled CNOT.

This is exact for the frozen disjoint 12-term window decomposition.

## Required baselines

- B0: R5B proof-carrying original outer incumbent (`CNOT=12232`, `T=95318`, `direct=104`, subject to exact replay).
- B*: R5C zero-slack quartet incumbent, reconstructed with pair list and exact controlled edge semantics.
- B2: R5C <=1% quartet successor.
- E: MAX-R5E exact 12-term-window result.

## Frozen development gates

All must hold:

1. B* reconstruction matches R5C zero-slack aggregate in `Lambda`, `CNOT`, `T`, and `direct`.
2. Every 12-term window is exhaustively enumerated (10,395 matchings for every full window).
3. E projected T <= B* projected T.
4. E direct count >= B* direct count.
5. E normalization overhead <=1% versus B*.
6. E controlled CNOT < B2 controlled CNOT.
7. E controlled CNOT reduction >=0.5% versus B*.
8. E controlled CNOT reduction >=0.5% versus B0.
9. No stronger oracle/access/ancilla/synthesis tolerance/PREP omission than R5B/R5C.

The 0.5% thresholds were fixed before the corrected outcome.

## If negative

Do not increase window size mechanically. The next materially different attacks are, in order:

1. mixed block cardinality with direct multi-term anticommuting cliques;
2. outer-selector co-design incorporating FOQCS-LCU's check-matrix SELECT and its actual PREP cost;
3. global symplectic/post-selection compilation inspired by Symphony only where coherent SELECT semantics remain valid.

## Fresh subject remains protected

H4/cc-pVDZ/2.0au/DUCC3 coefficients remain unopened. Fresh H4 gates are not frozen until the corrected N2 development result is known.
