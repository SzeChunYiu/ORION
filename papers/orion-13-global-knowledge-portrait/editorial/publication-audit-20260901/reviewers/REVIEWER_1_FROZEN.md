sha256:db9e60ba90507adb485e04aac1e76f1cdfb61b63101607bba5889e04bee1b36f manuscript.pdf

## Overall assessment

This Brief Report presents a deliberately bounded fixed-panel evaluation of a coordinate-governed mapping rule. Its principal empirical readout is internally coherent: on 32 confirmatory cases, the rule had 0 false merges versus 6/32 for an intentionally weak flat comparator, while showing no false-split disadvantage against the conservative comparator. The manuscript appropriately treats bootstrap intervals as fixed-panel diagnostics, identifies the authored case families and eight conformance archetypes as the scientific units, and repeatedly disclaims population, deployment, extraction, and downstream-utility conclusions.

The central technical limitation is reproducibility from the article: Equation 1 names the coordinates, but the manuscript does not operationally define the compatibility relations, “required incompatibility,” “load-bearing coordinate,” or the decision algorithm. A related ambiguity arises because the primary rule has three outcomes whereas the conformance implementation has four, without an explicit crosswalk. These are reporting and specification defects resolvable without new experiments.

## Central claim and evidence readout

The supportable central claim is narrow: for this frozen authored panel, preserving polarity-related information and allowing a typed non-merge terminal prevented six false agreements made by the registered flat predicate comparator.

Evidence readout:

- Confirmatory holdout: 32 cases in three authored families.
- Coordinate-governed rule: accuracy 32/32, false merges 0/32, false splits 0/32, abstentions 0/32.
- Flat comparator: accuracy 26/32 and false merges 6/32.
- Paired false-merge difference: −6/32 = −0.1875, with the reported fixed-panel bootstrap diagnostic [−0.34375, −0.0625].
- Conservative comparator: accuracy 26/32, 6/32 abstentions, and no measured false-split difference.
- All discrimination occurred in six polarity contrasts within one 13-case family; the other 19 cases did not discriminate the rules.
- The referent, construct, measurement, and temporal-context ablations were null on this panel. The manuscript correctly interprets these nulls as absent comparison opportunity, not evidence of dispensability.
- The 400 conformance rows represent eight unique authored decision states repeated across labels and identifiers. The reported scores therefore demonstrate deterministic contract performance on those states, not 400 independent scientific observations.
- The information-equivalent comparator’s 400/400 tie is an implementation-equivalence check, not evidence of external replication.
- No evidence is offered for population error rates, raw-text extraction, naturalistic transport, deployed-system superiority, downstream utility, or the independent value of every coordinate. Those adverse and null boundaries are appropriately preserved.

## Atomic coverage check

Atomic-claim coverage was checked independently against the supplied manuscript:

| Atomic claim | Direct evidence in the manuscript | Coverage assessment |
|---|---|---|
| A 32-case development panel preceded a frozen 32-case holdout | Methods §2.2; Results opening paragraph | Covered, but underlying records were not included in the review packet |
| Development and holdout identifiers are disjoint | Methods §2.2 | Asserted; not independently auditable from the supplied files |
| Two locator/hash combinations recur | Methods §2.2 | Asserted and appropriately disclosed |
| The holdout was prospectively frozen before output inspection | Methods §2.2 | Asserted; protocol details are externally referenced |
| Coordinate-governed mapping made 0 false merges | Table 1 | Numerically covered |
| Flat mapping made 6/32 false merges | Abstract; Table 1; Results | Numerically consistent |
| The paired difference equals −0.1875 | Table 1 | Arithmetically consistent with 0/32 minus 6/32 |
| The reported interval is a fixed-panel diagnostic | Abstract; Methods §2.3; Table 1 | Covered and correctly bounded |
| The false-split difference versus the conservative rule is zero | Abstract; Table 1 | Covered, although the handling of abstention in the error taxonomy should be made explicit |
| All six discriminating errors were polarity contrasts | Abstract; Results | Asserted; not independently auditable from case-level data in the packet |
| The other 19 cases did not discriminate the rules | Abstract; Results | Consistent with the stated family counts |
| Four coordinate ablations had zero measured change | Results | Covered as null results and not overinterpreted |
| The conformance battery has 400 rows but eight unique states | Methods §2.4; Results | Covered |
| Complete/strong/canonical/typed scores were 400/250/50/400 | Abstract; Results | Covered; raw scoring records are externally referenced |
| The strong product’s deficit reflects its narrower interface | Methods §2.4; Discussion | Covered and appropriately qualified |
| The typed comparator is information-equivalent | Methods §2.4; Results | Asserted; equivalence mapping is not specified in the article |
| The independent scorer is not external replication | Results | Covered and correctly bounded |
| Data and software are associated with a pinned commit | Data and software availability | Covered by a commit-specific repository location |
| No persistent archive DOI is asserted | Data and software availability | Explicitly and appropriately disclosed |
| Broad generalization claims are not established | Abstract; Discussion | Covered repeatedly and consistently |

