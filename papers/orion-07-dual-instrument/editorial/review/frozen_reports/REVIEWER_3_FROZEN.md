# Isolated Pre-Submission Review — TMLR

## 1. Assessment boundary

This review considers only:

- `MANUSCRIPT.tex`
- `REFERENCES.bib`
- `CASE_SERIES.json`

I did not inspect repository files, editorial records, prompts, code, hidden metadata, other reviews, or author identities. Bibliographic metadata and claimed external artifacts were not independently checked.

I apply the TMLR claims/evidence standard: central claims should be supported by accurate, convincing, and clear evidence, with adequate methodological reporting, reproducibility, availability, and appropriately bounded interpretation. This is not a prediction of an editor’s decision.

## 2. Summary of contribution

The manuscript proposes a prospective dual-instrument measurement contract for unresolved scientific questions. A tool-capable host and a deterministic typed controller independently record a diagnosis and next-experiment choice before resolving evidence exists. Agreement is recorded separately from later alignment.

The supplied case series reports:

1. Regime characterization: agreement on both coordinates; all four deferred alignment fields positive.
2. Support-threshold stress test: the same pattern, bounded to 53 rows.
3. Reweighted-objective census: agreement on both coordinates, but both diagnoses misaligned and both experiment choices aligned after a 39,489-case census with zero predicate–label mismatches.

The manuscript correctly presents this as a small, non-random case series and a bounded logical counterexample—not a reliability or performance study.

## 3. Major Concerns

### TMLR-MAJ-01 — Claimed anonymous verifier and availability package are not supplied

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Reproducibility; data/code availability; claims supported by accessible evidence
- **Claim pointer:** `MANUSCRIPT.tex:45`, `MANUSCRIPT.tex:295-299`
- **Evidence pointer:** `CASE_SERIES.json:1-105`
- **Concern:** The manuscript says the anonymous archive contains an independent verifier that reconstructs the alignment table and checks census arithmetic and absence of aggregate performance fields. Among the supplied material, there is only a summary JSON record; no verifier, executable instructions, environment specification, checksum, or machine-readable licence is present. The later-release commitment is also conditional on both lifting anonymity and subsequent author authorization.
- **Why it matters:** A reviewer can inspect internal consistency but cannot test the manuscript’s explicit reproducibility and availability claims. The JSON mirrors the reported conclusions rather than independently deriving them.
- **Resolution test:** In a clean, case-sensitive environment, an anonymous reviewer should be able to unpack the declared supplement, follow one documented command, and reproduce both result tables, the `729 + 38,760 = 39,489` arithmetic, and the aggregate-field check. The archive should state its version/hash, licence, dependencies, expected output, and a concrete post-review archival policy.

### TMLR-MAJ-02 — Prospective chronology and deferred scoring are stored as conclusions, not auditable evidence

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Accuracy and convincing evidence for the central prospective claim
- **Claim pointer:** `MANUSCRIPT.tex:67-75`, `MANUSCRIPT.tex:102-140`, `MANUSCRIPT.tex:169-180`, `MANUSCRIPT.tex:259-263`
- **Evidence pointer:** `CASE_SERIES.json:15-24`, `CASE_SERIES.json:33-42`, `CASE_SERIES.json:53-62`
- **Concern:** `prospective_freeze_verified: true` and the deferred alignment booleans are assertions. The sanitized record does not include the frozen admitted evidence, exact instrument decisions, predeclared scoring branches, freeze/outcome ordering evidence, or a derivation from later observations to alignment.
- **Why it matters:** The main counterexample depends on the scoring map genuinely preceding the census. Without an auditable frozen map, the packet cannot exclude retrospective relabelling or independently establish that the third-row diagnoses were misaligned under the original contract.
- **Resolution test:** For each case, provide anonymized, content-addressed freeze and outcome manifests containing the admitted-evidence hash, exact diagnosis and experiment selections, scoring branches, and an auditable ordering relation. A verifier must recompute relations and alignment without trusting the stored `true`/`false` fields. If contemporaneous evidence does not exist, narrow the prospective and predeclared-scoring claims rather than reconstructing it retrospectively.

### TMLR-MAJ-03 — The bounded scientific observations are not independently reproducible

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Clear and convincing empirical/computational evidence
- **Claim pointer:** `MANUSCRIPT.tex:145-180`, `MANUSCRIPT.tex:184-222`
- **Evidence pointer:** `CASE_SERIES.json:26-29`, `CASE_SERIES.json:44-49`, `CASE_SERIES.json:64-72`
- **Concern:**  
  - Case 1 does not define the registered domains, predicate, complementary family, or computational result in enough detail to inspect the alignment.
  - Case 2 does not supply the 53 rows, objective implementation, unrestricted and support-two optima, or brute-force outputs.
  - Case 3 supplies counts but not the admitted instance space, quotienting rule, predicate implementation, label computation, complete outputs, or cross-check records.
