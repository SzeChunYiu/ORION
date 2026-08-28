# ORION-14 Wave-1 atomic claim ledger — 2026-08-28

Pipeline: `academic-paper-skills/academic-paper-pipeline`  
Manuscript family: current Wave-1 TMLR revision on PR #1610  
Purpose: manuscript-facing verification at atomic scientific-content granularity.  
This ledger is **not** external peer review. A separate independent coverage pass is required before the paper can reach a simulated publication-ready terminal.

## Status vocabulary

- `SUPPORTED_PROOF` — established by a checked mathematical argument with stated scope.
- `SUPPORTED_BOUND_ARTIFACT` — established by a frozen/bound result artifact inside the stated finite design.
- `SUPPORTED_PRIMARY_SOURCE` — literature proposition entailed by the checked primary source.
- `SUPPORTED_BOUNDARY` — an explicit non-claim/limitation supported by the evidence boundary.
- `RETAINED_NEGATIVE` — a preregistered/adverse result remains visible and is not promoted.
- `NOT_RESULT_BEARING` — definition/design/prospective material not used as scientific result.
- `BLOCKED_PACKAGE` — filing statement depends on an artifact not yet materialized/bound.
- `BLOCKED_AUTHOR_FACT` — factual author/compliance information cannot be supplied by the pipeline.
- `RELEASE_PLACEHOLDER` — manuscript/template placeholder must be resolved before filing.

A final release may contain only supported/released scientific assertions. Blocked/package/placeholder rows must be resolved or removed before `simulated_publication_ready_for_target`.

## A. Title, abstract and submission surface

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| A01 | Verification-axis interpretation depends on identifiability, terminal attainability and discrimination. | Section 2a theory + V2/V3 diagnostics | SUPPORTED_PROOF | keep |
| A02 | Fibrewise Bayes risk is used to formalize exact-terminal attainability. | Eq. bayes-axis-risk | SUPPORTED_PROOF | keep |
| A03 | A donor-factorization boundary is proved for target scientific-promotion terminals. | Cor. 1 | SUPPORTED_PROOF | keep bounded wording |
| A04 | A terminal-adapter/data-processing criterion is proved for comparator outputs. | Cor. 2 | SUPPORTED_PROOF | keep exact assumptions |
| A05 | A total-variation bound is proved for claim-level indistinguishability. | Prop. 2 | SUPPORTED_PROOF | keep equal-prior/common-space assumptions |
| A06 | V2: governed pipeline has 0/360 false promotions. | protected V2 metrics | SUPPORTED_BOUND_ARTIFACT | finite battery only |
| A07 | V2: strongest frozen mechanism proxy has 180/360 false promotions. | protected V2 metrics | SUPPORTED_BOUND_ARTIFACT | mechanism proxy, not external software |
| A08 | V2: both governed pipeline and strongest comparator promote 60/60 clean positives. | protected V2 metrics | SUPPORTED_BOUND_ARTIFACT | clean controls are intentionally easy |
| A09 | V2 registered H3 is saturated and remains a negative measurement result. | V2 H3 artifact + construction audit | RETAINED_NEGATIVE | must remain visible |
| A10 | V3: governed pipeline selects undetermined on 30/30 eligible exact-axis cases. | protected V3 panel | SUPPORTED_BOUND_ARTIFACT | distinct battery |
| A11 | V3: H1-selected strongest comparator selects undetermined on 0/30. | protected V3 panel | SUPPORTED_BOUND_ARTIFACT | interface-attainability interpretation |
| A12 | V3: escalation-capable comparator selects undetermined on 15/30. | protected V3 panel | SUPPORTED_BOUND_ARTIFACT | preserve 0.5 margin |
| A13 | V3 measures terminal/interface expressiveness, not general scientific judgement. | Cor. 2 + panel alphabets | SUPPORTED_BOUNDARY | mandatory boundary |
| A14 | P4-X: target-bound relation scores 400/400 exact contracts. | P4-X protected terminal | SUPPORTED_BOUND_ARTIFACT | exact contracts only |
| A15 | P4-X: donor-complete generic product scores 250/400. | P4-X protected terminal | SUPPORTED_BOUND_ARTIFACT | registered B1 |
| A16 | P4-X: compensatory product scores 50/400. | P4-X protected terminal | SUPPORTED_BOUND_ARTIFACT | registered B2 |
| A17 | P4-X: information-equivalent typed product scores 400/400. | P4-X protected terminal | SUPPORTED_BOUND_ARTIFACT | defeats centralization/unique-expressivity claim |
| A18 | P4-X minus B1 equals +0.375 with domain-stratified 95% bootstrap interval [0.3275,0.4225]. | P4-X protected terminal | SUPPORTED_BOUND_ARTIFACT | finite registered panel |
| A19 | Present results do not establish naturalistic or deployed-system superiority. | evidence boundary | SUPPORTED_BOUNDARY | keep |
| A20 | manuscript is anonymous at author-name surface. | current main.tex | SUPPORTED_BOUNDARY | recheck PDF metadata |
| A21 | first-page LLM-assistance disclosure is factually correct. | author attestation required | BLOCKED_AUTHOR_FACT | do not invent |
| A22 | `MM`, `YYYY`, `XXXX` template fields are filing-correct. | current main.tex | RELEASE_PLACEHOLDER | resolve from official template |

