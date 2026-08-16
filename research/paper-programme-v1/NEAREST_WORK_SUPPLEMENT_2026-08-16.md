# Nearest-work supplement — 2026-08-16 flagship falsifier round

This supplement records nearest work that materially changed the five-paper implementation after the V1 atlas was frozen. It follows the same rule: absorb the mechanism first, then shrink the ORION novelty boundary.

## Paper V — ADIAS: issue-centric self-improvement

**Work:** *Automated Design of Interactive Agentic Systems* (ADIAS), arXiv:2608.06410.

**Mechanism absorbed:** persistent issue-centric optimization. The durable object of improvement is the unresolved issue, with identity/lifecycle/evidence/intervention-outcome history carried across candidate generations.

**Disposition:** `ADAPT`.

**ORION implementation:** `src/orion/self_orion/issue_state.py` (`DevelopmentIssue.v1`). ORION keeps a stable issue identity, candidate/supported causes, discriminator evidence, failure episodes, interventions and lifecycle transitions. Harmful/null interventions remain attached to the issue.

**Removed from ORION novelty:** persistent issue identity/state for self-improvement is not claimed as novel.

**Surviving difference:** issue-centric persistence is composed with ORION's recurrence-not-cause rule, invention-readiness gate, replay/fresh-transfer distinction, protected evaluator chronology, negative-history preservation and no self-certification.

## Paper IV — search-time contamination / evaluator integrity

**Work families absorbed:** search-time contamination benchmarks for web-searching agents; reward-hacking/evaluator-tampering and held-out leakage benchmarks for coding agents.

**Disposition:** `COMPOSE`.

**ORION consequence:** Paper IV's external promotion gate now requires explicit search-time contamination auditing, evaluator locking before candidate outcomes, held-out access telemetry and matched source-aware verifier baselines. These conditions are represented in `external_authority_gate`; absence yields `CANNOT_CHECK` rather than a soft caveat.

**Removed from ORION novelty:** detecting benchmark leakage or evaluator tampering is not an ORION novelty claim.

## Paper III — scientific semantic projection

**Parent work absorbed:** scientific information extraction/discourse and semantic-structure work (including SciERC/SciIE/UCCA-style structured meaning).

**Disposition:** `ADAPT`.

**ORION consequence:** the first exact atlas falsifier showed that `SourceProjection` + `RepresentationMapping` alone left the text-to-scientific-meaning boundary implicit. `ScientificMeaningProjection.v1` now exposes predicate roles, referents, constructs, measurements, temporal context, polarity, modality, discourse, attribution, assumptions and unresolved ambiguity before a mapping/GLUE decision.

**Removed from ORION novelty:** semantic parsing/scientific IE itself is not claimed as novel.

**Surviving difference:** the typed meaning projection participates in projection-preserving identity/context/measurement mapping, obstruction and recoverable global portrait reconstruction.

## Paper I — action-family distinction after diagnosis

The hidden-shift negative control found a local defect rather than new nearest work: singular responsibility was incorrectly treated as sufficient license for `REFRAME`. The repair separates *diagnosis* from *repair family*: `EVIDENCE` and `EXECUTION` responsibility now block formulation rewrite and require acquisition/execution repair. METHOD/EVALUATOR remain protected Self-ORION coordinates.

This episode is retained as development evidence because it validates the project's failure-learning principle: a falsifier should be allowed to change the machine.

## Paper II — no new novelty claim from coverage estimation

The V1 route-ensemble result remains unchanged: capture-recapture is historical nearest work; route independence must be earned and population estimates remain diagnostic-only. The flagship local suite therefore tests refusal behavior as strongly as positive retrieval performance.
