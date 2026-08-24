# Reviewer 1 isolated pre-submission report

## Review setup

- **Reviewer role:** Reviewer 1. Validity, methods, data, inference, and central technical blockers.
- **Target:** *Nature Machine Intelligence*.
- **Content type and stage:** Article, initial submission.
- **Immutable subject:** commit `8d47c546591a3c96dc5cf202f7e227d13251221c`; tree `6c8e412db4d31c2867fc4e3af9fa417479f79824`.
- **Isolation declaration:** I did not read any other reviewer report, editorial-triage conclusion, concern ledger, synthesis, consensus hint, or author-facing repair plan. This report uses only the five immutable manuscripts, the included manuscript-associated source material, and the common target and workflow criteria.
- **Assessment boundary:** The packet contains the five compiled manuscripts and selected manuscript source, figures, tables, and referenced P4 submission text. It does not contain the central repository evidence archives named by repository-relative path in the manuscripts. I can therefore assess the internal claim-evidence logic and reporting, but I cannot independently audit all raw cases, protected labels, result records, code, or custody receipts.
- **Target criteria used:** An NMI Article should present substantial novel research and a complex, well-supported story that is intelligible across disciplines. The current Article limits are 3,500 main-text words excluding the abstract, Methods, references, and figure legends; a 150-word unreferenced abstract; and no more than six combined main figures and tables. At initial submission, supporting data and central custom code must be available to editors and reviewers. Separate Data Availability and Code availability statements are required. The local NMI profile was verified against the official pages on 2026-08-14. Official URLs were reachable on 2026-08-24 but redirected through cookie-error pages.

### Immutable PDF identities

| Paper | Pages | PDF SHA-256 |
|---|---:|---|
| P1 | 44 | `fe5e2e87cbae96cc691b92768ebcb719a3837e60cdc3ddb45e483f952e83d806` |
| P2 | 45 | `56a9932edc4d9c048bd7b6889159a34376cdfba9d78cf2460bbedda36bfe0c12` |
| P3 | 44 | `80580a55295c84ca60454eed9cba8de4e58592285db82bb8349746340709134b` |
| P4 | 26 | `fee77d7f7d273e69138b4232719149ca0b31d526f088421c2c13b3a0ab5fd576` |
| P5 | 38 | `5acb6ee64b14f4d8ca32c75308cddc5f9ad1949330a68c1357e867a60ccb604e` |

### Cross-manuscript hard-criterion concern

#### R1-X-M1 [NMI Article format and evaluability]

**Severity** Major  
**Blocking** Yes  
**Target criterion** NMI Article limits and cross-disciplinary evaluability.  
**Claim pointer** Each manuscript presents itself as a complete Article-length research story.  
**Evidence pointer** `FORMAT_AUDIT.json`; the five `main.tex` files and their recursively included TeX sources.  
**Concern** A reproducible TeX preflight gives approximate abstract counts of P1 337, P2 807, P3 858, P4 591, and P5 656 words. Every abstract exceeds the 150-word Article limit. Literal main-document display counts are P1 5, P2 9, P3 1, P4 10, and P5 10. P2, P4, and P5 therefore exceed the six-item main-display budget. Approximate full-document prose counts range from 12,127 to 22,149 words. Those totals include Methods and other material excluded by NMI, so they are not exact main-text counts, but the manuscripts still require an exclusion-aware count and substantial restructuring. The long sequences of development versions, terminals, hashes, preflights, and unexecuted successor plans obscure the primary scientific question and decisive evidence.
**Alternative interpretation** The manuscripts function well as exhaustive internal research records or technical dossiers. That is not the same object as a concise NMI Article.
**Why it matters** This is a hard article-type compliance and evaluability problem. It also makes it difficult for a reader to distinguish a central result from provenance and future-work history.
**Resolution test** For each paper, produce an NMI-structured Article with an abstract of at most 150 words, an exclusion-aware main-text count at or below 3,500 words, no more than six combined main displays, and the sequence Introduction, Results, Discussion, and Methods unless an editor-authorized variant is justified. Move version-by-version diagnostics, checksum inventories, and prospective plans to Methods, Extended Data, Supplementary Information, or a repository. Retain adverse results that change interpretation, but report them as scientific findings rather than as an execution diary.

---

# Paper 1

## Overall assessment

P1 develops a coherent distinction between diagnosis, successful repair, and the scientific layer that evidence licenses changing. The formal interface and fail-closed semantics are clear, and the manuscript is unusually candid about its negative precursor and the exact-contract boundary. The positive evidence nevertheless shows behavior inside authored mechanical worlds whose rules instantiate the proposed licensing relation. It does not yet establish that the relation improves scientific revision decisions under naturalistic ambiguity, noisy responsibility inference, or independent authority. In its current form, the work is not a well-supported NMI Article at the breadth implied by the title and framing.

## Central claim and evidence readout