## B. Formal claims and definitions

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| T01 | For finite benchmark distributions, minimum exact-terminal error equals `1-E_D max_t P(Y=t|D)`. | Eq. 1 proof | SUPPORTED_PROOF | finite distribution |
| T02 | Zero exact-terminal error exists iff every positive-probability D-fibre is target-pure and target is in allowed alphabet. | Prop. 1 | SUPPORTED_PROOF | almost-sure only |
| T03 | Prop. 1 does not certify null fibres. | Prop. 1 statement | SUPPORTED_BOUNDARY | keep |
| T04 | Pointwise donor equivalence on a declared world class requires target constancy on every donor-state fibre plus terminal availability. | Cor. 1 | SUPPORTED_PROOF | pointwise scope |
| T05 | Distributional zero error requires the same condition only on positive-probability fibres. | Cor. 1 + Prop. 1 | SUPPORTED_PROOF | keep pointwise/distributional distinction |
| T06 | Mixed donor fibres impose the displayed Bayes lower bound. | Cor. 1 | SUPPORTED_PROOF | finite benchmark |
| T07 | Fibrewise Bayes rule attains that finite-benchmark lower bound. | Cor. 1 proof | SUPPORTED_PROOF | keep |
| T08 | A separate module has no inherent advantage once a donor product is target-sufficient and has the same decision relation. | Cor. 1 consequence | SUPPORTED_PROOF | no centralization claim |
| T09 | Comparator adapter is a prospectively declared measurable map from native output to target alphabet. | Cor. 2 definition | NOT_RESULT_BEARING | keep definition |
| T10 | If comparator output adds no world information beyond visible record, adapted risk cannot beat the visible-record Bayes risk. | Cor. 2 data processing | SUPPORTED_PROOF | Markov/setup assumptions explicit |
| T11 | Zero-error native-output adaptation requires target-pure positive-probability output fibres and available target terminals. | Cor. 2 | SUPPORTED_PROOF | distributional scope |
| T12 | A binary native alphabet cannot attain a three-terminal endpoint when all three terminals occur. | Cor. 2 | SUPPORTED_PROOF | keep |
| T13 | A semantically different block/parse/free-text output cannot simply be renamed CannotCheck unless the predeclared map satisfies fibre purity. | Cor. 2 | SUPPORTED_PROOF | keep |
| T14 | Under equal priors, claim adjudication error is at least `(1-TV(P0,P1))/2`, with equality. | Prop. 2 | SUPPORTED_PROOF | common measurable record space |
| T15 | Identical observable laws make the binary competence claim unidentifiable with error 1/2. | Prop. 2 | SUPPORTED_PROOF | keep |
| T16 | Nuisance-only Bayes advantage is defined by the displayed expression. | nuisance definition | NOT_RESULT_BEARING | keep |
| T17 | A finite nuisance probe register cannot prove absence of every possible shortcut decoder. | logical boundary | SUPPORTED_BOUNDARY | keep |
| T18 | Panel resolution rho=0 supplies no comparative ordering on that axis. | resolution definition | SUPPORTED_PROOF | does not imply competence equality |
| T19 | Nonzero score resolution plus mismatched terminal alphabets first supports interface expressiveness, not finer judgement. | Cor. 2 + definition | SUPPORTED_PROOF | keep |
| T20 | Broad axis interpretation requires intersection of semantic attainability, nuisance resistance, terminal attainability and nonzero resolution. | formal synthesis | SUPPORTED_PROOF | bounded conceptual theorem/synthesis |

