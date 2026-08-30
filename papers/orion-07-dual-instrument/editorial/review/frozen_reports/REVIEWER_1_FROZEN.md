# Isolated Pre-Submission Review — TMLR Claim/Evidence Assessment

## 1. Assessment boundary

This review considers only:

- `MANUSCRIPT.tex`
- `REFERENCES.bib`
- `CASE_SERIES.json`

No repository history, supplements, code, raw case records, editorial material, other reviews, or external citation sources were inspected. Consequently, assertions requiring those materials are marked **not auditable from the supplied packet**, rather than false.

I apply a TMLR-style claims/evidence standard emphasizing technical correctness, methodological validity, reproducibility, and whether each central claim is supported by clear and convincing evidence. I do not predict an editorial decision.

## 2. Summary of contribution

The manuscript proposes a prospective dual-instrument protocol for unresolved scientific questions. A tool-capable host and a deterministic typed controller:

1. receive a frozen scientific state;
2. independently record a diagnosis and proposed experiment;
3. have their relation recorded before the outcome;
4. are scored later, with diagnosis and experiment selection treated separately.

Three questions are reported. The instruments agree on both coordinates in all three. In the reweighted-objective case, a claimed exhaustive census finds zero predicate–label mismatches across 39,489 low-order cases. Under the reported scoring map, both diagnoses are therefore classified as misaligned while both experiment selections remain aligned.

The manuscript is commendably explicit that this is not evidence of reliability, calibration, statistical independence, population frequency, or generalization. Its central evidentiary burden is instead to establish:

- genuine prospective chronology;
- exact frozen decisions and scoring maps;
- correctness and completeness of the finite computations;
- auditable contamination handling;
- operational fail-closed behavior.

Those elements are described, but not demonstrated by the three supplied files.

## 3. Major Concerns

### MC-01 — Prospective status and completeness are asserted rather than demonstrated

- **Severity:** Critical
- **Blocking:** Yes
- **Target criterion:** Central claims must be supported by auditable, convincing evidence; prospective claims require verifiable chronology.
- **Claim pointer:** `MANUSCRIPT.tex`, Abstract; §Prospective measurement contract; §Three prospectively frozen questions; §Results.
- **Evidence pointer:** `CASE_SERIES.json`, `valid_questions[*].prospective_freeze_verified`; `study_boundary.valid_question_count`.
- **Concern:** The JSON contains three Boolean assertions that prospective freeze was verified, but no frozen packet identifiers, hashes, dates, event order, contemporaneous decisions, scoring-map versions, or outcome-artifact identities. It also does not establish that these were the complete set of valid questions rather than a post-outcome selection.
- **Why it matters:** Prospectivity is the defining distinction between this work and retrospective task construction. A post-result summary cannot itself establish that the evidence, vocabularies, decisions, and scoring branches existed unchanged before the outcomes.
- **Resolution test:** For every case, provide a machine-verifiable manifest binding: frozen question, admitted evidence, diagnosis vocabulary, experiment vocabulary, scoring map, both instrument outputs, relation record, and later outcome artifact. The manifest must demonstrate that the first six items precede the outcome and that their hashes remained unchanged. A verifier should reject any reordered, substituted, or modified artifact.

### MC-02 — The two instruments and their evidence interface are insufficiently specified

- **Severity:** High
- **Blocking:** Yes
- **Target criterion:** Methods must be sufficiently precise to evaluate technical correctness and reproduce the claimed measurement.
- **Claim pointer:** Abstract; §The two instruments; §Introduction, claim of “different decision machinery.”
- **Evidence pointer:** No instrument configuration, transcript, controller rule set, or transcription map appears in `CASE_SERIES.json`.
- **Concern:** The host model/version, prompting procedure, tool permissions, sampling or retry policy, raw output, and parser are not supplied. The controller’s typed vocabulary, complete rules, observations, and execution trace are also absent. Moreover, the abstract says both instruments receive the “same frozen evidence state,” whereas the methods say the controller receives observations transcribed from that packet.
- **Why it matters:** Without these materials, neither heterogeneity of execution nor evidence equivalence is auditable. A lossy or interpretive transcription could determine the controller answer. The agreement observations also cannot be reconstructed.
- **Resolution test:** Release the exact frozen host input and raw output receipt, model/configuration metadata, parser disposition, typed controller input, complete controller rules/code, and execution trace for each case. A parity test should identify every packet fact exposed to each instrument. If the inputs are not identical, revise “same evidence state” to the exact weaker relation, such as “controller observations derived from the same packet.”