The central claim is that typed responsibility-to-authority licensing identifies the minimal admissible scientific transition after diagnosis and repair. The primary and disjoint replication each contain 2,882 mechanical worlds, including 480 hidden shifts and 2,402 controls, and report 1.000 protected success for the governed policy. A separate 400-case exact-contract battery reports 400/400 for the licensing relation versus 275/400 for a donor-complete interface that lacks the same coupling. An information-equivalent donor product obtains 400/400. The historical broad precursor is negative. The naturalistic frame has 12,038 rights-valid relations in 11,602 families but no scientific-action gold, eligible dossier, ready comparator, or external custody.

## Major strengths

- Primary and disjoint replication are kept separate rather than pooled.
- The comparator-compromised first exact-contract execution is retained rather than silently repaired.
- The information-equivalent donor tie prevents an unsupported inherent-expressivity or centralization claim.
- The historical broad negative and naturalistic non-readiness are stated directly.

## Major Concerns

### R1-P1-M1 [construct validity of scientific-revision authority]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Substantial novel research with a complex, well-supported story; valid inference from evidence to the central claim.  
**Claim pointer** Typed responsibility licensing supports scientific revision and identifies the justified change layer. See `manuscript/main.tex:40-76` and `manuscript/sections/01-foundations.tex:31-77`.  
**Evidence pointer** Mechanical-world design and results in `manuscript/sections/05b-necessity-successor.tex:20-41,52-108`; exact contracts and comparators in `manuscript/sections/05c-revision-responsibility-successor.tex:13-41,43-89`; naturalistic preflight status in `manuscript/sections/09-reproducibility.tex:118-220`.  
**Concern** The two positive experiments test worlds and exact contracts authored around the load-bearing licensing rules. The donor-complete comparator omits that coupling by design, while an information-equivalent product ties exactly. These are strong conformance and factorization witnesses, but they do not establish naturalistic construct validity, prevalence, or decision benefit. Responsibility and revision gold are mechanical. The wider source frame has not produced scientific-action cases or external adjudication. The historical broad study remains negative and cue-vulnerable.
**Alternative interpretation** P1 establishes an analytic interface and verifies its exact semantics on registered generators. It does not yet establish a general scientific-revision method.
**Why it matters** The NMI Article case depends on a scientific, not merely self-consistent, demonstration that the proposed relation changes justified revision decisions under real ambiguity and without encoding the answer in the contract.
**Resolution test** Either provide a prospectively frozen, source-disjoint naturalistic study with independently authored scientific-action gold, blinded adjudication, noisy responsibility evidence, difficult benign controls, a strong donor-complete comparator with matched information and budget, an information-equivalent control, external result custody, and cluster-level uncertainty; or narrow the title, abstract, claims, and target to formal exact-contract licensing and remove naturalistic or model-general implications.

### R1-P1-M2 [review access and redistribution status]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Supporting data and central code accessible to reviewers; separate Data and Code availability; reproducible central evidence.  
**Claim pointer** The mechanical and exact-contract results are presented as archived, independently replayable evidence.  
**Evidence pointer** Repository-relative inventory in `manuscript/sections/09-reproducibility.tex:1-116`; omitted naturalistic payloads and bounded receipts in `:118-220`; repository access and licensing status in `:222-269`.  
**Concern** The review packet does not contain the raw worlds, protected response matrices, decision rows, verifier inputs, or executable code needed to audit the central results. The manuscript gives repository-relative paths but no review access route or persistent identifier. It explicitly reports no repository-level licence and unresolved redistribution terms. The current combined Data and code section does not satisfy the separate-statement requirement.
**Alternative interpretation** Hashes and internal verification provide valuable integrity evidence, but they do not substitute for reviewer access to the evidence those hashes bind.
**Why it matters** The central results cannot be independently assessed from the supplied initial-submission packet.
**Resolution test** Give editors and reviewers controlled access to the exact commit, raw and protected evidence needed for audit, executable reproduction instructions, dependency lock, manifests, and all restriction procedures. Supply separate Data Availability and Code availability sections, a stable access locator or private review link, and an explicit code/data licence or precise restriction statement. A DOI can remain pending at initial submission if reviewer access is real and complete.

## Minor Comments

### R1-P1-m1 [finite-world versus population language]

**Severity** Minor  
**Target criterion** Clear and non-inflated quantitative reporting.  
**Affected element** Abstract and conclusion language around replication and necessity.  
**Evidence pointer** `manuscript/main.tex:40-76`; `manuscript/sections/05b-necessity-successor.tex:52-108`.  
**Issue** A disjoint draw from the same authored generator is a useful implementation replication, but not source-family or institutionally independent replication.
**Required correction** Use `disjoint generator replication` wherever a reader could infer external replication, and place the population claim ceiling adjacent to the first headline number.

## Blocking technical failings

- `R1-P1-M1`: no naturalistic construct-validity evidence for scientific revision authority.
- `R1-P1-M2`: central data and code are not accessible in the supplied review packet.
- `R1-X-M1`: Article-length and abstract compliance are not met.

## Assessment against NMI criteria

- **Universal validity:** Exact-contract semantics appear internally coherent, but the broad scientific inference is not established.
- **NMI-specific advancement:** Potentially interesting across research-agent and scientific-reasoning communities, but current validation is mechanical rather than a substantial well-supported scientific story.
- **Cross-disciplinary intelligibility:** The central distinction is intelligible; the development chronology and terminal vocabulary overwhelm it.
- **Data/code reviewability:** Not met in the supplied packet.
- **Article format:** Abstract exceeds 150 words. Display count is within six, but main-text compliance requires major compression.

