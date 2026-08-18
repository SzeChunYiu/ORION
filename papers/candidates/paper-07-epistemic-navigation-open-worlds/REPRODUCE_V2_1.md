# P7 reproduce V2.1

Run from repository root:

```bash
PYTHONPATH=src python papers/candidates/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py
PYTHONPATH=src python papers/candidates/paper-07-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py
```

Expected sentinels:

```text
P7 THEORY CLOSURE V2: PASS
P7 CONTRACT MANIFEST V2: PASS
```

The first command checks the closed theorems/countermodels, including all 64 transport-coordinate combinations. The second executes all 8 frozen prospective contract cases, including harmful-reframe and non-retrieval experimental-design transfer controls.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py tests/unit/candidates/test_p6_p8_theory_closure_v21.py
```

The contract manifest is a reference-policy oracle and prospective instrument preflight. It does not constitute a live-agent performance result.