### MC-03 — The agreement-with-misdiagnosis result depends on an unavailable scoring map and ambiguous diagnosis semantics

- **Severity:** Critical
- **Blocking:** Yes
- **Target criterion:** Headline conclusions must follow logically from predeclared hypotheses and observed evidence.
- **Claim pointer:** Abstract; §Deferred scoring; §Reweighted-objective census question; Tables 1–2; Conclusion.
- **Evidence pointer:** `CASE_SERIES.json`, `valid_questions[2].instrument_relations` and `deferred_alignment`.
- **Concern:** The supplied JSON records both diagnoses as false-aligned values, but does not contain the original diagnosis tokens or predeclared branch map. The narrative alternates among “objective-scoped,” “expected not to transfer unchanged,” and “would change.” Zero mismatches on a low-order finite domain contradict a finite-domain prediction of change, but it does not by itself falsify the broader proposition that the predicate is objective-scoped or might change at larger sizes.
- **Why it matters:** The central counterexample requires an unambiguous proposition, a prospectively fixed domain, and a prospectively fixed rule under which the observed result makes that proposition misaligned. Otherwise “misdiagnosis” could be a post-outcome semantic contraction or merely failure to confirm a broader prediction.
- **Resolution test:** Publish the verbatim frozen diagnosis choices and the complete scoring map. A deterministic scorer must map the frozen zero-mismatch outcome to both diagnoses being misaligned without human reinterpretation. If the original diagnosis was not explicitly limited to the census domain, narrow the result to “the predicted change was not observed on the frozen low-order domain” rather than claiming the broader diagnosis was falsified.

### MC-04 — The three scientific outcomes are not technically reproducible from the supplied evidence

- **Severity:** Critical
- **Blocking:** Yes
- **Target criterion:** Empirical and computational claims require enough evidence to establish correctness, coverage, and reproducibility.
- **Claim pointer:** All three subsections of §Three prospectively frozen questions; §Results; §Limitations and unearned interpretations.
- **Evidence pointer:** `CASE_SERIES.json`, `valid_questions[*].bounded_scientific_observation`.
- **Concern:** The packet supplies only aggregate summaries:
  - The regime case has no formal predicate, domain definition, domain size, instances, or closure certificate.
  - The support-threshold case has no 53-row data, instance definitions, optimization formulation, solver/certificate output, or full independent check. Repeated execution establishes repeatability, not correctness.
  - The census case has no object universe, predicate or label formula, quotient construction, enumeration code, per-case outputs, or proof that 38,760 quotient representatives are complete and nonduplicated. The second implementation reportedly checks only 24 cases, not the complete census.
- **Why it matters:** “Exact,” “complete,” “exhaustive,” and “zero mismatches” carry a stronger burden than aggregate counts. The headline misdiagnosis classification depends directly on completeness and correctness of the census.
- **Resolution test:**  
  1. Define each finite domain and all predicates/objectives mathematically.  
  2. Supply the complete 53-row result table and exact optimization witnesses or certificates.  
  3. Supply all 39,489 census records or a reproducible generator, including canonicalization of the two-object quotient.  
  4. Run a genuinely separate implementation over the complete census, or provide a formal coverage/count argument plus an independent label oracle.  
  5. Require exact equality of case keys, predicate values, labels, positive counts, and mismatch counts.  
  6. Provide the formal regime predicate and checkable closure artifacts for the first case.

### MC-05 — Contamination retention is internally recorded but not auditable, and the selection/stopping process is unspecified

- **Severity:** High
- **Blocking:** Yes
- **Target criterion:** Prospective experimental design must expose exclusions, replacements, and stopping rules sufficiently to rule out outcome-dependent selection.
- **Claim pointer:** §Unit of analysis; §Chronology and fail-closed exits; §Retired candidate questions; §Contamination as data about the protocol.
- **Evidence pointer:** `CASE_SERIES.json`, `retired_candidates`.
- **Concern:** The names, reasons, and retained status of two candidates are internally consistent between manuscript and JSON. However, no contemporaneous candidate registry, visibility test, retirement time, replacement rule, or stopping rule is supplied. “Outcome-oriented surface visible” is not operationally defined.
- **Why it matters:** The manuscript relies on complete disclosure rather than statistical sampling. Without a candidate ledger and stopping rule, it is impossible to determine whether other invalid, disagreeing, or unresolved candidates existed or whether cases were pursued until the desired pattern appeared. This does not create a population estimate, but it affects the claimed completeness and integrity of the case series.
- **Resolution test:** Supply a time-ordered candidate ledger containing every admitted candidate, admission criterion, freeze attempt, contamination check, disposition, replacement relation, and the rule that terminated recruitment at three valid questions. A verifier should reproduce counts of three valid and two contaminated cases and confirm that no valid candidate was omitted.