## Recommendation posture

**Reject in present form for NMI Article review.** Reconsideration would require either decisive naturalistic validation or an explicit repositioning as a formal exact-contract paper with substantially narrower claims and a different article/venue strategy.

---

# Paper 2

## Overall assessment

P2 offers a useful conceptual separation among acquisition, route stopping, task closure, unresolved material routes, and authority. It also preserves several adverse external results with uncommon clarity. The evidence does not show that the proposed envelope improves open-world scientific discovery. The controlled positive is synthetic and expressly underpowered, the exact-contract advantage follows from withholding the target unresolved-route relation from B1, the ideal comparator ties, and every substantial public screening successor fails against or falls back to u4. The manuscript is therefore strongest as a theory and failure-localization paper, not as the broad NMI Article currently presented.

## Central claim and evidence readout

The paper claims that an acquisition-authority envelope governs route invention, evidence acquisition, optionality, safety, cost, and scientific closure. The offline controlled index reports recall 0.979487 versus 0.666667 but cannot promote superiority under its frozen plan. The exact 400-contract battery reports 400/400 versus 250/400 when B1 drops unavailable or invalid material routes from the denominator, while B3 ties 400/400. MetaSyn localizes retrieval and screening loss. SWIFT, KIFMS, donor-envelopment, and source-disjoint title-emphasis successors are adverse relative to u4. The matched external open-world campaign remains invalid, unexecuted, or undetermined.

## Major strengths

- The manuscript does not convert failed provider validity into a negative performance result.
- Strong u4 results and failed non-compensatory gates are preserved.
- The ideal comparator tie correctly bounds the factorization claim.
- Route-generation failures are distinguished from downstream screening failures.

## Major Concerns

### R1-P2-M1 [open-world effectiveness is not demonstrated]

**Severity** Major  
**Blocking** Yes  
**Target criterion** A substantial, well-supported Article story; valid inference for the central open-world discovery claim.  
**Claim pointer** The acquisition-authority envelope improves or governs open-world scientific discovery. See `manuscript/main.tex:29-112` and `manuscript/sections/acquisition_authority-envelope.tex`.  
**Evidence pointer** Synthetic and underpowered status in `manuscript/sections/results.tex:4-17,93-106`; external/adverse results in `:19-77,229-247,271-413`; exact unresolved-route construction in `manuscript/sections/p2x_unresolved_route_successor.tex:6-20`; public screening successors in `manuscript/sections/05a-public-screening-transport.tex:96-321`.  
**Concern** The evidence does not show an improvement in real open-world discovery. The offline index is authored, complete-gold, and underpowered for the declared margin. The exact battery grants B1 all local mechanisms but defines it to remove the very unavailable-route relation that determines the target label. B3 ties when it receives the same semantics. The external route campaign is provider-invalid or undetermined. The public screening studies repeatedly lose to the cadence-matched u4 donor or revert to it. These layers identify useful failure boundaries, but they do not jointly become a positive full-system result.
**Alternative interpretation** The manuscript establishes a theory of safe non-closure, an acquisition ceiling, and a record of why several candidate controllers fail to surpass a saturated donor.
**Why it matters** The title and Article framing concern open-world scientific discovery, while the positive authority is synthetic or exact-contract only and the nearest real comparisons are adverse.
**Resolution test** Either execute a prospectively frozen, source-disjoint, matched external campaign that jointly tests acquisition support, decision-relevant discovery, closure error, valid closure yield, harm, and cost under identical provider access and budgets against strong native comparators; or remove the performance/general-discovery implication and present the contribution as a formal closure and failure-localization framework. A positive screening-only result cannot close an acquisition claim.

### R1-P2-M2 [central evidence access and reproducibility boundary]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Review access to supporting data and central code; separate Data and Code availability.  
**Claim pointer** Archived controlled, external, and public-development records support the reported finite results.  
**Evidence pointer** `manuscript/sections/availability.tex:1-63,65-115,117-210,226-278,280-316`.  
**Concern** The availability section lists internal paths, omitted public-source bodies, deleted intermediates, hashes, and several non-redistributed comparator archives, but the review packet contains none of the central result archives or executable code. It does not provide a stable repository locator, private review route, or separate Code availability statement. For multiple result families, row-level labels, source text, rankings, or candidate captures are absent by design. Hash-only retention permits byte identity checks only when the corresponding object remains accessible.
**Alternative interpretation** The paper has a detailed internal provenance map, but provenance metadata alone does not make the scientific result reviewable.
**Why it matters** Reviewers cannot verify the controlled-index construction, exact-contract comparator implementation, or public-result projections from this packet.
**Resolution test** Supply reviewer access to the exact code revision, central synthetic data, result records, comparator configurations, and all legally shareable external projections. For restricted or omitted material, state a precise controlled-access procedure and retain an auditable escrow or repository object, not only its digest. Add separate Data Availability and Code availability headings with persistent or review-only access routes and executable instructions.

## Minor Comments

### R1-P2-m1 [primary estimand hierarchy]

