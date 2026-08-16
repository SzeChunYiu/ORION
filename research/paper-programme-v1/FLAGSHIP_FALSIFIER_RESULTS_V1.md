# Five flagship falsifier round V1

**Frozen starting main:** `348e11b3e4451609af7740bcee7df695bb3abbf8`
**Local-suite commit:** `8a8a7feed588363f8e2cd820d3399a33b7af3074`
**GitHub Actions:** run `31933432314`, success
**Authority:** deterministic known-world / hostile implementation evidence only. No external novelty or empirical-superiority claim is licensed.

## Round invariant

The five flagship papers have two distinct gates:

1. **local falsifier gate** — exact/hostile worlds that test whether the implemented mechanism has the claimed semantics;
2. **external promotion gate** — matched nearest-work baselines, fresh tasks, protected evaluators and domain-appropriate gold data.

The local gate may PASS while the external gate remains `CANNOT_CHECK`. `FlagshipEvidenceState.publication_ready` is true only if both pass for all five papers.

## Paper I — Recursive Epistemic Reconstruction

**Local result:** PASS on hidden-parent-domain, hidden-representation, missing-evidence-only and execution-bug-only cases.

### Failure consumed by the framework

The negative control exposed a real defect: `revision_allowed()` previously licensed `REFRAME` for any singular responsibility. A pure `EVIDENCE` or `EXECUTION` failure could therefore enter a formulation rewrite if the semantic reasoner proposed one. That confounded "responsibility is identified" with "this responsibility is repairable by reframing."

**Repair:** local `REFRAME` is now licensed only for question, representation, search, routing, decomposition, interface and measurement responsibilities. Evidence/execution failures require acquisition/execution repair; method/evaluator changes remain protected Self-ORION operations.

**External gate:** `CANNOT_CHECK` until fresh hidden-formulation tasks are run against matched static-workflow and tree-search/agentic baselines with labels hidden and resources matched.

## Paper II — Open-World Scientific Knowledge Discovery

**Local result:** PASS on a complete-gold retrieval world and the registered coverage hostile cases.

The suite confirms the implementation-level rules:
- a strong lexical baseline is computed in the same evaluation call;
- the candidate ranking must beat that baseline on recall in the frozen world;
- same-backend routes do not earn independence;
- independent routes with zero overlap do not produce a bounded unseen-population estimate;
- the same content encountered through multiple routes counts once;
- single-target hit-rate data cannot be reported as recall;
- coverage estimates are diagnostic only and never stopping authority.

**External gate:** `CANNOT_CHECK` until ResearchArena/AutoResearchBench/MetaSyn-style complete-gold trials are executed with frozen provider trajectories and matched simple baselines.

## Paper III — Global Knowledge Portrait

**Local result:** PASS on the first exact semantic-atlas world.

### Missing layer exposed and added

The existing atlas preserved `SourceProjection` and `RepresentationMapping` lineage but lacked a typed linguistic/scientific meaning projection between source span and normalized knowledge. V1 therefore adds proposal-level `ScientificMeaningProjection.v1` with predicate/roles, referents, constructs, measurements, temporal context, polarity, modality, discourse relation, attribution, assumptions and unresolved ambiguity.

The hostile world checks:
- same predicate / different referent is not merged;
- same construct / different measurement remains distinct;
- aligned asserted opposite polarity is contradiction;
- modal or attribution differences are contextual rather than contradiction;
- literature bridges require the same semantic pivot;
- ORION-native mappings remain source-recoverable;
- reconstructed portraits retain source-projection and mapping lineage;
- a new representation can widen the future relevance/search universe.

**External gate:** `CANNOT_CHECK` until real three-plus-domain cases with source/mapping gold, long-context/RAG/flat-schema baselines and semantic-coordinate ablations are run.

## Paper IV — Verified Scientific Discovery

**Local result:** PASS on the authority-laundering suite.

The suite checks exact evidence-content substitution, content-vs-provenance identity, weak non-empty verifiers, independent specific verifiers, same-lane verification and post-hoc verifier chronology. Exact evidence fingerprints and the host-owned hostile battery are exercised through the real answer/check machinery.

**External gate:** `CANNOT_CHECK` until claim/source-attribution evaluation, search-time contamination auditing, evaluator locking, held-out access logging, and matched source-aware verifier baselines are run. Issue #59 owns this external hostile programme.

## Paper V — Self-ORION

**Local result:** PASS on the issue/cause/fresh-transfer/reward-hacking world.

### Nearest-work absorption

The round absorbs the issue-centric insight from ADIAS (arXiv:2608.06410): the durable object of self-improvement should be the unresolved issue and its evidence/intervention history, not only a lineage of candidate agents. ORION now has `DevelopmentIssue.v1`, carrying a stable issue identity, candidate and supported causes, discriminator evidence, failure episodes, intervention outcomes and status transitions.

This **removes persistent issue state from ORION's novelty boundary**; the surviving delta remains the composition with failure-as-knowledge, recurrence-not-cause, invention readiness, fresh-transfer/protected-assurance gates, negative history and no self-certification.

The local hostile suite verifies:
- recurrence alone does not identify cause;
- cause support requires discriminator evidence;
- harmful and successful interventions remain attached to the same issue;
- fresh transfer is distinct from replay;
- a resolved issue cannot silently reopen, but new evidence can reopen the same identity;
- ordinary causes block method invention;
- invention readiness grants neither invention nor promotion authority;
- a candidate touching protected registry/governance paths is rejected even if visible and fresh deltas are artificially perfect.

**External gate:** `CANNOT_CHECK` until matched direct-self-edit and ADAS/DGM-like baselines, hidden failure causes, fresh transfer, protected evaluator chronology, complete negative history and protected-path access telemetry are all present.

## Current bounded terminal

```
LOCAL_FLAGSHIP_FALSIFIERS = PASS
EXTERNAL_PAPER_I = CANNOT_CHECK
EXTERNAL_PAPER_II = CANNOT_CHECK
EXTERNAL_PAPER_III = CANNOT_CHECK
EXTERNAL_PAPER_IV = CANNOT_CHECK
EXTERNAL_PAPER_V = CANNOT_CHECK
PUBLICATION_READY = false
```

This is progress, not a publication verdict. The local falsifiers make the hypotheses sharper and have already produced framework repairs; the external gates are deliberately preserved as the remaining empirical programme.