- **Why it matters:** Counts and outcome booleans alone cannot establish enumeration completeness, zero-gap/zero-mismatch findings, or scientific correctness. This affects all three evidence rows, including the headline counterexample.
- **Resolution test:** A fresh execution from sanitized specifications and data must recover the Case 1 finite-domain result, every Case 2 row and its zero-gap count, and the Case 3 domain counts, positive counts, and zero mismatches. Exact expected-output hashes should be provided.

### TMLR-MAJ-04 — The instruments are insufficiently specified for audit or replication

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Reporting completeness; reproducibility; reader clarity
- **Claim pointer:** `MANUSCRIPT.tex:79-85`, `MANUSCRIPT.tex:147-169`
- **Evidence pointer:** `CASE_SERIES.json:16-24`, `CASE_SERIES.json:34-42`, `CASE_SERIES.json:54-62`
- **Concern:** The host model/version, prompts, tool environment, decoding settings, number of calls, transcription procedure, and exact outputs are absent. The typed controller’s observation schema, rules, vocabulary, and executable implementation are also absent. The JSON records agreement and alignment but not the underlying decision values.
- **Why it matters:** “Heterogeneous decision machinery” and deterministic execution are methodological claims. Readers cannot determine what was held constant, what differed, or whether the controller would reproduce its recorded decisions.
- **Resolution test:** Publish an anonymized instrument specification containing exact prompts/inputs and frozen outputs, model and tool versions, execution settings, controller schemas/rules, and invalid/abstention handling. Replaying the controller must deterministically reproduce all three decisions. Any unavoidable limitation on re-running the language-model host should be stated explicitly and separated from auditability of its frozen output.

### TMLR-MAJ-05 — “Complete” case-series and no-omission claims lack a candidate-flow record

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Selective-reporting control; clear study boundary; generalization discipline
- **Claim pointer:** `MANUSCRIPT.tex:77`, `MANUSCRIPT.tex:184`, `MANUSCRIPT.tex:224-230`
- **Evidence pointer:** `CASE_SERIES.json:3-10`, `CASE_SERIES.json:75-89`
- **Concern:** The material reports three valid and two contaminated candidates, but does not define the candidate-generation frame, eligibility window, replacement order, stopping rule, or whether other questions were considered. The record therefore preserves the two stated contaminated candidates but cannot independently establish that no other rows or protocol events were omitted.
- **Why it matters:** Complete-case disclosure is central to the manuscript’s response to selective-reporting risk. A declared count is not independently sufficient to establish completeness.
- **Resolution test:** Provide a sanitized candidate-flow ledger and pre-specified inclusion/stopping rule accounting for every candidate in the study window. If no contemporaneous ledger exists, replace “complete series” and “no row is omitted” with language limited to the five reported events.

## 4. Minor Comments

### TMLR-MIN-01 — Bibliography filename case mismatch

- **Severity:** Minor
- **Blocking:** Yes
- **Target criterion:** Build reproducibility
- **Claim pointer:** `MANUSCRIPT.tex:311-312`
- **Evidence pointer:** Supplied filename `REFERENCES.bib`
- **Concern:** The source invokes `\bibliography{references}`, while the supplied file is named `REFERENCES.bib`.
- **Why it matters:** This can fail on case-sensitive build systems even if it succeeds on a case-insensitive local filesystem.
- **Resolution test:** Rename the file or change the bibliography command so case matches exactly, then compile from a clean case-sensitive environment.

### TMLR-MIN-02 — Scientific terminology is too dependent on unstated programme context

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Reader clarity
- **Claim pointer:** `MANUSCRIPT.tex:145-180`, `MANUSCRIPT.tex:193-197`
- **Evidence pointer:** `CASE_SERIES.json:14-72`
- **Concern:** Terms such as “donor construction,” “registered domains,” “support-two family,” “unary incumbent,” “boundary predicate,” and “reorder-quotiented” are not defined sufficiently for a reader outside the originating programme.
- **Why it matters:** The conceptual measurement contribution is understandable, but readers cannot readily interpret the scientific evidence or why each later observation follows its scoring branch.
- **Resolution test:** Supply concise definitions, explicit domain boundaries, and at least one worked scoring example without relying on internal programme documentation.

### TMLR-MIN-03 — “Independent” may be mistaken for external validation

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Claim precision
- **Claim pointer:** `MANUSCRIPT.tex:161`, `MANUSCRIPT.tex:178`, `MANUSCRIPT.tex:289`, `MANUSCRIPT.tex:297`
- **Evidence pointer:** No corresponding implementation or external-validation record appears in `CASE_SERIES.json`
- **Concern:** “Independent brute-force path,” “second implementation path,” “independently replayed,” and “independent verifier” could mean implementation independence or external research independence. The limitations state that outcomes were produced within the same programme.
- **Why it matters:** Readers may overinterpret implementation cross-checks as independent external confirmation.
- **Resolution test:** Define each use as implementation-level independence, personnel independence, or external validation. State explicitly where no external validation occurred.