**Severity** Minor  
**Target criterion** Clear, concise Article argument.  
**Affected element** Results chronology and abstract.  
**Evidence pointer** `manuscript/main.tex:29-112`; `manuscript/sections/results.tex:4-77`.  
**Issue** Many sequential V1-V11 studies receive similar narrative weight even though only a few bear on the central estimand.
**Required correction** Lead with one claim-evidence table that marks each layer as theory, synthetic conformance, public development, adverse comparison, or unexecuted. Move version chronology and terminal strings out of the main Article.

## Blocking technical failings

- `R1-P2-M1`: no valid positive open-world discovery comparison.
- `R1-P2-M2`: central evidence and code are not review-accessible from the packet.
- `R1-X-M1`: abstract and main-display limits are exceeded, and the Article requires major compression.

## Assessment against NMI criteria

- **Universal validity:** The adverse boundaries are responsibly reported. The broad positive inference is unsupported.
- **NMI-specific advancement:** The theoretical distinction may interest research-agent and information-retrieval readers, but the Article lacks the decisive external result needed for the broader claim.
- **Cross-disciplinary intelligibility:** The acquisition versus closure distinction is accessible; the extended development ledger is not.
- **Data/code reviewability:** Not met.
- **Article format:** Approximate abstract 807 words and nine main displays exceed NMI limits.

## Recommendation posture

**Reject in present form.** The scientifically credible route is either a new matched external open-world campaign or a much narrower theory/failure-analysis paper that treats u4 saturation and unresolved closure as the result rather than promising controller superiority.

---

# Paper 3

## Overall assessment

P3 has the clearest formal contribution of the set. The epistemic portrait envelope, identified-set view, information-refinement boundary, and authority-composition distinction are coherent and potentially useful. The empirical validation is too narrow for the breadth of the Article. The confirmatory effect is six flat-canonicalization false merges within 13 polarity, modality, attribution, or context cases. All other holdout strata are clean controls. The study begins from already-structured, host-constructed projections, not raw scientific texts or independently annotated cross-domain portraits. Naturalistic validity, downstream utility, provider-native gold, and scientific comparator performance remain absent.

## Central claim and evidence readout

The paper claims that scientific integration should return an envelope of compatible global portraits and separate identification from downstream decision. It reports a disjoint 32-case public-reference holdout with zero false merges under coordinate-governed mapping versus six under flat predicate canonicalization. An exact-coordinate conservative control satisfies the false-split guard. A separate 400-contract battery is exact-contract evidence. A constructed 36-case partial-observation corpus proves a 27/36 ceiling. OAEI development repairs interface coverage but does not obtain harm superiority. Native comparator readiness eventually reaches 3/3 on a synthetic pair, while scientific readiness remains 0/3 because no provider-native reference identity is admitted.

## Major strengths

- The paper separates point identification, partial identification, and decision loss.
- The 36-case indistinguishable-orbit result is correctly presented as a constructed identification bound rather than a natural prevalence estimate.
- Public OAEI failures and the worse-than-AML maximal envelope are retained.
- The information-equivalent tie and authority-composition countermodel prevent promotion of local interface readiness.

## Major Concerns

### R1-P3-M1 [naturalistic construct validity and comparator adequacy]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Substantial, well-supported research story; valid scientific integration claim.  
**Claim pointer** The epistemic portrait envelope provides a general alternative for cross-domain scientific synthesis and a composition at the scientific-identity interface. See `manuscript/sections/00-abstract.tex:2-38` and `manuscript/sections/10-introduction.tex:20-55`.  
**Evidence pointer** Already-structured projections in `manuscript/sections/30-method.tex:27-46,129-148`; dataset construction and absent expert gold in `manuscript/sections/40-dataset.tex:2-26,55-82`; compared rules in `manuscript/sections/50-evaluation.tex:28-49`; result localization and missing endpoints in `manuscript/sections/06-results.tex:1-125,417-506`.  
**Concern** The positive holdout compares an authored coordinate-governed rule with flat predicate canonicalization and an exact-coordinate conservative control over already-structured projections. It does not test raw-text coordinate extraction, independently authored mapping decisions, strong schema-induction or provenance-contract systems, generated-portrait recoverability, or downstream utility. The only discriminating empirical cell is 6/13 false merges in one case family. The broader expert atlas and naturalistic calibration are unexecuted, while public OAEI development does not establish comparator superiority.
**Alternative interpretation** The evidence validates a finite mapping semantics and supplies formal identification examples. It does not validate a general scientific knowledge-integration system.
**Why it matters** The formal theory may be general, but the NMI Article story presents empirical support that does not yet test the central naturalistic construct.
**Resolution test** Execute a source-disjoint expert atlas with independently authored cases, dual annotation and adjudication, raw-text input, provider-native reference authority, strong native integration or matcher comparators, and at least one downstream decision or recoverability endpoint. Preserve an exact-contract control and report failure families. If this study is not feasible, narrow the manuscript to the formal identified-set theory and finite mapping claim, and remove empirical language that suggests end-to-end cross-domain validation.

### R1-P3-M2 [statistical unit and source-general inference]

