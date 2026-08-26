# ORION-16 reproduce V2

Run from repository root on the theory-closure branch or any descendant containing V2.

```bash
PYTHONPATH=src python papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py
```

Expected sentinel:

```text
ORION-16 THEORY CLOSURE V2: PASS
```

Expected bounded counts include:

- root-inclusive graph/change cases: `(960, 2048)` where the second value counts changed-certified-root occurrences;
- preservation-certificate cases: `64`;
- separated commutation cases: `3`;
- residual-obligation Boolean cases: `8`;
- authority non-escalation bounded pairs: `64`;
- typed-erasure constructions: `3`;
- recursive-audit fixtures: `3`;
- conservative dependency special cases: `3`.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py
```

The first command checks the cross-donor envelope. The pytest wrapper also calls the live ORION schema/native-embedding checks and prior finite checkers.

These commands reproduce deterministic mathematical support only. They do not establish literature novelty or real-agent superiority.