No omitted adverse result or inflated effective sample size was identified. The main coverage gaps concern operational definitions and auditability, not contradiction of the reported arithmetic.

## Major strengths

- The inferential scope is unusually disciplined. The manuscript distinguishes a fixed-panel diagnostic from population uncertainty and does not present bootstrap resampling as creating independent evidence.
- Scientific units are explicitly identified as three authored families and eight unique conformance archetypes rather than 432 independent observations.
- Development and confirmatory outcomes are not pooled.
- The weak comparator is openly described as intentionally weak, and the manuscript does not claim superiority over contemporary deployed systems.
- Same-programme gold construction, partial source overlap, authored archetypes, comparator alphabet differences, and shared custody of the implementation check are all disclosed.
- Null ablations and the 19 non-discriminating holdout cases are retained and interpreted conservatively.
- The discussion clearly distinguishes insufficient evidence from a negative mapping decision.
- The proposed future work is explicitly optional and is not presented as a condition for this bounded Brief Report.
- Required ethics, contribution, competing-interest, funding, AI-use, and data/software statements are present.

## Major Concerns

### R1-01

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Methods transparency and reproducibility
- **Claim pointer:** Methods §2.1–2.3; central claim that the coordinate-governed rule avoided six false merges
- **Evidence pointer:** Equation 1 and the prose stating that a “required incompatibility” produces non-merge and a missing “load-bearing coordinate” produces undetermined
- **Concern:** The manuscript names nine projection fields but does not provide an executable or sufficiently precise decision specification. It does not define field-level equivalence or incompatibility, identify which coordinates are load-bearing under which conditions, state how discourse relations and assumptions enter the decision, or give pseudocode/a decision table for resolving combinations of compatible, incompatible, and missing coordinates. Consequently, an independent reader cannot reproduce the evaluated rule from the article.
- **Alternative interpretation:** The complete specification may exist in the pinned repository and the article may be intended only as a concise summary.
- **Why it matters:** F1000Research’s supplied criterion requires methods that permit repetition. Repository availability is valuable, but the manuscript must still identify the precise frozen artifact and explain the scientific decision rule sufficiently for readers to understand what was tested.
- **Resolution test:** Add a compact normative decision table or pseudocode defining every terminal condition, coordinate relation, precedence rule, and missing-data rule; identify the exact frozen specification file within the pinned snapshot. An independent implementation based on that description should yield the reported decisions without discretionary interpretation. No new experiment is required.

### R1-02

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Technical soundness and bounded inference; methods transparency and reproducibility
- **Claim pointer:** Methods §2.1 and §2.4; Results claim that the conformance battery confirms implementation of “the deterministic relation”
- **Evidence pointer:** The primary rule returns three decisions—merge, typed non-merge, or undetermined—whereas the conformance “complete rule” returns four—merge, obstruction, plural view, or unresolved
- **Concern:** The manuscript does not state whether these are the same rule at different abstraction levels or distinct interfaces, and it supplies no mapping between the three and four terminal alphabets. In particular, it is unclear whether “plural view” maps to typed non-merge, constitutes a separate scientific decision, or occurs only outside the holdout.
- **Alternative interpretation:** “Obstruction” and “plural view” may be subtypes of typed non-merge, while “unresolved” may correspond exactly to undetermined.
- **Why it matters:** Without an explicit crosswalk, the conformance result cannot unambiguously validate the rule used for the confirmatory holdout. It also obscures the meaning of the information-equivalent comparator.
- **Resolution test:** Provide a total crosswalk between the two terminal sets, state which outputs occur in each evaluation, and explain how conformance success entails conformity of the three-way holdout decision. If plural view is a subtype, say so explicitly and show its scoring treatment. No new experiment is required.

## Minor Comments

