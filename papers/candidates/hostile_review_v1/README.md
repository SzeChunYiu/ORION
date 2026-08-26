# ORION-16–ORION-18 hostile formal review V1

This additive package reviews the ORION-16–ORION-18 formal programme at Git snapshot
`999abd4899f3fed906ba024ae8ecd775a69b6560`. It does not replace the larger
enumerators already on the candidate branch. It targets gaps those checkers do
not encode.

## Review functions

- formal epistemology / knowledge representation;
- programming languages and finite-model checking;
- open-world navigation and representation refinement;
- authorization logic and capability security;
- scientific editing, overlap control and claim authority.

These are analytical roles, not claims of independent human participation.

## What is checked

### ORION-16

- directly changed certified roots are included in the affected closure;
- preservation certificates are downstream-only, evidence-bearing, change-bound
  and protected-root issued;
- later computational success cannot erase hard residual obligations.

### ORION-17

- the current unconstrained `T -> T'` witness is identified as non-discriminating;
- a stronger witness keeps latent states, transitions, goals and retained
  information fixed while refining only the observation quotient;
- the negative preservation direction is pressure-tested for its missing
  richness/ambiguity premise;
- task-stop, route-stop and `CANNOT_CHECK` remain distinct.

### ORION-18

- evidence-to-obligation discharge is checked across the full five-by-five
  domain matrix;
- coercion paths must compose scope, kind and epoch, not merely domains;
- revocation is checked on an AND/OR derivation structure with an independent
  alternative derivation;
- `AUTHORIZED`, `DENIED` and `CANNOT_CHECK` are kept distinct.

## Run

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s papers/candidates/hostile_review_v1/tests -v
PYTHONDONTWRITEBYTECODE=1 python papers/candidates/hostile_review_v1/run_all.py
```

The report is written to
`papers/candidates/hostile_review_v1/artifacts/HOSTILE_REVIEW_RESULTS.json`.

Authored replay results are recorded in `LOCAL_VALIDATION_2026-08-17.md`. File hashes are frozen in `MANIFEST.sha256`.

## Authority boundary

A `PASS` means the encoded corrected finite property held. A
`COUNTEREXAMPLE_CONFIRMED` means the package reproduced a weakness in the
reviewed statement/checker scope. Neither status establishes novelty,
real-world transfer, independent review or publication readiness.
