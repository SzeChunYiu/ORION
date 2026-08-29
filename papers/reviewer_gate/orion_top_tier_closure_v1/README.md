# ORION 01–25 top-tier scientific closure gate (v1)

- `BASELINE_COMMIT`: 703b87db22dce3981f13b407b56f4a656310632f
- `ASSESSMENT_DATE`: 2026-08-29
- `SCIENTIFIC_AUTHORITY_DELTA`: NONE
- `CURRENT_TOP_TIER_READY_COUNT`: 0

This gate is prospective. Paper-local adverse/retraction ledgers, raw evidence, protocols, custody, and validators remain controlling. It cannot rescue a retracted identity, turn `CANNOT_CHECK` into support, or count an open pull request as evidence.

## Latest main lineage reviewed
- `703b87db22dce3981f13b407b56f4a656310632f` — fix(orion-24): reconcile rendered manifest SHA256 — Scientifically neutral one-line digest reconciliation after the known-cause generator correction; no manuscript, protocol, raw-data, or terminal change.
- `ad61a71d226dd3aae1f5f83c8b259786aa01ea7b` — docs(orion-15): distinguish intentional omission from unwired observation — Makes unwired/missing cells inadmissible as either positive or adverse outcomes; intentional materialized omissions retain their declared reading.
- `f7780fb16aeca827a7a02534ae89ff6617239029` — docs(repo): define intentional omission versus unwired artifact — Adds the repository-wide fail-closed reading rule and validator support without changing any paper decision.
- `7e364d514b5957a2acab120e03027ff26ebdde87` — docs(orion-08): record paired mean-effect uncertainty — Merges all 12 paired bootstrap intervals and narrows the manuscript where intervals contain zero; directional Holm-controlled sign evidence remains a distinct estimand and creates no mean-effect promotion.
- `b04214b1076665aaaf3b3f78ae04f597bc403178` — docs: name the positive-demonstration control, and split the NOT_SUPPORTED terminal (#1735) — No new authority; adds a non-tautology control rule and distinguishes ORION-02 adverse revival from ORION-21/22/23/25 favourable bounded non-promotion.
- `18a54488c2a8a0231e68ee56822f516dbde32b21` — docs(publication-closure): ranked top-tier science gap list for ORION-01..25 (#1740) — Assessment only; records verified ORION-08/13 threats and labels 23 of 25 other rows as leads rather than findings.
- `6095870575a32551402535b2a653e9110abf0884` — science(orion-08): close the family-wise half of the multiplicity argument (#1737) — Exact paired sign tests with Holm correction: 11 of 12 survive; the prespecified exact-tie control remains the sole non-survivor; mean-undetermined rows are not upgraded.
- `754a62719062b1b623d9d31fce232b0aab5b0ebe` — science(orion-21): state what the >=8/10 family gate can detect at n=10 (#1736) — Adds exact gate-design power and Clopper-Pearson intervals; excludes capability at the registered bar while leaving moderate capability unresolved.
- `adc4f719fb5208f5510a46ff6546bd74fe9b720e` — docs(matrix): the PDF finding said nine papers, and it is now two (#1734) — Production-state correction only; all manuscript entry points have byte-pinned PDFs, while ORION-02 and ORION-04 remain Markdown-only.
- `87e2bcb330d243b7062ddba1ca26e426632edeab` — audit(repo): complete all-branch evidence recovery sweep (#1727) — Establishes the recovered main-line evidence baseline while preserving adverse, null, CANNOT_CHECK, and retraction history.

## Expert panel and veto rights
- `E1_editor` — Senior cross-disciplinary editor experienced in significance, scope, claim hierarchy, and top-tier editorial triage. Veto: Veto unsupported significance, scope inflation, fragmented paper identity, or a manuscript that lacks a single decisive advance.
- `E2_domain_theory` — Domain scientist and formal-methods reviewer matched to each paper's scientific mechanism, theorem, or causal interpretation. Veto: Veto incorrect mechanisms, missing assumptions, circular definitions, theorem overreach, or a claim not identifiable from the design.
- `E3_design_statistics` — Experimental-design, biostatistics, causal-inference, uncertainty-quantification, and multiplicity specialist. Veto: Veto unpowered designs, post-hoc endpoints, invalid units of analysis, missing calibration, uncontrolled multiplicity, or seed/cohort pseudoreplication.
- `E4_external_validation` — Independent replication and generalization specialist covering site, cohort, task-family, implementation, and operator shift. Veto: Veto claims whose decisive evidence remains single-site, single-family, same-team, synthetic-only, or drawn from the development distribution.
- `E5_reproducibility_governance` — Research-software, provenance, evidence-custody, adversarial replay, and claim-to-artifact binding specialist. Veto: Veto unverifiable artifacts, mutable or missing raw outputs, unpinned environments, stale-branch evidence, failed replay, or adverse-history deletion.
- `E6_literature_novelty` — Systematic-search and citation-integrity specialist with responsibility for primary-source novelty and nearest-neighbour comparison. Veto: Veto novelty claims lacking a dated, reproducible search; full-text verification; and an explicit difference from the strongest prior methods.
- `E7_safety_ethics` — Adversarial-testing, responsible-innovation, clinical/participant-risk, dual-use, and failure-mode specialist. Veto: Veto unsafe deployment language, hidden subgroup harms, missing human/clinical governance, or failure modes without a bounded fallback.

## Portfolio-wide gates
- At least 3 positive primary endpoints, with the seed/replication rule frozen before outcomes.
- Use at least five stochastic training seeds unless a paper-specific higher minimum is declared; broad claims require multiple independent cohorts, sites, systems, theorem families, or domains.
- Novelty requires a dated reproducible primary-source search and full-text verification. Search snippets, unverified DOI metadata, and citation-count rhetoric are inadmissible.
- Use the true experimental/generalization unit, report effect sizes and uncertainty, predeclare multiplicity handling, include failures, and never count seeds or repeated measurements as independent cohorts.
- No open pull request, stale branch, placeholder, self-declared manifest, missing external packet, or CANNOT_CHECK record counts as positive evidence.
- Methods, Results, Discussion, Abstract, figures, claim ledger, and conclusions unlock only after the corresponding evidence gate passes; wording cannot outrun evidence.
- Hard retractions remain authoritative. Only a separately named successor with new admissible evidence may advance, and it cannot restore the retracted paper identity.
- A submission candidate requires paper-local validators, repository validators, clean rendering, figure source data, reference attestation, and independent replay to pass on one pinned commit.

## Latest overlapping open work — zero evidence credit
- `PR #1732` — ORION-02 reproducible paired-control inference and claim narrowing — `state=open` — `counts_as_evidence=false`
- `PR #1733` — repository content-binding writer/checker path-set repair — `state=open` — `counts_as_evidence=false`
- `PR #1739` — ORION-13 baseline-degeneracy, discordance, and coordinate-coverage battery — `state=open` — `counts_as_evidence=false`
- `PR #1741` — overlapping current-state ORION-01–25 science-gap register — `state=open` — `counts_as_evidence=false`
- `PR #1744` — executable ORION-08 and ORION-13 closure batteries — `state=open` — `counts_as_evidence=false`
- `PR #1746` — fail-closed ORION content-binding gate and historical-snapshot protection — `state=open` — `counts_as_evidence=false`

## Contract parts

- `ORION_01_03.md`
- `ORION_04_05.md`
- `ORION_06_08.md`
- `ORION_09_10.md`
- `ORION_11_13.md`
- `ORION_14_15.md`
- `ORION_16_18.md`
- `ORION_19_20.md`
- `ORION_21_23.md`
- `ORION_24_25.md`

The checker proves structural completeness and non-promotion discipline only. It does not prove a scientific claim or make a manuscript submission-ready.