## C. Authority mechanism and methods

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| M01 | Authority decisions are Promote / Block / Undetermined rather than binary. | mechanism definition | NOT_RESULT_BEARING | keep |
| M02 | Failed prerequisite blocks; unresolved prerequisite leaves decision undetermined. | mechanism definition | NOT_RESULT_BEARING | keep |
| M03 | Promotion is non-compensatory over the nine required gates. | mechanism definition / frozen implementation | SUPPORTED_BOUND_ARTIFACT | exact implementation scope |
| M04 | Content binding is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M05 | Source/owner binding is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M06 | Claim support is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M07 | Checker-lineage independence is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M08 | Hostile-checker discrimination is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M09 | Behavioral influence is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M10 | Evaluator integrity is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M11 | Holdout/access integrity is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M12 | Search-contamination integrity is one required gate. | mechanism definition | NOT_RESULT_BEARING | keep |
| M13 | Public-seed preflight exercised 42 hostile tests plus 420-case pipeline with panel, ablations, repeats, protected scoring and separate reproducer before final hidden split. | frozen protocol/execution record | SUPPORTED_BOUND_ARTIFACT | current workflow must keep source binding |
| M14 | Final V2 split contains 420 cases: 60 clean + 12 hostile/insufficient families of 30 each. | protected split/metrics | SUPPORTED_BOUND_ARTIFACT | keep |
| M15 | Candidate/comparator see only opaque ID + visible packet, not attack family/protected gold/custody/expected terminal. | frozen bindings / host checks | SUPPORTED_BOUND_ARTIFACT | custody design |
| M16 | Five deterministic repeats are retained with file/network tracing. | execution record | SUPPORTED_BOUND_ARTIFACT | not external custody |
| M17 | Protected evaluator becomes gold-eligible only after candidate/comparator completion and checks telemetry first. | execution/custody record | SUPPORTED_BOUND_ARTIFACT | keep |
| M18 | Evaluator and reproducer are distinct code paths but within one project. | reproduction record | SUPPORTED_BOUNDARY | never call external replication |
| M19 | Comparator labels denote protocol-matched reimplementations, not original external systems. | baseline configs | SUPPORTED_BOUNDARY | mandatory |
| M20 | H1 margin is absolute false-promotion improvement >0.05 against strongest frozen comparator. | preregistered SAP | SUPPORTED_BOUND_ARTIFACT | keep |
| M21 | H2 margin is clean-coverage noninferiority within 0.05. | SAP | SUPPORTED_BOUND_ARTIFACT | keep |
| M22 | H3 tests correct selection of undetermined terminal on eligible cases. | SAP | SUPPORTED_BOUND_ARTIFACT | V2 result negative |
| M23 | Rate intervals use Wilson 95%; paired effects use fixed-seed percentile bootstrap. | SAP / result generator | SUPPORTED_BOUND_ARTIFACT | verify exact implementation in independent coverage pass |
| M24 | Eligible denominators retain false promotions/blocks/abstentions/failures/clean FNs. | SAP / evaluator | SUPPORTED_BOUND_ARTIFACT | keep |

