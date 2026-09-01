# P1 failed. Diagnosis, and a corrected metric declared before re-running

**Status:** `PREDICTION_FAILED__DIAGNOSED__CORRECTED_METRIC_FROZEN`
**Scientific authority delta:** `NONE`.

`REPAIR_RESULT_V1.json` records `REPAIR_FAILS__P1_zero_amplifying_edges_survive`. Four
amplifying edges survived the repair. Four of five predictions held; P1 did not. That
receipt stays on the record unedited.

## What the four surviving edges are

Enumerated directly:

| flips | `transport_vacuous` before | after |
|---|---|---|
| `evidence_transport_known` | False | False |
| `evidence_transport_known`, `evidence_transport_valid` | False | False |
| `evidence_transport_known`, `obligations_clear` | False | False |
| `evidence_transport_known`, `evidence_transport_valid`, `obligations_clear` | False | False |

Every one sits at `transport_vacuous = False` on both ends. That coordinate asserts the
derivation route **did** transport evidence. So in each of these four the transport flag
became true because a real transport happened.

Those are the legitimate repairs. My metric counted them as attacks.

## The defect is in the metric, not the repair

`VACUOUS` was fixed as a constant list of three coordinates, written before
`transport_vacuous` existed. Once the repair adds a coordinate that distinguishes a real
transport from an absent one, whether a transport flip is vacuous stops being a property of
the coordinate and becomes a property of the **state**. The constant list cannot express
that, so it convicts the legitimate route along with the attack.

This is my protocol-design error. The honest handling is to say so, keep the failed
receipt, and declare the corrected metric here — before running it — rather than editing
`check_repair_v1.py` until it passes.

## Corrected metric, frozen now

`amplifying(a, b)` holds iff `verdict(a) = CANNOT_CHECK`, `verdict(b) = ADMISSIBLE`, every
flip is a `False -> True` turn-on, and every flipped coordinate is **vacuously satisfiable
in `b`**, where:

- `obligations_clear` is vacuously satisfiable in every state, since `O_h = ∅` is always an
  available re-grounding;
- `evidence_transport_known` and `evidence_transport_valid` are vacuously satisfiable in
  `b` exactly when `b[transport_vacuous]` is true.

State-sensitive, not coordinate-sensitive.

## The control that stops this being a metric tuned to pass

The corrected metric is run against **both** classifiers over the same extended space:

- against the **unrepaired** `classify()`, it must still find the attack. If it does not,
  the metric defined the problem away and the repair result is worthless.
- against the **repaired** wrapper, the prediction is zero.

## Predictions, recorded before running

1. Corrected metric, unrepaired classifier: amplifying edges **> 0**. The attack is still
   detected. This is the load-bearing control.
2. Corrected metric, repaired classifier: amplifying edges **= 0**.
3. The sixteen real gold verdicts remain preserved, as in `REPAIR_RESULT_V1.json`.
4. No edge is amplifying by `obligations_clear` alone, under either classifier — because
   `obligations_clear = False` classifies `REOPEN`, never `CANNOT_CHECK`, so it cannot be a
   start state.

If (1) fails, the corrected metric is rejected and P1's failure stands unexplained.
