# Chaptered TeX migration plan for Q1-Q4

The active PR #829 owns the current scientific masters and target wrappers. This
plan is additive and does not create a competing master. Its paths become the
required per-paper layout when the active lane incorporates the scientific
repairs.

## Common package contract

Every paper directory must contain:

```text
main.tex
sections/
references.bib
figures/
supplement/
Makefile or documented build script
BUILDING.md
```

`main.tex` is the only canonical root. Each numbered scientific chapter is one
TeX file included with `\input{}`. Tables with substantive scientific meaning
live beside the section that interprets them; generated figures and data have a
machine-readable source manifest. Availability and repository details do not
interrupt the scientific narrative.

The review package must not expose project-internal identifiers, branch names,
commit cuts, local paths, receipt filenames, P/Q ownership labels, or public
repository history. Exact artifact bindings belong in an anonymized supplement
or in the non-anonymous post-acceptance archive.

## Q1 structure

```text
orion-05-tare-expressivity/
  main.tex
  sections/01_introduction.tex
  sections/02_problem_and_objective.tex
  sections/03_failed_support_one_families.tex
  sections/04_support_two_closure_theorem.tex
  sections/05_proof.tex
  sections/06_machine_certificate.tex
  sections/07_related_work_and_significance.tex
  sections/08_limitations.tex
  sections/09_conclusion.tex
  supplement/a_counterexample_certificates.tex
  supplement/b_exhaustive_local_inequality.tex
  supplement/c_reproducibility.tex
  references.bib
```

The complete proof is load-bearing main text or a formally incorporated
appendix, not an external protocol. Internal grammar names become mathematical
definitions. The machine checker corroborates the proof; it does not replace it.

## Q2 structure

```text
orion-06-recursive-recovery/
  main.tex
  sections/01_introduction.tex
  sections/02_related_work.tex
  sections/03_asserted_transition_model.tex
  sections/04_safety_invariants.tex
  sections/05_retrospective_case_selection.tex
  sections/06_graph_results.tex
  sections/07_semantic_adjudication.tex
  sections/08_discussion_and_limits.tex
  sections/09_conclusion.tex
  supplement/a_edge_provenance_tuples.tex
  supplement/b_complete_denominator.tex
  supplement/c_checker_specification.tex
  references.bib
```

If Q2 remains retrospective, title, abstract, Methods, and Discussion all say
so. “Causal graph,” “non-cherry-picked universe,” and policy-effectiveness
language are excluded. If Q2-P1 runs, its prospective methods and results are a
new chapter set under a versioned manuscript, never spliced into the old case as
if predeclared.

## Q3 structure

```text
orion-07-dual-instrument/
  main.tex
  sections/01_introduction.tex
  sections/02_measurement_problem.tex
  sections/03_historical_instruments_and_custody.tex
  sections/04_three_case_series.tex
  sections/05_scientific_outcomes.tex
  sections/06_construct_validity_audit.tex
  sections/07_historical_and_repaired_versions.tex
  sections/08_related_work_and_scope.tex
  sections/09_limitations.tex
  sections/10_conclusion.tex
  supplement/a_unit_manifests.tex
  supplement/b_analyzer_replay.tex
  supplement/c_contamination_and_invalid_receipts.tex
  references.bib
```

The existing article is a historical case audit unless Q3-P1 is executed. It
separates epistemic status, forecast, action, and deferred decision value. Model
execution is called provider-authenticated only when raw provider metadata is
bound.

## Q4 structure

```text
orion-08-typed-state/
  main.tex
  sections/01_introduction.tex
  sections/02_classical_theory_and_donors.tex
  sections/03_state_representation_and_policy_factors.tex
  sections/04_constructed_worlds.tex
  sections/05_exact_results_and_boundary_cases.tex
  sections/06_prospectivity_and_replay_audit.tex
  sections/07_scope_and_external_validity.tex
  sections/08_limitations.tex
  sections/09_conclusion.tex
  supplement/a_world_definitions.tex
  supplement/b_study_manifests.tex
  supplement/c_numeric_environment.tex
  supplement/d_factorial_successor_protocol.tex
  references.bib
```

The text distinguishes N4-A/B from co-developed N4-C/D/E/F3 and separates
information, inference, and policy interventions. Donor ties and no-advantage
regimes remain in the principal result display.

## Clean-build release test

For each paper:

1. create a fresh checkout at the submission source commit;
2. install the pinned venue style and exact TeX dependencies;
3. build bibliography and PDF from `main.tex` with no undefined citations,
   references, or control sequences;
4. fail on placeholder author/declaration text;
5. extract PDF text and compare all numbers/claims with source and receipts;
6. render every page and visually inspect equations, tables, captions, fonts,
   links, and overflow;
7. audit PDF metadata, URLs, filenames, acknowledgements, and supplement for
   anonymity where required;
8. archive source, dependency/style hashes, build log, PDF hash, and visual
   inspection receipt.

No structural manifest can substitute for this clean build.
