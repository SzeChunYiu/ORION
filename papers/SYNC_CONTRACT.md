# Paper ↔ framework ↔ harness synchronization contract

ORION's papers, executable framework, and research harness are three projections of one research semantics. None of the three is allowed to drift silently from the others.

The framework remains canonical for typed runtime objects and operator semantics; papers remain canonical for the scientific/epistemic claims and limitations those objects are intended to express; the harness is canonical for how those semantics are actually exercised against replayable capabilities and receipts. A material mismatch between any pair is a conformance defect rather than a reason to privilege one layer automatically.

A material change in **any** layer requires an audit of the other two when it changes any of:

- `K/W/M` state semantics;
- core operator identity or order;
- mechanics-of-mechanics substrate identity or audit grammar;
- scientific meaning/source-projection/representation-mapping semantics;
- authority/non-escalation rules;
- saturation/stopping semantics;
- `CANNOT_CHECK` / unresolved-state lifecycle;
- negative-result / obstruction / falsification assimilation;
- failure/experience/issue learning, reframe or reopen behavior;
- evaluation chronology;
- Self-ORION promotion rules;
- nearest-work absorption/novelty boundaries;
- flagship falsifier or external-promotion gate semantics;
- host capability/receipt semantics that can change the observable research-control path.

`papers/FRAMEWORK_SNAPSHOT.json` is machine-checked against `src/orion/registry.py`. Matching the snapshot proves only terminology/mechanic synchronization, not scientific validity or empirical support. Harness semantic terminals and hostile tests provide an additional execution-level synchronization check; they likewise do not grant scientific authority.

## Three-layer covariance rule

For every research-control mechanic:

1. the **paper layer** must state the epistemic contract, admissible conclusions, and explicit limitations;
2. the **framework layer** must expose typed objects/decisions implementing that contract without silently strengthening it;
3. the **harness layer** must exercise the same contract on replayable inputs and fail closed when the required evidence/capability/authority object is absent.

A paper concept with no executable owner is not operational. A framework object with no paper/claim boundary is not scientifically interpretable. A harness shortcut that bypasses the typed framework or paper boundary is not conformant.

## Outcome lifecycle: positive, negative, unresolved

ORION distinguishes three top-level research outcomes.

### Positive

A positive outcome satisfies the relevant bounded evidence/decision contract. It does not automatically imply novelty, publication, adoption, promotion, merge, or global task-stop authority.

### Negative

A verified negative result is scientific/research evidence, not an implementation failure and not missing information. Examples include a verified obstruction, falsified hypothesis, non-identifiability theorem/countermodel, donor subsumption, failed transfer under a frozen access/resource model, or impossibility boundary.

A verified negative result must remain negative and be assimilated. It may close a hypothesis branch, register an obstruction/donor result, reopen dependencies, trigger reframe/search, or force a paper/framework claim revision. It must never be softened to `CANNOT_CHECK` merely because a positive result was preferred.

Canonical typed representation: `ResearchNegativeResult.v1`.

### Unresolved / CANNOT_CHECK

`CANNOT_CHECK` means the current typed evidence/control state is insufficient to decide the requested judgment. It is not equivalent to a negative result.

By default, every `CANNOT_CHECK` is an **active research obligation** and must carry `ResearchResolutionObligation.v1`, including:

- stable subject/obligation identity;
- unresolved class and reason codes;
- required evidence/capability/authority objects;
- admissible next research actions;
- prior attempts and blockers;
- an explicit bounded/external stop condition when one applies;
- non-authorizing authority ceilings.

A bare `CANNOT_CHECK` emitted by the shared research harness is a covariance/conformance failure.

The harness must attempt an admissible resolution path when one exists: retry/restore capability, acquire/verify evidence, widen an authorized search route, orient/reframe, diagnose responsibility, repair representation/interface, assess OCME, check typed authority, or request a protocol-permitted resource/protected-evidence widening.

## Legitimate unresolved boundaries

The resolution-first rule does **not** mean ORION may fabricate decidability. An unresolved obligation may remain open when a typed boundary is established, including:

- protected/external evidence intentionally not yet released;
- extension ambiguity or formal non-identifiability under the declared world class;
- a frozen resource bound with no authorized widening;
- an authority/coercion boundary the harness is not permitted to mint;
- a currently unavailable host capability preserved as orchestration state rather than scientific evidence.

Such states explain why the obligation remains unresolved. They are not task-completion certificates.

## Nearest-work rule

Every flagship paper must maintain a nearest-work case. A novelty case is blocked while nearest-work routes remain open, while no hostile falsifier exists, or when the nearest work already subsumes the purported claim. `CANDIDATE_DELTA` is a research state, not publication authority.

Absorbing a nearest mechanism may shrink or eliminate the ORION claim; that is a successful research outcome. When nearest work subsumes the claim, the result should be represented as a verified negative/donor-subsumption outcome and assimilated rather than ignored.

## Two-level evidence rule

Every flagship paper distinguishes:

1. **local falsifier evidence** — exact known-world/hostile tests of implemented semantics;
2. **external promotion evidence** — fresh domain-appropriate tasks, matched strong baselines, protected evaluators/gold and the paper-specific primary outcome.

A green repository/CI run may support the first level only. A paper cannot be marked externally validated or publication-ready while its external gate is unresolved or negative relative to the required promotion conjunction. `FlagshipEvidenceState.publication_ready` requires both levels to pass for all registered flagship papers.

## External evidence may not be declared by booleans

The canonical flagship external gate consumes `ExternalEvidenceManifest.v1`, whose criterion records bind:

- exact subject revision;
- content-addressed evidence artifact;
- external evaluator artifact;
- producer and verifier process lineages;
- evaluation epoch and split;
- PASS / FAIL / CANNOT_CHECK;
- frozen-before-candidate chronology and freshness.

Missing, duplicate, self-verified, post-hoc, non-fresh or binding-mismatched external records yield `CANNOT_CHECK` plus a resolution obligation describing the missing external/protected object. A verified FAIL remains FAIL/negative evidence rather than being softened into missing evidence. In a repository-only environment, the default manifest may therefore contain unresolved external obligations without implying scientific failure.

The older paper-specific boolean gate helpers are non-authoritative fixture utilities only; the canonical `FlagshipEvidenceState` does not use them.

Paper-specific empirical claims maintain their own evidence ledgers and cannot inherit truth from passing software tests, nearest-work prose, caller declarations, framework synchronization, or harness conformance terminals.