### MC-06 — The fail-closed behavior is a stated policy, not an experimentally established property

- **Severity:** High
- **Blocking:** Yes for presenting fail-closed handling as an implemented property; No if narrowed explicitly to an untested design rule.
- **Target criterion:** Robustness and failure-handling claims must be supported by tests exercising the relevant failure paths.
- **Claim pointer:** Abstract; §Chronology and fail-closed exits; §Known fail-closed defects; §Limitations and unearned interpretations.
- **Evidence pointer:** `CASE_SERIES.json`, `known_instrument_limitations[*].triggered_in_valid_cases = false`.
- **Concern:** Both known defects are disclosed and appropriately described as untriggered limitations. However, no evidence demonstrates that malformed success actually becomes a typed invalid/cannot-check result, that immutable successful content remains retained, or that recovery cannot silently promote the case into a valid score.
- **Why it matters:** A fail-closed rule is only protective if all relevant state transitions enforce it. An untested parser or retry path could instead omit a case, reuse malformed content, or convert an invalid case into an apparently valid one.
- **Resolution test:** Add fault-injection tests for both defects. Each test must show: immutable retention of the original envelope; a typed invalid/cannot-check disposition; exclusion from valid-question counts and alignment fields; and rejection of in-place repair or retry promotion. If such tests cannot be supplied, describe these only as intended policies and unresolved risks.

## 4. Minor Comments

### MI-01 — Bibliography filename case is not portable

- **Severity:** Moderate
- **Blocking:** Yes for a case-sensitive build environment
- **Target criterion:** Submission artifact must compile reproducibly.
- **Claim pointer:** End of `MANUSCRIPT.tex`, `\bibliography{references}`.
- **Evidence pointer:** The supplied file is named `REFERENCES.bib`.
- **Concern:** The lowercase bibliography stem may work on a case-insensitive filesystem but fail on a case-sensitive Linux environment.
- **Why it matters:** This is a direct build failure independent of scientific merit.
- **Resolution test:** Rename the file or change the bibliography command so the cases match, then run a clean LaTeX build in a case-sensitive container.

### MI-02 — “Independent” and “repeated” validation terminology should be made exact

- **Severity:** Moderate
- **Blocking:** No
- **Target criterion:** Claims should be precise and should not invite unsupported independence or validation interpretations.
- **Claim pointer:** Support-threshold and reweighted-census subsections; §Limitations; §Reproducibility.
- **Evidence pointer:** Partial “independent brute-force” checks, a 24-case second path, repeated complete runs, and references to “independently replayed” evidence.
- **Concern:** Repeated execution of one implementation tests repeatability, not correctness. A second implementation over 24 cases validates those cases, not the entire 39,489-case census. “Independently replayed” may also be confused with the expressly prohibited claim of instrument independence.
- **Why it matters:** The distinction is central in a manuscript about relations between dependent instruments and delayed validation.
- **Resolution test:** Label each check as same-code repetition, separate implementation, full-domain cross-check, or partial spot check. Reserve “independent” for a clearly defined independence dimension.

## 5. Claim/evidence reconciliation