### R1-03

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Technical soundness and bounded inference
- **Claim pointer:** Results, Table 1; Methods §2.3
- **Evidence pointer:** The conservative comparator has six abstentions but zero false splits
- **Concern:** The error taxonomy does not explicitly explain why an abstention on a merge-eligible case is not counted as a false split, or whether the six abstentions occurred on cases whose gold label made this distinction immaterial.
- **Alternative interpretation:** Abstention may be a distinct terminal category and therefore neither a split nor a merge error under the preregistered definitions.
- **Why it matters:** The second non-compensatory gate depends on the false-split measure, so its denominator and treatment of abstentions should be transparent.
- **Resolution test:** Define false merge, false split, abstention, accuracy, and their denominators in Methods, including how abstention is scored against each expected decision.

### R1-04

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Technical soundness and bounded inference
- **Claim pointer:** Abstract conclusion; Results ablation paragraph; Discussion opening paragraph
- **Evidence pointer:** All six errors were polarity contrasts; both removing the grouped coordinates and forcing compatibility without the non-merge terminal changed the false-merge rate by 0.1875
- **Concern:** The wording can be read as assigning separable causal credit to retained polarity and the non-merge terminal, although the reported interventions appear bundled and all discrimination comes from one polarity subset.
- **Alternative interpretation:** The intended claim is only that the complete decision condition—polarity information interpreted through a non-merge terminal—prevented these six merges.
- **Why it matters:** The panel does not establish independent component value, as the manuscript itself acknowledges.
- **Resolution test:** State consistently that the complete polarity-sensitive non-merge condition prevented the six errors, and avoid wording implying independently estimated effects of polarity preservation and terminal design.

### R1-05

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Underlying-data accessibility; required declarations and policy compliance
- **Claim pointer:** Data and software availability
- **Evidence pointer:** Pinned GitHub commit is supplied; “A repository DOI may be added after long-term deposit; none is asserted in this version”
- **Concern:** The commit-specific link provides version pinning, but no persistent archive identifier is yet asserted.
- **Alternative interpretation:** A public immutable commit may satisfy immediate accessibility even before archival deposition.
- **Why it matters:** Long-term preservation and the human filing requirement remain unresolved, although this is not a defect in the reported scientific result.
- **Resolution test:** Before filing, confirm public access to the exact snapshot and add a persistent archive identifier if required by the submission workflow. Preserve the bounded statement if no DOI exists; do not imply one has already been minted.

## Blocking technical failings

- **R1-01:** The evaluated mapping rule is not operationally specified sufficiently to permit independent repetition from the manuscript.
- **R1-02:** The relationship between the three-outcome scientific rule and four-outcome conformance implementation is undefined, preventing unambiguous interpretation of what the conformance battery validates.

No contradiction in the reported arithmetic, scientific-unit accounting, null results, or stated scope was identified from the supplied material.

## Assessment against target criteria

| Target criterion | Assessment |
|---|---|
| Brief Report scope and article-type fit | Fits a short, preliminary methods observation and remains concise and conventionally structured. |
| Technical soundness and bounded inference | The numerical summaries are internally coherent and the inference is carefully bounded. Terminal-alphabet and component-attribution ambiguities require clarification. |
| Methods transparency and reproducibility | Not yet sufficient because the decision rule and interface crosswalk are under-specified. |
| Underlying-data accessibility | A public, commit-pinned repository location is stated, but the underlying artifacts were not part of the supplied review packet and therefore could not be independently audited here. Persistent archival identification remains a bounded filing item. |
| Literature-context adequacy | Adequate for the narrow contribution; the manuscript distinguishes its rule from extraction, ontology matching, alignment repair, and broader interoperability programmes. |
| Readability and evaluability | Generally clear, with explicit limitations and well-presented results. Specialized terminal vocabulary needs definition. |
| Required declarations and policy compliance | Data/software, ethics, contributions, competing interests, funding, licensing, and AI-use statements are present. Human filing inputs identified in the criteria card remain outside the scientific assessment. |

## Recommendation posture

The bounded observation is potentially supportable as an F1000Research Brief Report after the two blocking specification issues are resolved. The required revisions concern transparent definition of the already-evaluated rule and its output crosswalk; they do not require new experiments. All null results, authored-panel limitations, comparator limitations, source-overlap disclosure, lack of external replication, absence of population inference, and the non-assertion of a repository DOI should remain intact.