## 5. Reproducibility and reporting assessment

| Item | Assessment |
|---|---|
| JSON validity and row count | Internally coherent: three rows are present and the declared count is three. |
| Complete alignment-table pattern | Recoverable from the JSON: rows 1–2 have four positive alignment fields; row 3 has two negative diagnosis and two positive experiment fields. |
| Census arithmetic | Internally consistent: `729 + 38,760 = 39,489`. |
| Contaminated candidates | Both stated candidates are retained, marked contaminated, and excluded from the valid count. |
| Unrepaired limitations | Both stated defects have `repaired_between_valid_cases: false`; neither is claimed to have triggered. |
| Aggregate performance promotion | None identified. Counts describe study structure/domains; no accuracy, agreement rate, reliability score, calibration estimate, or pooled performance statistic is promoted. |
| Internal programme identifiers | None identified in the supplied manuscript or JSON. Case names are generic; external bibliographic names are not programme identifiers. |
| Anonymization | Adequate within the supplied text: anonymous authors, no author affiliation, repository URL, internal project code, or self-identifying custody data are visible. Unseen PDF/build metadata cannot be assessed. |
| Prospective chronology | Not independently verifiable from the JSON. |
| Scoring-map provenance | Not supplied. |
| Scientific computation | Not reproducible from the three supplied files. |
| Host/controller execution | Not reproducible or sufficiently auditable. |
| Data/code availability | Manuscript promise present, but the claimed verifier and execution package are absent from the supplied material. |
| Generalization boundaries | Strong and appropriately explicit. The manuscript repeatedly disclaims reliability, calibration, independence, population rates, larger-domain invariance, and superiority. |

The decisive distinction is: **the sanitized record independently reconstructs the reported three-row table, but it does not independently support the evidence chain underlying that table.**

## 6. Minimum-sufficient repair tests

1. **Anonymous replay test:** A reviewer runs one documented command in a clean environment and reconstructs both manuscript tables from supplied records.
2. **Prospective-order test:** Each case has an anonymized freeze manifest demonstrably preceding its outcome manifest.
3. **Blind scoring test:** Alignment is recomputed from frozen decisions, predeclared branches, and later observations without reading stored alignment booleans.
4. **Case 1 test:** Domain, predicate, and complementary closure are explicitly defined and reproduced.
5. **Case 2 test:** All 53 rows and both optimization values are regenerated, with zero unrestricted improvements recovered.
6. **Case 3 test:** Enumeration independently recovers 729 one-object cases, 38,760 quotient two-object cases, 39,489 total cases, zero mismatches, zero one-object positives, and one two-object positive.
7. **Instrument test:** The typed controller deterministically reproduces all decisions; the host configuration and frozen outputs are auditable.
8. **Candidate-flow test:** Every candidate in the declared study window is accounted for, including the two contaminated candidates and the stopping point.
9. **Availability test:** The archive carries a version/hash, licences, dependencies, instructions, and an unambiguous final-deposit commitment.
10. **Build test:** The manuscript compiles on a case-sensitive clean system after resolving the bibliography filename mismatch.
11. **Anonymization test:** The built PDF, source archive, manifests, code comments, paths, and metadata contain no author or internal programme identifiers.
12. **Boundary test:** Automated and manual checks confirm no pooled accuracy, agreement, calibration, reliability, independence, or larger-domain performance claim has been introduced during repair.

## 7. Risk / unsupported claims

### Supported at summary-record level

- The exact three-row agreement/alignment pattern.
- Preservation of both stated contaminated candidates.
- Preservation of both stated unrepaired instrument limitations.
- Internal consistency of the 39,489-case arithmetic.
- Absence of aggregate performance promotion.
- Explicit non-random, non-generalizing, non-independent scope.
- Absence of visible internal programme identifiers in the supplied material.

### Not independently supported by the supplied material

- That each freeze preceded all outcome-bearing evidence.
- That scoring branches were genuinely fixed before outcomes.
- That the three valid rows and two contaminated candidates constitute the complete candidate stream.
- Correctness or completeness of the three scientific computations.
- The repeated-run, brute-force, second-path, or independent-replay claims.
- Availability and operation of the claimed independent verifier.
- The stated licensing and future permanent archive beyond the manuscript’s promise.

Accordingly, the logical argument is well bounded, but the phrase **“direct prospective counterexample”** is only conditionally supported: it becomes convincing once chronology, the predeclared scoring map, and the third-row computation are independently auditable.