| Claim | Evidence present in supplied files | Reconciliation |
|---|---|---|
| There are three reported valid questions | Three JSON entries and `valid_question_count: 3` | Structurally consistent, but prospective validity is not established; see MC-01. |
| All three instrument pairs agreed on diagnosis and experiment | JSON relations match Table 2 | Internally consistent; raw outputs and relation computation are unavailable; see MC-02. |
| Cases 1–2 have aligned diagnoses and experiments | JSON matches the manuscript | Internally consistent only; scoring maps and outcome artifacts are unavailable; see MC-03–MC-04. |
| Case 3 has two misaligned diagnoses and two aligned experiments | JSON matches Table 2 | Central classification is not independently derivable without exact diagnosis text and scoring map; see MC-03. |
| Support-threshold panel contains 53 rows and zero gaps | Manuscript gives \(3+2+24+24=53\); JSON gives 53 and zero | Arithmetic is consistent; row contents and exact optimization evidence are absent. |
| Census contains 39,489 cases | \(729+38{,}760=39{,}489\), consistent with JSON | Arithmetic is correct; exhaustiveness, quotient construction, and zero-mismatch computation are unverified. |
| Two candidates were contaminated and retained | Manuscript and JSON agree on names and reasons | Internally consistent; timing and completeness are not auditable; see MC-05. |
| Two defects are retained fail-closed limitations | Manuscript and JSON agree that they were untriggered and unrepaired | Disclosure is adequate; operational fail-closed behavior is untested; see MC-06. |
| No reliability, calibration, population-frequency, causal/statistical-independence, or generalization claim is made | Explicit negative flags in JSON and repeated manuscript limitations | Reconciled. No prohibited aggregate rates were identified. |
| All scientific results remain finite-domain bounded | Repeated explicit limitations; `larger_domain_claimed: false` for each case | Scope language is appropriately conservative, but the finite domains themselves require formal definition. |
| The cited literature supports the related-work characterizations | Bibliographic metadata only | **Cannot check** without reading the cited works; no bibliographic fabrication is inferred. |
| A sanitized archive and independent verifier provide reconstruction | Asserted in §Reproducibility | **Cannot check** because neither is included in the supplied packet. |

## 6. Minimum-sufficient repair tests

1. **Prospective custody test:** Verify immutable hashes and chronological ordering for every frozen packet, decision, scoring map, relation record, and later outcome.
2. **Instrument reconstruction test:** Reconstruct controller decisions exactly and verify the preserved host outputs and parser dispositions from fully specified inputs.
3. **Evidence-parity test:** Produce a field-level comparison of host-visible evidence and controller-visible observations; narrow “same evidence state” if they differ.
4. **Scoring-map test:** Apply a deterministic, frozen scorer to all three outcome artifacts and reproduce all twelve diagnosis/experiment alignment values, especially the two false diagnosis values in case 3.
5. **Scientific reproduction test:** Reproduce the regime certificate, all 53 support-panel rows, and all 39,489 census labels from disclosed definitions and implementations.
6. **Census completeness test:** Verify the one-object count, the two-object quotient count, canonicalization uniqueness, positive counts, and zero mismatches through a complete second path or equivalent formal coverage evidence.
7. **Contamination/completeness test:** Reconstruct the complete candidate ledger, retirement events, replacement logic, and stopping rule.
8. **Fail-closed fault-injection test:** Force both known defects and verify immutable retention, typed invalidity, exclusion from scoring, and prevention of repair promotion.
9. **Clean-build test:** Compile on a case-sensitive filesystem after resolving the bibliography filename mismatch.

A larger case series, confidence intervals, calibration analysis, or generalization study is **not** required to support the manuscript’s deliberately bounded logical contribution. The minimum repairs concern auditability of the contribution already claimed.

## 7. Risk / unsupported claims

| Risk level | Claim or interpretation | Assessment |
|---|---|---|
| **High** | The study was genuinely prospective and the three rows are the complete valid series | Unsupported by the supplied post-outcome summary alone. |
| **High** | The reweighted census is exhaustive and establishes zero mismatches on the declared domain | Numerically consistent but not technically auditable. |
| **High** | Agreement-with-misdiagnosis is an established counterexample | Plausible, but conditional on the unavailable frozen diagnosis wording, scoring map, and census correctness. |
| **High** | Both instruments received the same evidence state and used meaningfully different machinery | Insufficient specification; the controller received a transcription rather than demonstrably identical evidence. |
| **Medium** | Contaminated candidates were conservatively and completely retained | Internally recorded but not chronologically or operationally verified. |
| **Medium** | The instrument is fail-closed under the two known defects | Untested because neither defect triggered in the valid series. |
| **Medium** | Results were independently validated | Only partial second-path checks are described; repeated execution is not independent correctness validation. |
| **Low / controlled** | Reliability, calibration, accuracy, population frequency, instrument independence, or generalization | These interpretations are repeatedly and appropriately prohibited. |
| **Low / controlled** | Larger-domain invariance or an extension of the support-two theorem | Explicitly disclaimed. |
| **Low / controlled** | Productive experiment choice implies generally superior experiment selection | Explicitly disclaimed. |

Overall, the manuscript shows disciplined claim boundaries and unusually clear separation of agreement, diagnosis, experiment choice, contamination, and invalidity. The principal obstacle is not overgeneralization; it is that the supplied evidence is too aggregated to verify the prospective design and the finite computations on which the bounded central result depends.