# Isolated TMLR Pre-Submission Review

## 1. Assessment boundary

This review is based exclusively on:

- `MANUSCRIPT.tex`
- `REFERENCES.bib`
- `CASE_SERIES.json`

I did not inspect repository history, editorial material, prompts, other reviews, supplementary code, or the cited papers themselves. Consequently, I assess whether the submitted text and JSON support the manuscript’s claims; I do not independently validate the cited literature or underlying quantum-compilation results.

The criteria applied are claim–evidence fit, methodological clarity and reproducibility, accurate literature positioning, explicit limitations, and potential interest to a segment of the machine-learning community. “Blocking” below means blocking a claims-and-evidence-ready submission in its current form, not a prediction of an editor’s decision.

## 2. Summary of contribution

The paper presents a prospective measurement contract for research decisions made before resolving scientific evidence exists. A tool-capable language-model host and a typed deterministic controller receive a frozen evidence state and separately choose:

1. a responsibility diagnosis; and
2. a next discriminating experiment.

Their relation is recorded before the later scientific analysis, after which diagnosis and experiment selection are scored separately. Contaminated questions and invalid instrument outcomes are retained rather than repaired or silently removed.

The contract is illustrated on three non-random questions from one quantum-compilation programme. Both instruments agree in all three. In the third case, a finite census of 39,489 cases yields zero predicate–label mismatches, so the predeclared scoring map marks both diagnoses as misaligned while retaining both census choices as aligned. This is offered as a bounded illustration that agreement does not itself validate a diagnosis.

The manuscript expressly disclaims reliability, calibration, independence, population-frequency, benchmark-performance, and generalization conclusions.

## 3. Major Concerns

### TMLR-PE-001 — The supplied evidence does not establish the prospective chronology

- **Severity:** Major  
- **Blocking:** Yes
- **Target criterion:** Claim–evidence fit; reproducibility
- **Claim pointer:** Abstract; “Prospective measurement contract”; Figure 1; “Reproducibility, data and code availability”
- **Evidence pointer:** `CASE_SERIES.json → valid_questions[*].prospective_freeze_verified`; the file contains Boolean assertions but no frozen records, timestamps, hashes, scoring maps, or verifier
- **Concern:** The central claims require the questions, evidence, vocabularies, controller rules, decisions, and scoring branches to have been fixed before the outcomes. The supplied JSON restates that this happened but does not demonstrate it. Likewise, it cannot establish that later science was generated outside both instruments or that the table can be independently reconstructed.
- **Why it matters:** Precommitment is the essential distinction between this contribution and retrospective case annotation. Without auditable chronology, the agreement-with-misdiagnosis example could be reproduced by post-outcome classification and would no longer support the claimed prospective method.
- **Resolution test:** A blinded reader should be able to verify immutable pre-outcome identities for every question packet, vocabulary, controller rule set, scoring map, and instrument output; establish their order relative to the outcome; and mechanically reproduce the three-row table from the deposited artifacts. Identity-sensitive material can remain blinded if stable hashes and sufficient custody metadata are provided.

### TMLR-PE-002 — “Alignment” and the deferred scoring maps are insufficiently operationalized

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Technical clarity; falsifiability; reproducibility
- **Claim pointer:** “Separate scored coordinates”; “Deferred scoring”; the three case descriptions; Tables 1–2
- **Evidence pointer:** `CASE_SERIES.json → deferred_alignment`, which supplies final Booleans but not the branches that generated them
- **Concern:** The exact diagnosis vocabulary, experiment vocabulary, exhaustive outcome branches, and definitions of aligned, misaligned, unresolved, and invalid are absent. This is especially consequential for:
  - the first case, where successful regime characterization is used to support a “responsibility” diagnosis;
  - the second case, where “certificate silence with sharpness open” may remain true under many possible panel outcomes; and
  - experiment alignment, whose normative criterion is not specified beyond the experiment proving productive.
- **Why it matters:** Readers cannot determine whether each diagnosis could genuinely have failed under the frozen map, whether experiment alignment was decided independently of outcome utility, or whether the mappings were permissive or hindsight-sensitive.
- **Resolution test:** Provide the exact per-case frozen map with mutually exclusive outcome branches and the score assigned to every branch. A simple implementation should derive all six fields in Table 2 from the frozen maps and raw outcomes without manual interpretation.