**Severity** Major  
**Blocking** Yes for any source-general empirical claim  
**Target criterion** Correct uncertainty and generalization.  
**Claim pointer** The prospectively frozen 32-case holdout is described as confirmatory evidence for reduced false merging.  
**Evidence pointer** Holdout selection in `manuscript/sections/40-dataset.tex:17-26`; family composition in `:28-53`; bootstrap and decision rules in `manuscript/sections/50-evaluation.tex:10-26,72-84`; localized result in `manuscript/sections/06-results.tex:34-77`.  
**Concern** The holdout is disjoint by case identifier but is drawn from the same small source pools using the next deterministic window. The paired percentile bootstrap resamples 32 cases as units, even though cases may share source authority, construction template, or stratum. Six discordant cases from one 13-case family drive the entire superiority result. The interval therefore quantifies finite-case resampling, not transport across source families or independently authored scientific domains.
**Alternative interpretation** If the estimand is strictly the frozen 32-case census, descriptive paired counts are valid and sufficient; inferential language should remain finite-set only.
**Why it matters** A case-level confidence interval can look like source-general replication while shared construction and source lineage remain unmodelled.
**Resolution test** Either relabel the result as a finite-holdout descriptive confirmation without population transport, or preregister a source-clustered, source-disjoint study with the source or independently authored case family as the top-level unit, cluster-aware uncertainty, and a worst-domain or replication gate.

### R1-P3-M3 [review access to gold, code, and result archives]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Reviewer access to supporting data and central code; separate availability statements.  
**Claim pointer** Deterministic public-reference scripts and immutable archives make the mapping result reproducible.  
**Evidence pointer** `manuscript/sections/60-availability.tex:1-106,108-289`; stable-release boundary in `manuscript/sections/40-dataset.tex:84-91`.  
**Concern** The packet provides only manuscript source and PDF, not the public-reference gold, source registry, evaluator, execution freeze, analysis, or code. The availability section lists internal paths but no accessible repository URL, private review link, DOI, or independent archive. It also combines Data and code availability rather than providing separate headed statements.
**Alternative interpretation** Extensive path and digest documentation improves internal provenance, but does not provide the review access required to evaluate the central result.
**Why it matters** Neither the 32-case labels nor the reported 6/13 error localization can be independently inspected from the submission packet.
**Resolution test** Provide a stable or private reviewer-access repository containing the exact gold records legally shareable, source locators and restrictions, candidate outputs, evaluator, analysis, and executable environment. Separate Data Availability from Code availability and state the access route for restricted third-party text.

## Minor Comments

### R1-P3-m1 [abstract evidence hierarchy]

**Severity** Minor  
**Target criterion** Concise, intelligible abstract.  
**Affected element** Abstract.  
**Evidence pointer** `manuscript/sections/00-abstract.tex:40-90`.  
**Issue** The abstract devotes more space to V4-V14 runtime preflights than to the central theory and finite confirmatory result.
**Required correction** Retain only the main theoretical object, the 32-case finite result, the partial-observation bound, and the naturalistic claim ceiling. Move runtime repair chronology to Supplementary Information or the repository.

## Blocking technical failings

- `R1-P3-M1`: no naturalistic or end-to-end construct validation.
- `R1-P3-M2`: uncertainty does not support source-general inference.
- `R1-P3-M3`: central gold and code are not review-accessible.
- `R1-X-M1`: abstract and Article length require major restructuring.

## Assessment against NMI criteria

- **Universal validity:** Formal statements appear coherently bounded. Empirical generalization exceeds what the finite source construction can establish unless narrowed.
- **NMI-specific advancement:** The identified-set framing may be interesting, but a well-supported Article requires either stronger naturalistic validation or a more clearly theoretical contribution with priority established elsewhere.
- **Cross-disciplinary intelligibility:** The opening theory is accessible; the V2-V14 execution chronology is not.
- **Data/code reviewability:** Not met.
- **Article format:** Approximate abstract 858 words. Display count is within six, but the manuscript requires drastic compression.

## Recommendation posture

**Reject in present NMI Article form.** P3 may be salvageable as a substantially shorter formal paper with exact finite evidence, or as an NMI Article only after independent naturalistic validation and cluster-level inference.

---

# Paper 4

## Overall assessment

P4 correctly emphasizes that verification axes can be saturated, interface-limited, or non-identifying. Its treatment of the negative H3 construction is a genuine strength. The primary performance contrast is nevertheless generated by a mechanical benchmark whose hostile families instantiate the proposed gate lattice and whose comparator mechanisms omit some gates. P4-X repeats this structure at a higher semantic level: B1 lacks the target scientific-promotion relation, while B3 ties when given it. No naturalistic scientific claim panel or native external comparator has been executed. The protected per-case gold is also unavailable to this reviewer.

## Central claim and evidence readout

The paper claims that a non-compensatory scientific-authority transition prevents false promotion and that scientific promotion remains a distinct relation after donor mechanisms are granted. V2 reports 0/360 false promotions versus 180/360 for the strongest mechanism proxy, with 60/60 clean promotion in both arms. H3 is saturated because an empty evidence list reveals the family. V3 reports 30/30 versus 0/30 or 15/30 on a repaired exact axis, but nine of ten comparators cannot emit CannotCheck. P4-X reports 400/400 versus 250/400 for B1 and 400/400 for information-equivalent B3. The naturalistic 768-cluster study remains prospective, with zero natural pairs and no external comparator execution.

