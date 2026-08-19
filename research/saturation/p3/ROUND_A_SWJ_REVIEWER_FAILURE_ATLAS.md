# P3 saturation — Round A SWJ reviewer-failure atlas

Date: 2026-08-19  
ORION base: `d73e65c10f4f3b7ae773cea667f6dccd1507e8f0`  
Nature-skills subject: `Yuan1z0825/nature-skills@96e41d3348748796c239cf5cb85bd947e5b02d38`  
Parent: #491 / #488

This artifact uses Semantic Web Journal's public review history as empirical editorial/reviewer evidence. It does not copy prose from accepted papers; it records recurring review tests that P3 should pass before submission.

## 1. Official SWJ review contract

For a Full Paper, SWJ explicitly reviews originality, significance and writing quality and encourages evaluation detail sufficient for replication. Since 2021, relevant data and software must be provided to the maximum feasible extent at a stable URL, with README/instructions sufficient for reviewers to inspect or reproduce the experiment.

This creates a strong match to P3's current source-bound public-reference package but also a strict burden: the scoped structured-mapping claim must be visible immediately, and the released artifacts must be organized as an evaluator can actually use them.

## 2. Public-review cases sampled in Round A

### Case A — `Background Knowledge in Ontology Matching: A Survey`

Decision history: revised from broader schema-matching framing to ontology matching, ultimately accepted.

Reviewer lessons:

- **scope wording must change everywhere when scope narrows**: a reviewer still saw schema-matching framing in abstract/introduction after the authors changed the target;
- search strategy parameters and inclusion/exclusion criteria are reviewable scientific objects, not hidden workflow details;
- evaluation material that does not serve the paper should be removed rather than retained for apparent completeness;
- figures/tables should appear where they support the argument, not merely where generated;
- references are demanded for apparently obvious domain statements when they perform historical/definitional work;
- replication/data files are explicitly reviewed for organization, README quality and completeness.

P3 consequence: the manuscript's scope contraction from a broad cross-domain atlas to **already-structured public-reference mapping/obstruction** must be perfectly consistent in title, abstract, introduction, methods, evaluation, results, limitations and package. Any residual sentence implying natural-paper extraction or a completed expert atlas is a major risk.

### Case B — `Survey on complex ontology matching`

Decision history: major revision -> accepted.

Reviewer lessons:

- reviewers accept a technically ambitious paper when scope/classification are clear, but definitions are inspected literally;
- a concept cannot be described as a triple while examples/semantics implicitly add a fourth coordinate;
- evaluation/limitations must be discussed as first-class aspects, not afterthoughts;
- broad coverage alone does not excuse formal imprecision.

P3 consequence: `ALIGNED / RELATED / OBSTRUCTION / UNRESOLVED`, GLUE semantics, referent/construct/measurement/context coordinates and mapping conditions need one canonical definition each. Confidence/uncertainty must not be smuggled into a relation whose formal arity excludes it.

### Case C — `Foundational Ontologies meet Ontology Matching`

Decision history: major/minor revision -> accepted.

Reviewer lessons:

- broad-community usefulness, balanced coverage and readability matter alongside technical completeness;
- after core concerns are fixed, reviewers still inspect terminology, grammar and precise claims;
- a survey/positioning paper earns acceptance by making its taxonomy useful to readers, not by listing work exhaustively.

P3 consequence: nearest work should be synthesized around **what kind of semantic mismatch is being protected against** rather than becoming a long list of schema/KG papers.

## 3. Recurring SWJ rejection / major-revision risks for P3

| Risk | Why SWJ reviewers care | P3 resolution test |
|---|---|---|
| scope drift | reviewers compare abstract/introduction/evaluation claims literally | no sentence implies raw-text/expert-atlas/downstream completion |
| unclear novelty boundary | Semantic Web has mature ontology/schema/KG/provenance literature | every mechanism has donor/residual disposition |
| weak benchmark realism | mapping papers are expected to justify datasets/gold/evaluation | clearly state that P3 tests an already-structured mapping calculus and why that bounded object is scientifically useful |
| baseline incompleteness | reviewers expect comparison to established semantic-web approaches | strongest compatible canonicalization/mapping controls must be named; unsupported unavailable systems remain explicit |
| relation/coordinate ambiguity | formal definitions are scrutinized | one canonical arity/type/semantic contract per relation |
| insufficient data/software | SWJ evaluates resource usability | stable package, README, exact commands, immutable gold/provenance/checksums |
| missing search/inclusion logic | literature claims must be reproducible | record search routes and selection rationale in saturation artifacts |
| verbosity over usefulness | supplementary evidence can carry review criteria | main text tells the shortest sufficient mapping story; audit/provenance detail can live in supplement/repository |

## 4. P3 Round-A review questions

These become inputs to later isolated `nature-reviewer` packets:

1. Can a Semantic Web reviewer explain the exact P3 contribution without mentioning ORION's broader programme?
2. Is the current mapping relation formally clearer than the systems it critiques, or does P3 introduce more coordinates than its evidence can validate?
3. Does the 32+32 public-reference study test an interesting semantic-web failure mode, or look like a handcrafted toy benchmark?
4. Are the flat/exact controls strong enough for the **scoped** claim, and are stronger unavailable/natural-paper comparisons clearly future work?
5. Does P3 distinguish semantic mismatch from lexical difference, provenance difference, contradiction, and representational plurality without conflating them?
6. Can a reviewer reproduce the exact confirmatory result from the stable package without ORION-internal knowledge?
7. Are all data/software artifacts immutably hosted and organized for external review?

## 5. Round-A terminal

`SWJ_REVIEW_ATLAS_ROUND_A_STARTED`.

This is not enough to satisfy #491. Round B should add 8–15 modern full-paper/open-review cases, including accepted, major-revision and rejected/desk-rejected examples close to ontology matching, KG integration, schema/data integration and LLM+KG evaluation.