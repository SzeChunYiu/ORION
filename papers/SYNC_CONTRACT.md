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

## ORION-Q publication synchronization — recursive V3 epoch

The closed ORION-Q programme now uses sync epoch `2026-08-22-q-series-recursive-v2`. Q1-Q4 were recursively rebuilt with the pinned `academic-paper-skills` donor and an ORION harness controller that separates manuscript quality, exact venue fit, scientific evidence blockers, claim narrowing and target transfer.

Canonical objects:

- `papers/Q_SERIES_FINAL_SPEC_V1.json` — V3 manuscript identities, scoped claims, target ladders, evidence blockers and forbidden promotions;
- `development/q-paper-recursive-refinement/ACADEMIC_PAPER_SKILLS_PIN.json` — exact external paper-method donor revision;
- `development/q-paper-recursive-refinement/RECURSIVE_PAPER_REFINEMENT_PROTOCOL.md` — frozen evidence-first iterative paper-research contract;
- `development/q-paper-recursive-refinement/VENUE_READINESS_PROFILES_V1.json` — internal target gates; explicitly not acceptance probabilities;
- `packages/orion-research-harness/src/orion_research_harness/paper_refinement.py` — typed paper/referee/concern/terminal controller;
- `src/orion/programme/q_series_sync.py` — executable semantic/evidence/readiness-boundary checker;
- `papers/Q_SERIES_CONTENT_BINDING_V1.json` + `src/orion/programme/q_series_content_binding.py` — epoch-bound Git-blob drift guard over canonical V3 papers, V3 ledgers, review verdicts and load-bearing publication analyses;
- `src/orion/programme/content_binding_coverage.py` — repository-wide survey that recognizes Q1-Q4's cross-paper canonical binding;
- `packages/orion-research-harness/src/orion_research_harness/publication_contract.py` — Q3's original receipt/campaign harness contract;
- `packages/orion-research-harness/src/orion_research_harness/frontier_benchmark.py` — Q3 frontier-item / instrument-decision / deferred-score contract;
- `.github/workflows/q-series-publication-sync.yml` — push/PR gate that runs framework/binding, paper-refinement, Q3 frontier, Q1 proof-sanity and Q4 paired-analysis reproductions.

`src/orion/registry.py` carries the shared Q-series sync epoch and canonical V3 manuscript identities. A material publication-contract change must update registry, framework snapshot, final spec, content binding, affected manuscript/ledger and relevant harness/test surfaces together.

### Recursive paper-refinement rule

Paper improvement is treated as a bounded research process, not as prestige-style polishing.

The order is:

`claim/evidence foundation -> exact venue criteria -> independent review lenses -> concern classification -> minimum valid repair -> re-review -> scoped terminal`.

Allowed closure routes include adding decisive evidence, reanalysing existing evidence, correcting an error, clarifying/restructuring, narrowing/removing a claim, or changing target/article type. Missing scientific evidence cannot be converted into a higher score by prose.

Internal scores are prioritization/debugging signals only. A `READY_FOR_SCOPED_TARGET` terminal means the **bounded claim** clears the local paper/venue contract; it does not predict acceptance or create external authority.

### Current paper asymmetry is load-bearing

The final spec intentionally does not give all four papers the same terminal.

- Q1: internally clears PRX Quantum scoped preflight and npj Quantum Information fallback for the sharp theorem.
- Q2: scoped methodology/case-study paper is internally ready for an npj-level AI-for-science attempt with positioning risk; Nature Computational Science general-method framing remains evidence-blocked.
- Q3: systems/benchmark contract is technically refined, but predictive/calibration impact remains evidence-blocked at one prospective item; systems checks cannot promote it.
- Q4: exact-synthetic matched-information benchmark is internally ready for a scoped npj-level attempt with positioning risk; Nature Machine Intelligence real-agent framing remains evidence-blocked pending real transfer.

Changing one of those blockers requires the corresponding new evidence and a new sync epoch/spec, not an editorial rewrite.

### Q-series content-binding rule

P6-P8 use per-directory `SHA256SUMS`/manifest bindings; Q1-Q4 use a cross-paper binding over the canonical publication package. Historical drafts remain provenance and may stay outside the canonical binding. Canonical V3 manuscripts, V3 ledgers, nearest-work/figure contracts, review verdicts and secondary publication analyses may not drift silently.

### Owner-skipped external expert review

The owner elected not to require a separate external quantum-expert pre-review for Q1. The final spec records this as `SKIPPED_BY_OWNER`. The sync checker rejects any attempt to encode that skip as a scientific pass. Journal peer review remains external scrutiny if the paper is submitted.

### Successor-study rule

Q2's cross-domain comparison, Q3's multi-frontier series and Q4's real-domain matched-information study remain registered successor research. They are required only for claims that exceed the current scoped terminals. They must never be described as executed until prospective evidence actually exists.

## Nearest-work rule

Every flagship/candidate claim maintains a nearest-work case. A novelty case is blocked while a nearest-work route remains plausibly absorbing or when equivalent prior work is located. `NOT_LOCATED_IN_BOUNDED_SEARCH` is not novelty certification.

## Two-level evidence rule

Software/tests may establish local implementation/provenance/falsifier state. They do not establish external scientific authority. Paper-specific empirical and theorem claims remain governed by their own evidence ledgers. Green CI cannot promote a manuscript beyond its frozen claim ledger or evidence terminal.

## External evidence may not be declared by booleans

The broader flagship system still consumes typed external evidence manifests rather than caller-declared success booleans. Missing, duplicate, self-verified, post-hoc, stale or binding-mismatched evidence remains `CANNOT_CHECK`; a verified failure remains a failure rather than being softened into missing evidence.