## D. V2 protected results

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| V201 | typed authority panel passed with no blockers. | V2 result attestation | SUPPORTED_BOUND_ARTIFACT | bounded run |
| V202 | separate local reproducer matches headline counts. | independent_reproduce_v2 | SUPPORTED_BOUND_ARTIFACT | local code-path only |
| V203 | governed pipeline false promotions 0/360. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | keep |
| V204 | strongest frozen comparator false promotions 180/360 = 50%. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | keep |
| V205 | paired difference = -0.50, 95% CI [-0.553,-0.447]. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | finite panel |
| V206 | H1 passes predeclared -0.05 practical margin. | SAP + V2 metrics | SUPPORTED_BOUND_ARTIFACT | keep |
| V207 | both governed and strongest comparator promote 60/60 clean positives. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | keep |
| V208 | clean-coverage difference and paired CI are 0. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | saturated coordinate |
| V209 | H2 passes noninferiority margin. | SAP + V2 metrics | SUPPORTED_BOUND_ARTIFACT | does not establish difficult-case recall |
| V210 | all eleven primary systems are at 1.0 clean coverage. | V2 panel | SUPPORTED_BOUND_ARTIFACT | saturated axis |
| V211 | all eleven systems score 30/30 on original insufficient-evidence H3 family. | V2 panel | RETAINED_NEGATIVE | keep |
| V212 | original H3 construction exposes an empty evidence list only on that family. | construction audit | SUPPORTED_BOUND_ARTIFACT | explains saturation |
| V213 | empty-list rule classifies all 420 original cases correctly. | construction audit | SUPPORTED_BOUND_ARTIFACT | shortcut finding, not scientific competence |
| V214 | V2 H3 supplies no comparative result. | V211-V213 + rho=0 | RETAINED_NEGATIVE | keep |
| V215 | no governed false promotions occur in any hostile family. | V2 family contrast | SUPPORTED_BOUND_ARTIFACT | finite taxonomy |
| V216 | strongest comparator false-promotes all 30 in six named governance/checker families and is correct on the other named families. | V2 family contrast | SUPPORTED_BOUND_ARTIFACT | mechanism proxy only |
| V217 | every registered ablation preserves 60/60 clean coverage and increases false promotion. | V2 ablation table | SUPPORTED_BOUND_ARTIFACT | finite battery |
| V218 | removing five single gates yields 30/360 false promotions each. | V2 ablation table | SUPPORTED_BOUND_ARTIFACT | keep exact gate list in table |
| V219 | source/provenance collapse yields 60/360. | V2 ablation table | SUPPORTED_BOUND_ARTIFACT | keep |
| V220 | removing evaluator protection/telemetry yields 90/360. | V2 ablation table | SUPPORTED_BOUND_ARTIFACT | keep |
| V221 | 6-of-9 soft threshold yields 330/360. | V2 ablation table | SUPPORTED_BOUND_ARTIFACT | keep |
| V222 | mean deterministic gate latency is about 2.97 ms/case and proxy mechanisms are microsecond-scale in this synthetic harness. | V2 metrics | SUPPORTED_BOUND_ARTIFACT | not serving benchmark |
| V223 | scored-process telemetry records zero protected-ID hits and zero external-IP connections. | result attestation | SUPPORTED_BOUND_ARTIFACT | raw traces protected |
| V224 | earlier 39-case live-model arm has inconsistent labels/terminals, wrong denominators and hidden-family leakage. | LIVE_ARM_STATUS | SUPPORTED_BOUND_ARTIFACT | adverse diagnostic |
| V225 | 39-case arm is excluded from publication authorization and not pooled/tuned into V2. | evidence boundary | RETAINED_NEGATIVE | mandatory |

