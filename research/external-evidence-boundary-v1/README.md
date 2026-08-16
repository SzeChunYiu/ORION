# External evidence boundary V1

## Problem

The first flagship benchmark implementation correctly kept external claims separate from local falsifiers, but its paper-specific helper functions still accepted caller booleans such as `evaluator_locked=True` or `matched_baseline=True`. Those helpers did not mint scientific authority, yet the pattern was declaration-bound and could manufacture a PASS-shaped benchmark report without real external artifacts.

The later Self-ORION readiness failure showed this class must be removed wherever a stronger claim depends on external custody.

## Repair

`ExternalEvidenceManifest.v1` is now the canonical input to the flagship external paper gates.

Each `ExternalEvidenceRecord` binds:

- one typed Paper I–V external criterion;
- content-addressed evidence artifact;
- exact ORION subject revision;
- external evaluator artifact;
- producer and verifier process lineages;
- evaluation epoch and split;
- PASS / FAIL / CANNOT_CHECK;
- frozen-before-candidate chronology;
- fresh-split status.

The record is not independently verified when producer and verifier lineages are identical.

## Assessment rules

For each flagship paper:

- every required criterion must have exactly one record;
- every record must bind the manifest subject/evaluator/epoch;
- self-verification, post-hoc evaluation and non-fresh evidence yield `CANNOT_CHECK`;
- a criterion with `CANNOT_CHECK` yields `CANNOT_CHECK`;
- a fully bound verified FAIL yields FAIL;
- only a complete independently verified PASS set yields external PASS.

This distinction is important: missing evidence is not failure, and failure is not missing evidence.

## Repository-only boundary

`empty_external_manifest()` contains no external records. The canonical `current_flagship_evidence_state()` therefore derives:

```
P1 = CANNOT_CHECK
P2 = CANNOT_CHECK
P3 = CANNOT_CHECK
P4 = CANNOT_CHECK
P5 = CANNOT_CHECK
publication_ready = false
```

No caller boolean can change that state. A host or external evaluation process must supply the content/lineage-bound manifest.

## Relationship to open issues

### #8 Shadow Self-ORION live-provider trial

Paper V records require real development/research provider traces, matched self-edit/agent-design baselines, hidden failure causes, fresh transfer, external evaluator chronology, negative-history completeness and protected-path access evidence.

### #59 Verified Scientific Discovery hostile benchmark

Paper IV records require real source-attribution evaluation, search-time contamination audit, evaluator lock, held-out access telemetry, matched source-aware verifier baseline and the false-authority-promotion outcome.

The repository now has the local machinery to ingest and judge these artifacts. It does not possess the external custody/provider/evaluator evidence itself; those issues remain open for that reason.

## Failure-learning rule

Whenever a new gate depends on a fact whose truth is controlled outside the candidate system, represent it as externally bound evidence rather than a caller declaration. `CANNOT_CHECK` is the correct state until such evidence exists.
