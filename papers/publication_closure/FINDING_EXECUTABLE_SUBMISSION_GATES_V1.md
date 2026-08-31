# Some submission gates are executable, and one is a hard lock

Several papers carry their own checkers. Reading a paper's prose does not tell you its state; running its checker does. This was learned late: ORION-07 was reported as not-ready on the strength of an abstract sentence, while its checker had been returning `PASS` on `main`.

## What the checkers report on `main`

| paper | checker | result |
|---|---|---|
| ORION-06 | `check_transition_graph.py` | runs; `SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR` |
| ORION-07 | `check_q3_completion.py` | `Q3_COMPLETION_CHECK=PASS`, gate met |
| ORION-21 | `check_p11_adverse_integration_v2.py` | `status: PASS`, `scientific_authority_delta: BOUNDARY_NARROWING_ONLY` |
| ORION-22 | `check_p12_lifecycle_integration_v4.py` | `status: PASS`, **`top_tier_submission_allowed: false`** |
| ORION-23 | `check_p13_p14_pinned_corpus_v1.py` | present, not yet run here |

## ORION-22 is deliberately locked, not merely unready

The field is not a status the checker reports. It is an invariant the checker **enforces**:

```python
if authority.get("top_tier_submission_allowed") is not False:
    errors.append("top-tier submission gate must remain false")
```

Flipping that flag makes the check fail. The paper's authority record bars top-tier submission, and the checker exists partly to keep it barred.

The adjacent assertions give the reason: `external_public_benchmark_status` must equal `CANNOT_CHECK_NO_BOUND_PUBLIC_DATA_RESULT`, and an artifact-identity note records that a specific successor artifact does not exist and that the landed study is an adverse robustness stress. So the lock encodes a missing external-benchmark result, not a formatting problem.

ORION-22 is the **only** paper in the corpus asserting such a lock; a corpus grep for `top_tier_submission_allowed` returns it alone.

## Consequence

ORION-22 should not appear on any list of papers awaiting packaging work. No amount of author-block, reference or caption work moves it, and editing the flag to make it look ready would break its own checker --- which is exactly what the assertion is there to prevent. It needs a bound public-data benchmark result, which is new science.

## The method error this exposes

Every readiness judgement made earlier in this session came from reading text: abstracts, section files, rendered PDFs. That is the right way to find leaked codes and placeholder authors, and it is the wrong way to establish whether a paper's evidence gate is open. Two of these papers state their status in code, and one enforces it. A readiness audit that never runs the repository's own checkers is measuring the wrong surface.
