# Framework ↔ paper synchronization contract

The executable framework is canonical for current mechanics; papers are scientific projections of that framework.

A framework change requires a paper audit when it changes any of:

- `K/W/M` state semantics;
- core operator identity or order;
- mechanics-of-mechanics substrate identity or audit grammar;
- scientific meaning/source-projection/representation-mapping semantics;
- authority/non-escalation rules;
- saturation/stopping semantics;
- failure/experience/issue learning, reframe or reopen behavior;
- evaluation chronology;
- Self-ORION promotion rules;
- nearest-work absorption/novelty boundaries;
- flagship falsifier or external-promotion gate semantics.

`papers/FRAMEWORK_SNAPSHOT.json` is machine-checked against `src/orion/registry.py`. Matching the snapshot proves only terminology/mechanic synchronization, not scientific validity or empirical support.

## Nearest-work rule

Every flagship paper must maintain a nearest-work case. A novelty case is blocked while nearest-work routes remain open, while no hostile falsifier exists, or when the nearest work already subsumes the purported claim. `CANDIDATE_DELTA` is a research state, not publication authority.

Absorbing a nearest mechanism may shrink or eliminate the ORION claim; that is a successful research outcome rather than a reason to ignore the work.

## Two-level evidence rule

Every flagship paper distinguishes:

1. **local falsifier evidence** — exact known-world/hostile tests of implemented semantics;
2. **external promotion evidence** — fresh domain-appropriate tasks, matched strong baselines, protected evaluators/gold and the paper-specific primary outcome.

A green repository/CI run may support the first level only. A paper cannot be marked externally validated or publication-ready while its external gate is `CANNOT_CHECK` or `FAIL`. `FlagshipEvidenceState.publication_ready` requires both levels to pass for all registered flagship papers.

## External evidence may not be declared by booleans

The canonical flagship external gate consumes `ExternalEvidenceManifest.v1`, whose criterion records bind:

- exact subject revision;
- content-addressed evidence artifact;
- external evaluator artifact;
- producer and verifier process lineages;
- evaluation epoch and split;
- PASS / FAIL / CANNOT_CHECK;
- frozen-before-candidate chronology and freshness.

Missing, duplicate, self-verified, post-hoc, non-fresh or binding-mismatched external records yield `CANNOT_CHECK`. A verified FAIL remains FAIL rather than being softened into missing evidence. In a repository-only environment, the default manifest is empty and all five external paper gates remain `CANNOT_CHECK`.

The older paper-specific boolean gate helpers are non-authoritative fixture utilities only; the canonical `FlagshipEvidenceState` does not use them.

Paper-specific empirical claims maintain their own evidence ledgers and cannot inherit truth from passing software tests, nearest-work prose, caller declarations or framework synchronization.
