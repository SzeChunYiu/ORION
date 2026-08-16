# The development-readiness gate is self-certifiable

**Observed:** 2026-08-16, main. **Status:** OPEN — reproduction below, repair specified, not applied.

## Reproduction

```python
assess_readiness_stage(
    ShadowSelfDrivingArchitectureEvidence(*[True] * 10),
    ReadinessEvidence(*[True] * 9),
)  # -> SelfOrionReadinessStage.GOVERNED_SELF_ORION
```

`assess_readiness` (`src/orion/self_orion/readiness.py:48-51`) is
`all(evidence.__dict__.values())` over nine caller-supplied booleans;
`ShadowSelfDrivingArchitectureEvidence` adds ten more. Nothing is derived from
an artifact. Any caller — including a challenger ORION proposing its own
promotion — reaches the top governance stage by constructing the dataclasses.

Worse, seven of the ten architecture coordinates are hardcoded at their only
construction site (`src/orion/self_orion/self_driving.py:128-134`):
`autonomous_research_loop_present`, `development_proposal_boundary_present`,
`content_addressed_patch_boundary_present`, `isolated_sandbox_boundary_present`,
`protected_assurance_boundary_present`, `failure_history_preserved`,
`self_merge_absent` are literal `True`. **A coordinate that cannot be False is
not evidence.**

## Failure class

`DECLARATION_BOUND_PROMOTION` — a promotion decision resting on assertions the
subject of the decision can author. The repository already names this defect in
its own research (`research/development/mechanic-answer-loop/candidate-answers/
REFRAME.METHOD.v0.md`): "a promotion API accepting a caller-provided
`governance_approved` boolean is declaration-bound, not content-bound."

## Why this one matters more than an ordinary bug

The inversion is the point. `experience/learning.py:364-384` refuses to promote
a *single failure guard* past `VERIFIED_LOCAL`, failing closed with
`external_lineage_separation_attestation_required`, because in-process lineage
labels "prove inequality, not independent organizational or process custody".
So today a self-improver cannot promote one guard — but can promote *itself to
primary development process* by filling in nineteen booleans.

The kernel's answer path fixed exactly this shape: `AnswerRecord` evidence must
resolve to a real artifact at a pinned digest, and a check must be independently
laned and frozen before the round it judges. The readiness gate never received
that treatment.

## Repair, specified

Every coordinate becomes a derivation over a cited, content-addressed artifact;
`CANNOT_CHECK` stays distinct from `FAIL`; `META_OVERFIT` (development gain with
fresh-assurance loss) becomes its own verdict rather than collapsing into
`CANDIDATE_ONLY` as it does at `change_control.py:169-172`; and the ceiling is
`READY_PENDING_EXTERNAL_ATTESTATION` — the enum must not contain `READY`, so
unconditional readiness is inexpressible rather than merely unreached.

Blocking dependency, verified: no concrete `ProtectedDevelopmentEvaluator`
exists in `src/` — only the Protocol (`change_control.py:45-51`) and test
doubles. Until an evaluator exists outside challenger write authority, the
honest verdict is `CANNOT_CHECK` by nonexistence, and the gate cannot pass.

## Falsifier

If a derivation-bound gate is implemented and the reproduction above still
reaches `GOVERNED_SELF_ORION`, the attribution is wrong and the defect is
elsewhere.