### TMLR-PE-003 — The construction and isolation of the two instruments remain unclear

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Validity of the evaluated setup; methodological transparency
- **Claim pointer:** “The two instruments”; Figure 1; “Agreement is a relation, not authority”
- **Evidence pointer:** The manuscript acknowledges shared evidence, ontology, research history, and human-authored controller rules; neither supplied data file records construction order or information access
- **Concern:** The paper appropriately denies statistical and causal independence, but it does not state whether the controller rules were fixed before the host output, whether their designers saw that output, or what human intervention occurred on either path. If a question-specific controller was authored after observing the host decision, the reported agreement could be engineered rather than independently produced by heterogeneous machinery.
- **Why it matters:** This would not invalidate the logical statement that agreement is not truth, but it would substantially reduce the empirical content and TMLR relevance of calling the setup “dual-instrument.”
- **Resolution test:** Report the full construction and execution chronology, human touchpoints, host configuration, typed observations, controller rules, and information barriers. Demonstrate that the controller decision was produced without access to the host decision or later outcome. If that separation did not occur, rename the setup as two execution paths of a shared authored system and narrow the interpretation accordingly.

### TMLR-POS-001 — The surviving originality is asserted but not differentiated element by element

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Literature positioning; originality boundary
- **Claim pointer:** “Related evaluation settings and the surviving scope”; the threefold contribution statement
- **Evidence pointer:** `REFERENCES.bib` contains five scientific-agent benchmarks and three works covering delayed outcomes, automated judges, and agreement metrics
- **Concern:** The manuscript commendably cedes several broad areas, but it does not show which elements of the residual bundle are already present in adjacent work: prospective or prequential evaluation, preregistered deferred scoring, evaluation of information-acquisition decisions, value-of-information or experiment selection, consensus/inter-rater methodology, contamination handling, and fail-closed benchmark design. The uncited statement that coordinate separation is compatible with decision-theoretic views highlights this gap.
- **Why it matters:** The reader can understand the proposed combination but cannot determine whether its originality lies in a new method, a synthesis of established safeguards, or merely this particular case-series execution.
- **Resolution test:** Add a verified literature search and an element-by-element comparison table. State the contribution without a “first” claim—for example, as an instantiated combination of identified components—and specify which components, if any, are methodologically new. Cite or remove the decision-theoretic positioning sentence.

### TMLR-POS-002 — TMLR-level utility is plausible but not yet demonstrated by the supplied packet

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Interest to a segment of the machine-learning community; article positioning
- **Claim pointer:** “Implication for research-agent evaluation”; Conclusion; “The protocol is useful”
- **Evidence pointer:** Three non-random questions from one programme; a custom controller for each question; no human or agent baseline; untriggered failure modes; no supplied executable protocol artifact
- **Concern:** The surviving contribution is understandable, and the small sample does not invalidate either feasibility or the bounded logical example. However, the manuscript currently reads partly as an internal protocol audit. The general lesson that consensus does not entail correctness is already logically available; the article’s additional value must therefore come from a reusable prospective evaluation mechanism, not merely the existence of one counterexample.
- **Why it matters:** TMLR interest does not require population-scale benchmarking, but readers should receive a transferable evaluation object or design insight.
- **Resolution test:** Package the schemas, generic scoring logic, contamination states, and verifier as a reusable method, and show that an uninvolved reader can instantiate or replay it from the paper. Explicitly position the article as an evaluation-method case study rather than a benchmark or reliability study. A larger case series is not the minimum necessary repair if reuse and chronology can be established.

## 4. Minor Comments

### TMLR-MIN-001 — Bibliography filename capitalization

- **Severity:** Minor
- **Blocking:** Yes
- **Target criterion:** Build reproducibility
- **Claim pointer:** `\bibliography{references}` at the end of `MANUSCRIPT.tex`
- **Evidence pointer:** The supplied file is named `REFERENCES.bib`
- **Concern:** This can fail on case-sensitive submission/build systems.
- **Why it matters:** A locally successful build on a case-insensitive filesystem may not transfer to the review environment.
- **Resolution test:** Make the filename and LaTeX reference match exactly, then build from a clean case-sensitive environment.

### TMLR-MIN-002 — The opening generalization is broader than the supplied positioning supports

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Claim precision
- **Claim pointer:** “Research-agent evaluations usually assume that a correct answer or reward is available when an agent acts”
- **Evidence pointer:** The five benchmark citations described in the Introduction and Related Work
- **Concern:** “Usually” generalizes beyond the cited benchmark subset, while the manuscript later acknowledges delayed-outcome evaluation work.
- **Why it matters:** The opening can create an avoidable strawman and obscure the genuinely narrow residual contribution.
- **Resolution test:** Use “many benchmark-style evaluations” or explicitly delimit the class being contrasted.