## Major strengths

- The manuscript explicitly refuses to interpret a saturated H3 axis as equality.
- V3 distinguishes terminal expressiveness from epistemic judgement.
- The information-equivalent B3 tie prevents a centralization claim.
- Exploratory live results with label and denominator defects are excluded from authorization.

## Major Concerns

### R1-P4-M1 [benchmark construct validity and comparator fairness]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Valid, substantial, well-supported evidence for scientific verification and promotion.  
**Claim pointer** The non-compensatory authority transition reduces false scientific promotion and scientific promotion is a distinct relation beyond donor verification and authorization. See `manuscript/sections/01-introduction.tex:1-18` and `submission/P4_X_PROMOTION_AUTHORITY_SECTION.tex:1-10,24-36`.  
**Evidence pointer** Synthetic design and mechanism proxies in `manuscript/sections/04-methods.tex:10-27`; V2/V3 results in `manuscript/sections/05-results.tex:4-73`; exact P4-X arm definitions and result in `submission/P4_X_PROMOTION_AUTHORITY_SECTION.tex:12-28`; acknowledged limits in `manuscript/sections/06-threat-model-limitations-and-interpretation.tex:1-58,165-178`.  
**Concern** V2 and V3 use synthetic mechanical-gold cases in which fields differ on the exact authority gates the governed rule evaluates. The external systems are mechanism-style reimplementations, not native executions. H2 is saturated, and the V3 advantage is largely output-alphabet attainability because most comparators cannot emit CannotCheck. In P4-X, B1 is defined without the full target promotion relation and B3 ties when supplied it. These results establish interface and rule behavior, not correct scientific promotion judgement on naturally occurring claims.
**Alternative interpretation** P4 provides a benchmark-identifiability theory and exact conformance evidence for a fail-closed promotion interface.
**Why it matters** The headline scientific-authority claim requires evidence that the registered gates correspond to correct promotion decisions under real source ambiguity, not only that a rule wins a benchmark built from its own predicate.
**Resolution test** Execute a prospectively frozen naturalistic panel of independently adjudicated scientific claims with difficult benign and hostile cases, source-disjoint replication, native external systems or faithful executable adapters, matched information and resources, a three-terminal comparator, external custody, and cluster-level harm and recall endpoints. Otherwise narrow the paper to verification-axis attainability and exact interface conformance, and remove general scientific-judgement implications.

### R1-P4-M2 [protected evidence is not independently reviewable]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Supporting data and central code accessible to reviewers.  
**Claim pointer** Protected V2 counts and P4-X results are treated as publication-authorizing evidence with local independent reproduction.  
**Evidence pointer** `manuscript/sections/08-data-and-code-availability.tex:4-20,162-163`; custody description in `manuscript/sections/04-methods.tex:10-20`; result claims in `manuscript/sections/05-results.tex:4-18,73`.  
**Concern** The packet does not provide the 420 cases, protected per-case gold, raw traces, candidate outputs, scoring code, safe bundle, or P4-X records. The manuscript states that protected gold and traces are withheld, and the local reproducer only reconstructs aggregates from a safe bundle. Repository paths and a GitHub Actions run ID are not a reviewer access mechanism. DOI assignment is pending, and the availability section is combined rather than split.
**Alternative interpretation** Withholding public protected gold may preserve benchmark custody, but confidential reviewer access or a trusted controlled audit is still required.
**Why it matters** The central 0/360 and 400/400 claims cannot be independently checked, including whether the generated cases, gold terminals, and comparator implementations match the stated estimand.
**Resolution test** Provide confidential reviewer access to the full case-generation specification, protected labels, candidate-visible packets, scorer and independent reproducer, execution manifests, and traces sufficient to audit leakage and denominators. If raw gold cannot leave custody, arrange a documented controlled-access audit and provide per-case blinded records plus a trusted verification receipt. Add separate Data and Code availability statements and a stable review locator.

## Minor Comments

### R1-P4-m1 [elementary theory versus empirical contribution]

**Severity** Minor  
**Target criterion** Clear statement of contribution.  
**Affected element** Verification-axis theory.  
**Evidence pointer** `manuscript/sections/02a-verification-axis-identifiability.tex:11-62,64-126`.  
**Issue** The Bayes-risk, fibre-constancy, data-processing, and total-variation results are mathematically correct-looking but largely standard consequences. Their scientific contribution is the application and composition, not the generic identities.
**Required correction** Separate standard lemmas from the genuinely new claim and avoid counting each consequence as an independent major theoretical advance.

## Blocking technical failings

- `R1-P4-M1`: no naturalistic construct validation or native matched comparator result.
- `R1-P4-M2`: protected central evidence is not review-accessible.
- `R1-X-M1`: approximate abstract 591 words and ten main displays exceed NMI limits.

## Assessment against NMI criteria

