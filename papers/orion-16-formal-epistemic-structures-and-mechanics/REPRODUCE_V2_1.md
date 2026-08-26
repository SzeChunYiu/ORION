# ORION-16 reproduce V2.1

Run from repository root:

```bash
PYTHONPATH=src python papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2_1.py
PYTHONPATH=src python papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py
```

Normative sentinel:

```text
ORION-16 THEORY CLOSURE V2.1: PASS
```

V2.1 specifically checks:

- 960 forward-DAG/change root-inclusive safety cases and 2,048 changed-root occurrences;
- one explicit spurious-edge countermodel showing soundness alone does not imply minimality;
- 7 affected-realizability sets with every one-node omission rejected by a compatible adversarial semantics;
- 8 footprint-faithful composition fixtures;
- one hidden-read commutation counterexample;
- 3 preservation-versus-revalidation controls;
- compatibility with the typed-erasure discriminator.

Refutation capacity of the two graph checkers:

```bash
PYTHONPATH=src python papers/orion-16-formal-epistemic-structures-and-mechanics/formal/refutation_audit.py
```

Both `check_reopening` and `check_root_inclusive_safety` asserted set-algebra
identities until 2026-08-22, and every wrong graph operator substituted for
`descendants` was accepted while the published counts stayed at `(543, 130320)`
and `(960, 2048)`. This audit measures what the repaired assertions reject:
per-check refutation over a register of declared false reopening operators, the
enumerated axes that only multiply case counts, and the substitution table with
its before column re-derived on each run. It exits `3` if any check has no live
falsifier. The counts the two checkers print are unchanged.

Programme integration:

```bash
PYTHONPATH=src python papers/candidates/checkers/check_donor_complete_envelope_v1.py
pytest -q tests/unit/candidates/test_p6_p8_candidate_embedding.py tests/unit/candidates/test_p6_p8_theory_closure_v21.py tests/unit/candidates/test_p6_formal_refutation_capacity.py
```

The V2.1 assumption checker is normative for the minimality/commutation premises; the older V2 checker remains supporting evidence for the other closed results.