### TMLR-MIN-003 — “Independent” should distinguish implementation replay from external validation

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Claim clarity
- **Claim pointer:** “independent brute-force path,” “independently replayed,” and “independent verifier”
- **Evidence pointer:** The limitations state that outcomes remain internal to the same research programme
- **Concern:** These phrases may be read as external scientific validation, although the text appears to mean separate implementations or replay paths.
- **Why it matters:** The paper otherwise carefully distinguishes internal exactness from field-wide authority.
- **Resolution test:** Use “second implementation path,” “deterministic replay,” or similarly precise language unless genuinely external validation occurred.

## 5. Literature and positioning assessment

### Areas appropriately ceded

The manuscript explicitly and appropriately cedes:

- **Broad scientific-agent benchmarking:** It states that the three cases are not a benchmark suite and do not compare agent performance.
- **Delayed-outcome agreement gating:** It credits `chang2026valueblindbench` with studying agreement-gated evaluation before outcomes become observable.
- **Automated-judge validation:** It credits `wang2026reflect` and does not present the host or agreement relation as a validated judge.
- **Agreement-metric methodology:** It credits `rao2026agreementmetrics`, declines to compute an agreement rate, and treats invalid outputs and abstentions as estimand-relevant.
- **Generalization and reliability:** These are repeatedly and clearly disclaimed.

There are no “first,” priority, or broad superiority claims. The originality language is mostly disciplined.

### Surviving position

The defensible surviving contribution is:

> A prospectively frozen, two-coordinate case-study protocol that records instrument relation separately from later diagnostic and experiment-selection alignment, retains contamination and invalidity, and includes one bounded agreement-with-misdiagnosis example.

This is understandable. It could be useful to researchers designing evaluations for agents acting before ground truth exists. The three-question, single-programme scope is not inherently fatal because the paper does not estimate a rate: one properly precommitted case can establish executability, and one valid counterexample can disprove a universal implication.

The unresolved issue is whether this is a new measurement method, a reusable synthesis of established methods, or a careful internal case report. An explicit comparison against the cited and adjacent methodological literature is needed to settle that positioning without resorting to a “first” claim.

## 6. Minimum-sufficient repair tests

Before submission, the following pass/fail tests would be sufficient without requiring a population-scale expansion:

1. **Prospective-custody test:** Every input, vocabulary, rule set, map, and decision has a verifiable pre-outcome identity and ordering.
2. **Mechanical scoring test:** A clean implementation derives Table 2 solely from frozen maps and later raw observations.
3. **Instrument-isolation test:** The record establishes what humans and each instrument could see at every stage.
4. **Case-selection test:** The sampling frame, replacement rule, contamination trigger, and reasons for stopping at three valid cases are explicit.
5. **Scientific replay test:** The 53-row panel and 39,489-case census can be regenerated, including domain definitions, quotienting logic, labels, and cross-checks.
6. **Positioning test:** A comparison table identifies precisely what is ceded and what the manuscript adds relative to verified prior work.
7. **Claim-language test:** “Useful,” “counterexample,” “exhaustive,” “independent,” and “heterogeneous” are restricted to their demonstrated meanings.
8. **Clean-build test:** LaTeX and bibliography compile without local filesystem assumptions.

## 7. Risk / unsupported claims

| Risk | Assessment from supplied material |
|---|---|
| Prospective freeze and predeclared maps | **High:** asserted, not auditable from the supplied files |
| Later evidence generated outside both instruments | **High:** stated, but construction and access chronology are absent |
| Independent reconstruction from the supplement | **High:** the supplied JSON is a conclusion ledger, not a reconstruction package |
| “Exhaustive” 39,489-case census | **Medium–High:** count is internally consistent, but domain generation and quotient completeness are not supplied |
| First-case exact characterization and complementary closure | **Medium–High:** described narratively and only generically represented in JSON |
| Experiment-selection alignment | **Medium–High:** scoring criterion and counterfactual branches are absent |
| Heterogeneous instruments | **Medium:** carefully limited to decision machinery, but insufficiently operationalized |
| Protocol usefulness beyond the programme | **Medium:** plausible but not demonstrated; “may be useful” would be safer |
| Direct counterexample to agreement as validation | **Conditional:** logically sound if the universal implication and predeclared scoring are formalized and the prospective record is verified; otherwise it is a bounded illustration |
| Reliability, calibration, independence, population rates, or generalization | **Low:** these interpretations are repeatedly and appropriately disclaimed |
| Broad benchmarking, automated-judge validation, delayed-outcome gating, or agreement-metric originality | **Low:** the manuscript explicitly cedes these areas |