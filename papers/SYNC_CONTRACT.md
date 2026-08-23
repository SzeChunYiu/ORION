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

## ORION-Q publication synchronization — final V1

The Q-series has an additional, narrower synchronization layer because Q1-Q4 were written from a closed research programme and Q3 describes the research harness itself.

Canonical objects:

- `papers/Q_SERIES_FINAL_SPEC_V1.json` — paper identities, canonical manuscript paths, maximum claim scopes, required evidence, owner-declared skipped/deferred gates and forbidden promotions;
- `src/orion/programme/q_series_sync.py` — executable semantic/evidence checker for that specification;
- `papers/Q_SERIES_CONTENT_BINDING_V1.json` + `src/orion/programme/q_series_content_binding.py` — content-addressed drift guard for the canonical Q submission bytes;
- `src/orion/programme/content_binding_coverage.py` — repository-wide survey that now recognizes the Q1-Q4 cross-paper canonical binding alongside the older per-directory bindings;
- `packages/orion-research-harness/src/orion_research_harness/publication_contract.py` — Q3's machine-readable harness contract;
- `tests/unit/publication/test_q_series_final_spec.py`, `test_q_series_content_binding.py`, `tests/unit/programme/test_content_binding_coverage.py`, and `packages/orion-research-harness/tests/test_publication_contract.py` — regression gates;
- `.github/workflows/q-series-publication-sync.yml` — push/PR gate that exercises the paper/framework binding, Q3 harness contract and Q1 independent finite-core sanity result together.

`src/orion/registry.py` carries the shared Q-series sync epoch, canonical manuscript identities and Q3 harness publication-contract id. A change to any of those surfaces must update the final Q spec, content binding, framework snapshot and affected manuscript/claim ledger together.

### Q-series content-binding rule

The repository supports two content-binding forms. P6-P8 use per-directory `SHA256SUMS`/manifest bindings; Q1-Q4 use a deliberate cross-paper binding over the **canonical publication package**, not every historical draft. The Q binding recomputes Git blob identities directly from working-tree bytes, so an uncommitted/local edit is visible as drift. The generic `content_binding_coverage` survey consumes both forms, so Q1-Q4 no longer appear `UNBOUND` merely because their binding lives at the publication-wave level.

Historical V1 drafts may remain outside the canonical Q binding because they are provenance snapshots rather than current submission surfaces. They remain visible as unbound files in the survey's denominator accounting. A canonical Q manuscript, proof, claim ledger, novelty record or final spec may not change silently: the Q-series binding must be reviewed/regenerated with the change.

### Owner-skipped external expert review

The owner has explicitly elected not to require an external quantum-expert pre-review for Q1. `Q_SERIES_FINAL_SPEC_V1.json` records this as `SKIPPED_BY_OWNER` and the sync checker rejects any attempt to encode the skip as a scientific `PASS`.

Skipping that optional pre-review does **not** convert internal evidence into external validation, novelty authority, or physical-quantum authority. Journal peer review remains external scrutiny if/when the manuscript is submitted.

### Deferred Q2-Q4 upgrade studies

The prospective cross-domain/multi-frontier/real-domain protocols under Q2-Q4 remain registered successor research. They are not silently treated as executed evidence. The current Q2-Q4 manuscripts are finalized only at their narrower case-study / benchmark-definition / exact-synthetic mechanism scopes. A future paper that claims the broader generality must execute the corresponding protocol and advance the Q-series sync epoch/spec.

## Nearest-work rule

Every flagship paper must maintain a nearest-work case. A novelty case is blocked while nearest-work routes remain open, while no hostile falsifier exists, or when the nearest work already subsumes the purported claim. `CANDIDATE_DELTA` is a research state, not publication authority.

Absorbing a nearest mechanism may shrink or eliminate the ORION claim; that is a successful research outcome rather than a reason to ignore the work.

## Two-level evidence rule

Every flagship paper distinguishes:

1. **local falsifier evidence** — exact known-world/hostile tests of implemented semantics;
2. **external promotion evidence** — fresh domain-appropriate tasks, matched strong baselines, protected evaluators/gold and the paper-specific primary outcome.

A green repository/CI run may support the first level only. A paper cannot be marked externally validated or publication-ready while its external gate is `CANNOT_CHECK` or `FAIL`. `FlagshipEvidenceState.publication_ready` requires both levels to pass for all registered flagship papers.

The Q-series `current_internal_status` values are deliberately **not** `FlagshipEvidenceState.publication_ready`: they mean that the paper is internally complete for the explicitly bounded scope named in the Q-series final spec.

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
