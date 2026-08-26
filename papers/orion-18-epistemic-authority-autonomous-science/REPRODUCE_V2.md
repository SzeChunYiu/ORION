# ORION-18 reproduce V2

Run from repository root on the V2 theory-closure branch or descendant.

```bash
PYTHONPATH=src python papers/orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2.py
```

Expected sentinel:

```text
ORION-18 THEORY CLOSURE V2: PASS
```

Expected bounded counts:

- source-domain/target-domain direct-discharge matrix: `25`;
- typed coercion composition fixtures: `2`;
- alternative-derivation revocation fixtures: `5`;
- authority terminal fixtures: `5`;
- finite additive-blocker cases: `5`;
- shared-calculus / ideal typed-product equivalence cases: `160`;
- positive/trusted coercion controls: `3`;
- post-hoc/epoch fixtures: `2`;
- protected self-promotion fixtures: `2`.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py
```

The donor-envelope checker includes generic-permission/scientific-discharge, alternative-support revocation, chronology and resource/censoring cases. It intentionally expects behavioral equality with the ideal donor-product baseline when semantics are identical.

These commands reproduce the formal claims only. They do not show superiority over real authorization/governance systems.
