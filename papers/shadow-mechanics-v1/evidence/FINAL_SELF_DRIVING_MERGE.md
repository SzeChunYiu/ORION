# Final Shadow self-driving merge evidence — 2026-08-15

This note supersedes intermediate reconciliation-run references for the RAKL-transfer/self-driving development round.

## Final merged state

The RAKL-transfer and Shadow self-driving work is present on `main` together with the newer concurrent self-driving kernel and answer-authority hardening. The reconciliation was performed against the newest available `main` rather than by overwriting the concurrent history.

A fresh public snapshot of post-merge `main` was installed and the complete repository test suite was executed locally after merge. The suite passed on that post-merge filesystem.

## Structural result

The current mechanics programme contains 59 reachable mechanic cells and fourteen step-specific provisional structural dimensions per cell before transfer:

- verification;
- failure semantics;
- observability;
- handoff;
- state;
- transition model;
- mathematics;
- dependencies;
- metrics;
- uncertainty;
- invariants;
- parent discipline;
- search coverage;
- saturation.

The resulting structural frontier is therefore 826 questions. The V1 transfer does **not** clear these flags directly. It generates one typed `AnswerRecord` per mechanic/dimension pair and applies them through the host-evidence-bound answer engine. Every content answer resolves a host-owned `EvidenceRecord` and carries its SHA-256 fingerprint. Waiver proposals do not close questions in V0.

The transfer is considered structurally closed only when:

1. the pre-transfer open-question count is non-zero;
2. the post-transfer open-question count is zero;
3. the number of closed questions equals the number of applied answer records;
4. the answer application has zero typed residuals;
5. the closure-attribution audit has zero residuals;
6. containment/dependency/mixed graph integrity remains clean;
7. empirical-open coordinates remain present.

## RAKL absorption

- all 24 registered canonical RAKL method surfaces are represented as scoped ORION transfer profiles;
- 49 leaf/cross-cutting ORION mechanics receive direct or adjacent RAKL profiles;
- 10 root/top-level mechanics receive explicit ORION composition profiles;
- 16 of the 21 registered RAKL V3 overlay modules are functionally subsumed or reconstructed;
- five remain deliberately selective/open: `gluing_learning`, `experience_benchmark`, `driver_learning`, `summation_compatibility`, and `quantifier_compatibility`.

These are design/provenance transfers, not scientific-authority imports.

## Shadow self-driving boundary

The merged architecture can compose the following loop when host/provider boundaries are supplied:

`local/RAKL absorption -> evidence-bound structural answers -> empirical work ranking -> DevelopmentFibre -> ORION research -> evidence gate -> coding proposal -> content-addressed patch -> isolated sandbox -> protected fresh assurance -> evolution archive -> host-promotion recommendation`

The coding LLM/Codex-like worker is proposal-only. It does not own work selection, evaluation, assurance, or repository promotion. Protected evaluator/governance paths are hard-reject coordinates. No Self-ORION component exposes a self-merge primitive.

## Remaining empirical gate

This merge establishes **Shadow self-driving architecture readiness**, not Governed Self-ORION.

`GOVERNED_SELF_ORION` still requires prospective evidence from frozen wide-literature/deep-target live trials and fresh development trials, including matched baselines, outside-neighborhood knowledge acquisition, failure localization, positive development delta, positive protected fresh-assurance delta, preserved negative history, and scoped external promotion.
