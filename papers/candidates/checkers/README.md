# ORION-16–ORION-18 deterministic finite falsifiers

These scripts instantiate bounded examples from the candidate formal cores. They require only the Python standard library and no LLM/API access.

They are **not** substitutes for general proofs, donor-baseline experiments, protected evaluation, or novelty review.

## Run

```bash
python papers/candidates/checkers/p6_finite_falsifiers_v1.py
python papers/candidates/checkers/p7_finite_falsifiers_v1.py
python papers/candidates/checkers/p8_finite_falsifiers_v1.py
```

## Initial local result — 2026-08-17

- ORION-16: 5/5 checks pass.
- ORION-17: 7/7 checks pass.
- ORION-18: 7/7 checks pass.

The checks cover selective reopening, history-aware commutation, non-escalation/residual obligations, recursion/self-authorization, extension ambiguity, certificate/ambiguity separation, route/task stop, chart-change expressivity, support/goal transport, fail-closed stopping, anti-laundering, scope restriction, non-compensatory blockers, dependency revocation, epoch replay, post-hoc refusal and clean authorized controls.

Future versions should move from hand-constructed fixtures to exhaustive bounded enumeration/model checking and donor-faithful embedding fixtures.