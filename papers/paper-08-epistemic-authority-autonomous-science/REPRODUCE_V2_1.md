# P8 reproduce V2.1

Run from repository root:

```bash
PYTHONPATH=src python papers/paper-08-epistemic-authority-autonomous-science/formal/check_theory_closure_v2.py
PYTHONPATH=src python papers/paper-08-epistemic-authority-autonomous-science/formal/check_theory_closure_v2_1.py
PYTHONPATH=src python papers/paper-08-epistemic-authority-autonomous-science/formal/check_contract_manifest_v2.py
```

Expected sentinels:

```text
P8 THEORY CLOSURE V2: PASS
P8 THEORY CLOSURE V2.1: PASS
P8 CONTRACT MANIFEST V2: PASS
```

The theorem checker covers full 5x5 domain typing, exact coercion composition, support-family revocation, terminal distinctions, finite blocker cases, 160 shared/product equivalence cases, positive coercion, epoch and self-promotion boundaries.

The V2.1 primitive-closure checker discharges the four elements V2 left implicit: fail-closed blocker determination (with the fail-open countermodel), blocker monotonicity, a witness pair proving permission is not a function of confidence and expected utility, non-monotonic authority in both directions, forward-only demotion, and protected custody as one root class among four.

The contract executor runs all 17 frozen authority cases: clean authorized cases across all five ORION domains, paired blocked cases, five laundering attacks, one `CANNOT_CHECK` case, and a clean registered-coercion control.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py tests/unit/candidates/test_p6_p8_theory_closure_v21.py tests/unit/candidates/test_p8_formal_core_primitives.py
```

The contract manifest is a protected reference-policy preflight, not a real-agent superiority result.
