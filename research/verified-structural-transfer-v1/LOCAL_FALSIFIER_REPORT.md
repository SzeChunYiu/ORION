# Local falsifier report — Verified Structural Transfer V1

**Authority:** `LOCAL_ENGINEERING_ONLY`. These are deterministic known-answer counterexamples, not external paper results.

## Test execution

Command:

```bash
PYTHONPATH=src pytest -q tests/test_verified_structural_transfer.py
```

Isolated prototype result before repository integration:

```text
31 passed
```

Compilation/import smoke check also passed for `orion.transfer`.

## Paper-specific known-answer counterexamples

The executable `orion.transfer.toy_benchmarks.run_all_toys()` produced:

| Paper | Mechanism | Weak baseline | Prototype | Local result |
|---|---|---:|---:|---|
| P1 | responsibility diagnosability + active probe | formulation rewrite license = 0 | license = 1 after discriminating evidence | GREEN |
| P2 | conservative route exploration | reward 2 | reward 4 while declared safety credit remains non-negative | GREEN |
| P3 | scientific lens consistency | naive equivalent-measurement false contradiction = 1 | false contradiction = 0 | GREEN |
| P4 | defeater-directed protected evidence | expected addressed severity 0.18 | 1.53 | GREEN |
| P5 | non-compensatory multi-stage gate | greedy replay-only harmful acceptance = 1 | harmful acceptance = 0 | GREEN |

These values are **constructed toy-world quantities** and must never appear as empirical paper performance.

## Hostile properties proved by tests

- a higher structural retrieval score cannot bypass a false transfer assumption;
- unknown transfer evidence stays `CANNOT_CHECK`;
- failed transfer falsifier yields `OBSTRUCTED`;
- cross-confirmation does not count two examples from the same source domain as independent;
- P1 identical probe signatures have zero information gain and cannot license diagnosis;
- P1 evidence responsibility does not license formulation rewrite;
- P2 provider censoring does not become a zero reward;
- P2 an unsafe exploratory update is rejected **before state mutation**;
- P3 corrupted cycle produces `OBSTRUCTION`; no anchors produce `CANNOT_CHECK`;
- P4 unprotected self-check cannot clear a critical defeater and available evidence does not itself authorize;
- P5 fresh harm blocks regardless of replay score; protected `CANNOT_CHECK` blocks; harmful candidates remain archived;
- a known out-of-order failure cannot be hidden behind missing earlier P5 stages.

## Important failure found and repaired during this wave

The first P2 allocator implementation checked the safety invariant **after** mutating route statistics. A deliberately unsafe direct call raised an error but left polluted state. The hostile test was strengthened to require transactionality; `record()` now checks the next lower-bound state before committing any reward/censoring statistics.

The P5 gate originally returned `IN_PROGRESS` at the first missing stage before inspecting an already-recorded later-stage failure. A hostile out-of-order record could therefore hide known harm. The evaluator now gives any known `FAIL`/harm priority over missing stages.

These repairs are exactly why the mechanisms are not proposed from prose alone.
