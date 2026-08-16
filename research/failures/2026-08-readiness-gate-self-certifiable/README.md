# The development-readiness gate was self-certifiable

**Observed:** 2026-08-16. **Status:** REPAIR IMPLEMENTED ON `fix/readiness-derivation-v1`; external custody/evaluator remains unavailable.

## Original reproduction

The old API accepted nineteen caller-supplied booleans. A caller could construct all of them as `True` and obtain `GOVERNED_SELF_ORION`. Several architecture booleans were hardcoded true at the only construction site.

Failure class: `DECLARATION_BOUND_PROMOTION` — a promotion decision resting on assertions the subject of the decision can author.

## Why this mattered

ORION already refused to promote a single failure guard past local verification without external lineage separation, but the larger system could promote itself to primary development status by setting booleans. That inverted the authority hierarchy.

## Applied repair

### 1. In-process governed-readiness state removed

`SelfOrionReadinessStage` now contains only:

- `BOOTSTRAP`;
- `SHADOW_SELF_DRIVING`;
- `READY_PENDING_EXTERNAL_ATTESTATION`.

There is **no** `GOVERNED_SELF_ORION` enum value. ORION cannot express unconditional self-promotion internally.

### 2. Empirical booleans removed

The old `ReadinessEvidence` boolean dataclass is gone. Empirical readiness now consumes `ReadinessEvidenceRecord.v1` objects. Every record binds:

- one typed criterion;
- content-addressed evidence artifact;
- exact subject revision;
- evaluator artifact;
- producer and verifier process lineage hashes;
- evaluation epoch and split;
- PASS / FAIL / CANNOT_CHECK;
- whether evaluator chronology was frozen before the candidate;
- whether the split is fresh.

Self-verification, post-hoc evaluator evidence, non-fresh evidence, duplicate/missing criteria, mixed subject revisions, mixed evaluator artifacts and mixed evaluation epochs are blockers.

Even a complete independently separated PASS set reaches only `READY_PENDING_EXTERNAL_ATTESTATION`.

### 3. Shadow architecture evidence is derived, not hardcoded pass flags

`ShadowSelfDrivingController.architecture_evidence()` now derives open-question count, graph-defect count and empirical-work availability from the live development state, names the component/protected-boundary/failure-history artifacts in the assembled controller, and detects whether a merge/promote-self capability is actually exposed. Architecture evidence establishes only the Shadow stage.

### 4. META_OVERFIT is explicit

`ChangeControlVerdict.META_OVERFIT` now distinguishes development-set improvement accompanied by fresh-assurance regression from generic `CANDIDATE_ONLY`. The Self-ORION cycle surfaces the same typed status.

## Falsifier

The repaired tests require:

- a complete architecture with no empirical receipts -> `SHADOW_SELF_DRIVING`;
- complete independently verified empirical receipts -> **only** `READY_PENDING_EXTERNAL_ATTESTATION`;
- `GOVERNED_SELF_ORION` absent from the enum;
- self-verified or post-hoc records blocked;
- `CANNOT_CHECK` distinct from FAIL and readiness-blocking;
- all records bound to one subject revision, one evaluator artifact and one evaluation epoch;
- development gain + fresh regression -> `META_OVERFIT`;
- no result authorizes self-merge.

If the old all-boolean reproduction becomes possible again, this failure class has recurred.

## Remaining external blocker

There is still no concrete protected development evaluator in external custody in this repository—only the protocol/test doubles. Therefore issue #8/live Self-ORION evidence and actual host promotion remain `CANNOT_CHECK`. That is now an explicit external dependency rather than a boolean callers can bypass.