## E. V3 exact-axis results

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| V301 | first repair removed empty list but retained length and label-language shortcuts. | V3 construction history | SUPPORTED_BOUND_ARTIFACT | no panel result promoted |
| V302 | five of fourteen judgement-free probes achieve informedness 1.0 on first repair. | identifiability audit | SUPPORTED_BOUND_ARTIFACT | adverse diagnostic |
| V303 | second repair is shape-identical across cases in registered structural quantities. | V3 freeze/construction | SUPPORTED_BOUND_ARTIFACT | exact registered class |
| V304 | undetermined cases are split into two shape-identical subtypes and overlap support-pattern features with blocking cases. | V3 freeze | SUPPORTED_BOUND_ARTIFACT | keep |
| V305 | fourteen frozen nuisance probes have informedness 0.0 on protected axis across 13 registered seeds. | IDENTIFIABILITY_V3 | SUPPORTED_BOUND_ARTIFACT | finite probe class only |
| V306 | nuisance result does not prove absence of all possible shortcuts. | formal boundary | SUPPORTED_BOUNDARY | keep |
| V307 | governed pipeline selects undetermined 30/30. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | keep |
| V308 | H1-selected strongest comparator selects undetermined 0/30. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | keep |
| V309 | paired difference vs H1 comparator is 1.0, CI [1.0,1.0]. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | finite panel |
| V310 | escalation-capable comparator selects undetermined 15/30. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | keep |
| V311 | margin vs escalation-capable comparator is 0.5. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | keep |
| V312 | nine of ten comparator mechanisms cannot emit undetermined terminal in the relevant interface. | panel/interface audit | SUPPORTED_BOUND_ARTIFACT | core interpretation boundary |
| V313 | all eleven systems retain 1.0 clean coverage on V3. | PANEL_V3 | SUPPORTED_BOUND_ARTIFACT | H2 still saturated |
| V314 | V3 cannot relabel or rescue the V2 H3 null because it is a different battery. | evidence identity | SUPPORTED_BOUNDARY | mandatory |

## F. P4-X donor-complete result

| ID | Atomic assertion | Authority | Status | Release note |
|---|---|---|---|---|
| X01 | P4-X uses 400 protected exact identities across 5 domains x 8 archetypes x 10 variants. | frozen P4-X protocol/terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X02 | P4-X scores 400/400. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | exact contracts |
| X03 | donor-complete generic B1 scores 250/400. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X04 | compensatory B2 scores 50/400. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X05 | ideal typed B3 scores 400/400. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X06 | P4-X minus B1 = +0.375. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X07 | domain-stratified bootstrap 95% CI is [0.3275,0.4225]. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | keep |
| X08 | McNemar discordance is 150-0. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | if retained in manuscript/support |
| X09 | P4-X has zero false promotions and clean promotion 1.0. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | finite contracts |
| X10 | exact direction is positive in every registered domain. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | finite domains |
| X11 | independent implementation reproduces canonical row digest and all arm counts without importing main executor. | final P4-X terminal | SUPPORTED_BOUND_ARTIFACT | local independent implementation |
| X12 | B3 tie means no inherent expressivity or centralization advantage is authorized. | Cor.1 + final terminal | SUPPORTED_BOUNDARY | mandatory |
| X13 | P4-X does not authorize generic provenance/verification/authorization novelty. | novelty subtraction | SUPPORTED_BOUNDARY | mandatory |
| X14 | P4-X does not authorize deployed/provider/general universal scientific-authority superiority. | final terminal | SUPPORTED_BOUNDARY | mandatory |

## G. Literature-facing assertions

Each row below is backed by `editorial/LITERATURE_ENTAILMENT_AND_NOVELTY_AUDIT_2026-08-28.md` and current primary records.