- **Universal validity:** Exact benchmark counts may be internally valid, but the benchmark does not identify real scientific promotion competence.
- **NMI-specific advancement:** The measurement-theory framing is potentially relevant. The current empirical story is not sufficiently external or well-supported for the broad Article claim.
- **Cross-disciplinary intelligibility:** The main distinction is understandable. Source-transport and version chronology dominate the Results.
- **Data/code reviewability:** Not met.
- **Article format:** Abstract and display limits are exceeded.

## Recommendation posture

**Reject in present form.** A shorter theory and benchmark-identifiability paper may be defensible. An NMI Article about scientific promotion requires the unexecuted naturalistic, matched, independently adjudicated study.

---

# Paper 5

## Overall assessment

P5 articulates a responsible governance principle: failures should become persistent evidence, revisions require causal discrimination, fresh transfer must remain separate from replay, and candidates cannot certify their own promotion. The manuscript does not contain the empirical study needed to assess whether this architecture improves method evolution. Its primary H1-H4 campaign is unexecuted, zero of six comparator arms is ready, and 71 of 126 execution fields remain blocking. The only performance-like result is a single glm-5.2 run on 24 constructed cause-label cases, with no matched baseline and three retained errors. One public known-fix Defects4J cluster has `n=1`. Seven main tables have no admissible rows. This is not a completed NMI Article.

## Central claim and evidence readout

The paper claims that minimal method revision under observational equivalence should be governed by persistent failure knowledge, discriminator coverage, isolated challengers, protected fresh transfer, and external promotion custody. The formal factorization and Bayes results are acknowledged as standard consequences. The diagnostic archive scores 21/24 on constructed labels. P5-RD-01 and P5-RD-03 are unexecuted; P5-RD-02 contains one public known-fix cluster and a post-outcome archival audit. Synthetic interface audits pass 90/90 and 231/231 contract cases but execute no comparator. The six-arm campaign remains at 0/6 ready with 71 blockers and no protected outcome.

## Major strengths

- The manuscript does not convert unexecuted studies into null results.
- The three diagnostic errors and harmful or adverse cells are preserved.
- It correctly distinguishes conformance, replay, fresh transfer, and promotion authority.
- Statistical unit language for the `n=1` Defects4J cluster and fixed 24-case suite is appropriately cautious.

## Major Concerns

### R1-P5-M1 [the primary scientific study has not been executed]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Substantial novel research and a complex, well-supported Article story.  
**Claim pointer** Failure-governed method evolution improves protected fresh development outcomes while preventing harmful transfer and self-promotion. See `manuscript/sections/01-scope.tex:20-57` and `manuscript/sections/07-evaluation.tex:40-60,70-108`.  
**Evidence pointer** Design freeze and unbound execution in `manuscript/sections/07-evaluation.tex:40-68`; 0/6 readiness and remaining blockers in `:70-303`; diagnostic and `n=1` development evidence in `manuscript/sections/09-results-attribution.tex:1-70`; empty result tables in `:194-205`; limitations in `manuscript/sections/10-limitations.tex:1-225`.  
**Concern** H1-H4 remain CannotCheck. There is no protected fresh-task improvement estimate, harmful-transfer guard, matched baseline, executed ablation, protected evaluator, or external custody. The 21/24 cause-label score is a single-model diagnostic on a fixed constructed suite and is not the primary endpoint. The one known-fix replay cannot estimate transfer or method improvement. Interface preflights and blocker reduction are preparation, not scientific outcomes.
**Alternative interpretation** P5 is a formal governance proposal, preregistration, and research programme with local conformance tests.
**Why it matters** NMI Articles report completed original research. A protocol and execution-readiness programme cannot support the claimed safety or effectiveness of governed method evolution.
**Resolution test** Execute a prospectively frozen matched campaign with source-disjoint issue clusters, at least one fresh protected task per development episode, runnable native comparator arms under matched resources, blinded revision-responsibility gold, a protected one-shot evaluator, harmful-transfer and difficult-benign recall gates, cluster-level inference, and external result verification. The required sample size should follow the actual cluster variance and planned effect, not the current count-only design. If this cannot be done, change the target or article type and present the work as a theory, perspective, or registered protocol without effectiveness claims.

### R1-P5-M2 [the formal composition does not by itself establish a new method]

**Severity** Major  
**Blocking** Yes for the current Article claim  
**Target criterion** Substantial novel research and scientific advancement beyond architecture description.  
**Claim pointer** Revision factorization, Bayes risk, discriminator cover, adaptive leaf purity, stochastic transcript separation, and non-self-promotion jointly motivate a method-evolving architecture.  
**Evidence pointer** `manuscript/sections/02a-minimal-method-revision-theory.tex:1-233`; novelty boundary in `manuscript/sections/01-scope.tex:36-59`; architecture limitation in `manuscript/sections/10-limitations.tex:1-35`.  
**Concern** The manuscript appropriately acknowledges that factorization, conditional Bayes risk, set cover, active diagnosis, and transcript separation are standard or direct consequences. The remaining claimed contribution is their composition into a governance architecture. Without an executed discriminator or fresh-transfer study, the composition has no demonstrated predictive, causal, safety, or performance advantage. The no-self-promotion corollary is an information-interface impossibility statement, not empirical evidence that the proposed custody design is sufficient against realistic gaming.
**Alternative interpretation** The work is a rigorous conceptual framework and protocol for evaluating self-improving agents.
**Why it matters** Architecture alone does not meet the NMI Article requirement for a substantial, well-supported original research story.
**Resolution test** Identify one nontrivial prediction unique to the composition and test it in the protected campaign, for example lower false broad revision at matched fresh improvement and harm, with ablations that isolate discriminator coverage, fresh-transfer separation, and external custody. If no such executed test is available, reduce the contribution claim to a synthesis and formalization and select a compatible non-Article format or venue.

