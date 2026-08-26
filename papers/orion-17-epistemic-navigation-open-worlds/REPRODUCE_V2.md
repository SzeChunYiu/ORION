# ORION-17 reproduce V2

Run from repository root on the V2 theory-closure branch or descendant.

```bash
PYTHONPATH=src python papers/orion-17-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py
```

Expected sentinel:

```text
ORION-17 THEORY CLOSURE V2: PASS
```

Expected bounded counts:

- stopping-impossibility decision fixtures: `3`;
- certificate/ambiguity boundary fixtures: `2`;
- fixed-information representation-refinement fixtures: `3`;
- harmful-coarsening fixtures: `3`;
- evidence-versus-closure construction: `1`;
- support-transport combinations: `64`;
- distinct stop-terminal fixtures: `4`;
- fixed-chart special case: `1`.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py
```

The programme checker includes representation+obligation, goal+provenance and censored-resource cross-donor cases. The pytest wrapper also calls live ORION-11–ORION-15 selected native-decision embeddings.

These are deterministic theorem/countermodel checks, not evidence that a deployed navigation agent outperforms donor implementations.