| ID | Atomic assertion | Status |
|---|---|---|
| L01 | attribution evaluation is established as a separate measurement problem | SUPPORTED_PRIMARY_SOURCE |
| L02 | source-aware factuality explicitly targets cross-source conflation | SUPPORTED_PRIMARY_SOURCE |
| L03 | scientific claim-evidence reasoning and scientific claim-source retrieval are existing benchmark/retrieval problems | SUPPORTED_PRIMARY_SOURCE |
| L04 | relevant evidence can differ from evidence authorized to determine an agent action | SUPPORTED_PRIMARY_SOURCE |
| L05 | authorization-limited evidence can produce unsafe completeness despite correct access filtering | SUPPORTED_PRIMARY_SOURCE |
| L06 | structural/formal/cryptographic agent authorization and permission-graph machinery already exist | SUPPORTED_PRIMARY_SOURCE |
| L07 | claim-level auditability, citation fidelity and behavioral influence are distinct existing evaluation/design concepts | SUPPORTED_PRIMARY_SOURCE |
| L08 | research-integrity provenance and declared-vs-actual agent-skill integrity are existing work | SUPPORTED_PRIMARY_SOURCE |
| L09 | iterative verification, evidence escalation and stage-wise fact-checking are existing methods/evaluation designs | SUPPORTED_PRIMARY_SOURCE |
| L10 | evaluator tampering, holdout leakage, search contamination and benchmark defects are established evaluation-integrity concerns | SUPPORTED_PRIMARY_SOURCE |
| L11 | abstention/acknowledgement of inability is an existing agent/scientific-integrity evaluation target | SUPPORTED_PRIMARY_SOURCE |
| L12 | ORION-14 does not claim novelty for the donor concepts in L01-L11. | revised Related Work + boundary | SUPPORTED_BOUNDARY |
| L13 | no exact collision for the residual ORION-14 contribution was located in the bounded 2026 search. | bounded search | SUPPORTED_BOUNDARY |
| L14 | L13 is not a novelty certificate. | search-method boundary | SUPPORTED_BOUNDARY |

## H. Limitations and non-claims

| ID | Atomic assertion | Authority | Status |
|---|---|---|---|
| B01 | theory does not establish that deployed verifiers possess target-sufficient representations | formal scope | SUPPORTED_BOUNDARY |
| B02 | V2/V3 are synthetic mechanical-gold batteries, not natural scientific disputes | dataset identity | SUPPORTED_BOUNDARY |
| B03 | no human-adjudication claim is supported because final cases are mechanically decidable | protocol/results | SUPPORTED_BOUNDARY |
| B04 | P4-X is exact-contract evidence, not a sampled natural-dispute population | P4-X design | SUPPORTED_BOUNDARY |
| B05 | final scoring is deterministic and does not estimate stochastic research-agent error | implementation identity | SUPPORTED_BOUNDARY |
| B06 | comparator results are about matched mechanism reimplementations, not published systems in native environments | baseline identity | SUPPORTED_BOUNDARY |
| B07 | 60/60 clean controls do not estimate difficult benign-case recall | clean-control design | SUPPORTED_BOUNDARY |
| B08 | finite attack taxonomy does not cover adaptive attacks/compromised hosts/unobserved side channels | threat-model boundary | SUPPORTED_BOUNDARY |
| B09 | fourteen-probe nuisance audit is limited to the registered probe class | V3 design | SUPPORTED_BOUNDARY |
| B10 | component mechanisms are prior art; novelty is not claimed for them | literature audit | SUPPORTED_BOUNDARY |
| B11 | naturalistic transfer is unestablished | successor status | SUPPORTED_BOUNDARY |
| B12 | strongest current public source identity bridge is 76/80 in one bounded software-publication frame | prospective transport records | SUPPORTED_BOUND_ARTIFACT |
| B13 | zero natural pairs are authorized; lineage/pair eligibility/source-disjoint replication/external custody/external comparator execution remain unresolved | successor records | SUPPORTED_BOUNDARY |
| B14 | source-feasibility/transport preflights contribute no performance evidence to current paper | evidence identity | SUPPORTED_BOUNDARY |
| B15 | deterministic replay/custody integrity is not independent scientific validation | epistemic boundary | SUPPORTED_BOUNDARY |

## I. Figures, tables and display assertions