### R1-P5-M3 [data, code, and licensing are not review-ready]

**Severity** Major  
**Blocking** Yes  
**Target criterion** Reviewer access to central data/code; separate availability statements; executable reproducibility.  
**Claim pointer** The repository contains the controller, diagnostic archive, protocols, preflights, and table generator.  
**Evidence pointer** `manuscript/sections/11-ethics-reproducibility.tex:1-120,200-229`.  
**Concern** The packet contains none of the 24 raw diagnostic records, controller code, protocol objects, comparator ledgers, or result receipts. The availability section gives repository-relative paths and a repository name but no stable link or private review access. DOI assignment is pending. The manuscript explicitly says there is no repository-level licence and redistribution terms are unresolved. Data and code are combined rather than separately headed.
**Alternative interpretation** Internal hashes and clean regeneration may protect local integrity, but they do not give reviewers access or legal clarity.
**Why it matters** Even the limited 21/24 diagnostic cannot be audited from the supplied packet, and central custom code is unavailable for peer review.
**Resolution test** Provide reviewer access to the exact commit, raw diagnostic rows, table generator, controller, protocol files, and all preflight receipts. Supply a locked environment and one-command reproduction for the actual reported results. Add separate Data Availability and Code availability sections, a review locator, an explicit OSI-compatible code licence where possible, and precise restrictions for third-party task content.

## Minor Comments

### R1-P5-m1 [empty result tables]

**Severity** Minor  
**Target criterion** Concise and evaluable Article presentation.  
**Affected element** Seven main-text result tables with no admissible rows.  
**Evidence pointer** `manuscript/sections/09-results-attribution.tex:194-205`; `manuscript/tables/P5-2_replay_vs_fresh_scatter.tex` through `P5-T3_harmful_null_interventions.tex`.  
**Issue** Empty tables document planned endpoints but visually resemble missing results in a completed Article.
**Required correction** Remove them from the Article. Put the prospective endpoint schema in the preregistration or Supplementary Information and state once in the main text that the campaign is unexecuted.

## Blocking technical failings

- `R1-P5-M1`: the primary campaign and all matched comparisons are unexecuted.
- `R1-P5-M2`: the formal composition has no demonstrated scientific advantage.
- `R1-P5-M3`: data, code, and licensing are not review-ready.
- `R1-X-M1`: approximate abstract 656 words and ten main displays exceed NMI limits.

## Assessment against NMI criteria

- **Universal validity:** The manuscript accurately reports its lack of empirical authority. That accuracy also means the central effectiveness claim is presently unsupported.
- **NMI-specific advancement:** The governance problem is relevant, but the paper is a protocol and theory programme, not a completed well-supported Article.
- **Cross-disciplinary intelligibility:** The opening architecture is clear. The 38-page blocker and preflight chronology is not an effective Article narrative.
- **Data/code reviewability:** Not met.
- **Article format:** Abstract and display limits are exceeded.

## Recommendation posture

**Reject in present form.** This paper should not return as an NMI Article until the protected matched campaign exists. Before then, a formal framework, Perspective, or registered-protocol venue is the scientifically honest route.

---

# Per-paper disposition summary

| Paper | Current NMI Article posture | Central blocking reason |
|---|---|---|
| P1 | Reject in present form | Exact authored worlds do not establish naturalistic scientific-revision authority. |
| P2 | Reject in present form | No positive matched open-world discovery result; nearest real screening results are adverse. |
| P3 | Reject in present form | Formal theory lacks naturalistic construct validation and source-level generalization. |
| P4 | Reject in present form | Synthetic gate-conformance benchmarks do not establish scientific-promotion judgement. |
| P5 | Reject in present form | The primary protected campaign has not been executed. |

## Final Reviewer 1 conclusion

None of P1-P5 is ready for top-tier NMI Article peer review at this immutable commit. The decisive gap is not a need to hide or rhetorically reverse negative findings. The manuscripts already preserve adverse evidence well. The gap is that positive authority is concentrated in authored exact contracts, synthetic mechanics, local conformance, or unexecuted protocols, while the titles and theoretical framing concern scientific decisions in open, naturalistic settings. The minimum scientifically valid route is paper-specific. P1, P3, and P4 need independent naturalistic construct-validity studies if they retain their broad empirical framing. P2 needs a matched external acquisition campaign or a theory-only repositioning. P5 needs its primary campaign executed before it is a research Article. All five also need complete reviewer access to central evidence and a substantial NMI-format rewrite.

No pytest, repository CI, new model experiment, live scientific outcome, or external-custody claim was generated for this review.
