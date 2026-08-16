# Duplicate pytest module name blocked whole-suite verification

## Observed

The first Task-2 test file was named
`tests/unit/kernel/test_transition.py`, while
`tests/unit/mechanics/test_transition.py` already existed and the test
directories were not Python packages. The focused kernel suite passed, but the
first full-suite run stopped during collection with:

```text
import file mismatch: imported module 'test_transition' ...
is not the same as ... tests/unit/mechanics/test_transition.py
```

No project test executed in that run. Renaming the new file to
`test_transition_identity.py` restored full collection (`258 passed` at that
intermediate state).

## Failure class

`VERIFICATION_INSTRUMENT_COLLISION` + `FOCUSED_SUITE_BLIND_SPOT`.

## Correct response

- Give non-package pytest modules repository-unique basenames.
- Run the full collection before treating a focused green suite as a stage
  gate.
- Classify collection/instrument failures separately from ORION behavior
  failures; neither may be reported as passing evidence.

## General lesson candidate

A focused test result validates only the focused import topology. Verification
is not compositional when the complete test instrument cannot even collect.

## Residuals and reopen coordinates

- duplicate basenames introduced by later test modules;
- CI environments using different pytest import modes;
- stale `__pycache__` masking or changing the same failure signature.