| ID | Display assertion | Authority | Status |
|---|---|---|---|
| F01 | Fig. false-promotion panel reflects protected V2 mechanism rates | safe V2 aggregate | SUPPORTED_BOUND_ARTIFACT |
| F02 | Fig. clean-coverage frontier shows all primary mechanisms at 1.0 | safe V2 aggregate | SUPPORTED_BOUND_ARTIFACT |
| F03 | Fig. hostile-family contrast matches family aggregate | FAMILY_CONTRAST_V2 | SUPPORTED_BOUND_ARTIFACT |
| F04 | Fig. attribution/support coordinates do not imply safe authority terminal | safe V2 aggregate + cross-coordinate counts | SUPPORTED_BOUND_ARTIFACT |
| F05 | Fig. latency/false-promotion plot uses deterministic harness latency and log scale | safe V2 aggregate | SUPPORTED_BOUND_ARTIFACT |
| F06 | Table 1 custody counts match the frozen split | split/custody artifact | SUPPORTED_BOUND_ARTIFACT |
| F07 | Table 2 comparator/ablation rates match safe V2 metrics | publication metrics | SUPPORTED_BOUND_ARTIFACT |
| F08 | Table 3 abstention/error counts preserve V2 H3 saturation | publication metrics | RETAINED_NEGATIVE |
| F09 | all display captions identify comparator mechanisms as proxies/reimplementations where needed | current TeX | SUPPORTED_BOUNDARY |

## J. Availability, reproducibility and compliance

| ID | Atomic assertion | Authority | Status | Release action |
|---|---|---|---|---|
| C01 | safe materials can reproduce released aggregates/figures without protected gold | current safe bundle + reproduction path | SUPPORTED_BOUND_ARTIFACT | keep |
| C02 | protected per-case gold/raw traces are intentionally absent from public review bundle | custody design | SUPPORTED_BOUNDARY | keep |
| C03 | separate reproduction path is not external replication | project identity | SUPPORTED_BOUNDARY | keep |
| C04 | anonymous review package contains the enumerated materials | package not yet built | BLOCKED_PACKAGE | materialize + checksum + identity scan |
| C05 | blind PDF does not reveal public repository ownership | revised source | SUPPORTED_BOUNDARY | verify rendered PDF + metadata |
| C06 | blind supplementary ZIP/PDF does not reveal authors | package not yet built | BLOCKED_PACKAGE | identity scan exact archive |
| C07 | public archive/repository identifiers can be restored after unblinding without changing science | package design | SUPPORTED_BOUNDARY | camera-ready action only |
| C08 | no DOI is asserted in blind manuscript | current availability section | SUPPORTED_BOUNDARY | keep unless archive exists |
| C09 | TMLR LLM-use footnote accurately describes actual assistance | author facts | BLOCKED_AUTHOR_FACT | author verifies wording |
| C10 | author/funding/conflict/IRB/OpenReview profile metadata are complete | human filing metadata | BLOCKED_AUTHOR_FACT | supply at filing |
| C11 | final PDF is exact clean build of final source | current revision still changing | BLOCKED_PACKAGE | final workflow + hash |
| C12 | every final PDF page is visually audited | current revision still changing | BLOCKED_PACKAGE | final page audit |

## Cross-section consistency rules

- V2 H3 must be `RETAINED_NEGATIVE` everywhere. V3 cannot relabel it.
- V3 must be described as interface/terminal attainability before judgement competence.
- P4-X B3 tie must remain visible wherever B1 superiority is summarized.
- Comparator names must not imply execution of external authors' software.
- Local independent code paths must not be described as external replication.
- Naturalistic/source-transport work must not enter a current performance denominator or headline.
- No `first`, `novel`, `general`, `universal`, `deployed`, `autonomous superiority`, or centralization claim is authorized unless separately evidenced.

## Current ledger terminal

Scientific manuscript assertions represented above are either supported, explicitly retained negative, or explicit non-claims. The remaining open states are filing/package/compliance states, not hidden scientific positives.

`ATOMIC_LEDGER_PASS1_COMPLETE__INDEPENDENT_COVERAGE_AND_FINAL_PACKAGE_OPEN`
