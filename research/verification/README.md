# ORION scientific result verification (#283)

Independent red-team / reproducibility receipts for currently promoted flagship
positives. This directory is additive: it does not modify paper evidence or
scoring internals to make an audit pass.

## Layout

- `schemas/SCIENTIFIC_RESULT_VERIFICATION_V1.json` — machine-readable receipt schema
- `scientific_result_verification.py` — writer/validator (fail-closed)
- `independent_stats.py` — Wilson / bootstrap from written formulas
- `independent_scorers.py` — paper scorers from written specs (no original-scorer imports)
- `leakage.py` — shortcut falsifiers, including planted exact-label detector
- `audit.py` — builds receipts from committed artifacts
- `METHODOLOGY_MATRIX_V1.md` — literature freeze
- `VERIFIER_STANDARD_V1.md` — scorer/leakage/denominator protocol freeze
- `records/` — one `ScientificResultVerification.v1` JSON per atomic claim

## Run

```bash
PYTHONPATH=research/verification python research/verification/audit.py
PYTHONPATH=research/verification pytest -q tests/unit/verification
```

A receipt cannot authorize the claim it describes (`self_authorizing: false`).
`INVALIDATED` is a valid successful audit outcome. Unrun holdouts are
`CANNOT_CHECK` layers and cap the terminal state at `BOUNDED_VERIFIED`.
