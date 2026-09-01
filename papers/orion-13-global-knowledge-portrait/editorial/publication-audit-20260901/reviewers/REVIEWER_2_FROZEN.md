sha256:db9e60ba90507adb485e04aac1e76f1cdfb61b63101607bba5889e04bee1b36f manuscript.pdf

## Overall assessment

This Brief Report presents a deliberately bounded evaluation of a coordinate-governed rule for deciding whether already-structured scientific projections may be merged. Its principal contribution is not a general semantic-integration system, but a compact decision-layer formulation, a prospectively frozen fixed-panel comparison, and an executable conformance contract.

The manuscript is unusually careful about adverse and null findings. It reports that all six discriminating holdout errors arose from polarity contrasts; the remaining 19 holdout cases did not discriminate the rules; four coordinate-ablation cells produced zero measured change; the failing comparator was intentionally weak; the holdout was not fully source-disjoint or independently adjudicated; and the 400 generated records represent only eight unique candidate-visible states. These limitations are carried consistently into the conclusions.

The work fits the stated F1000Research Brief Report category as a short report of a preliminary, falsifiable methods observation. No broad-impact or prestige threshold is applicable. Two presentation-level technical issues nevertheless prevent the supplied manuscript from making the evaluated rule and its two evidence layers fully reproducible without consulting external implementation artifacts.

## Central claim and evidence readout

The defensible central claim is:

> On the frozen 32-case holdout, retaining polarity and an explicit non-merge terminal prevented the six false merges made by the registered flat predicate rule, without increasing false splits relative to the exact-coordinate conservative rule.

The reported evidence directly supports that fixed-panel claim:

- Coordinate-governed rule: 0/32 false merges and 0/32 false splits.
- Flat canonicalization: 6/32 false merges, all involving polarity contrasts.
- Paired false-merge difference: −0.1875, with the stated fixed-panel bootstrap diagnostic [−0.34375, −0.0625].
- False-split difference against the conservative comparator: 0, diagnostic [0, 0].
- Nineteen cases in the other two families did not discriminate among the rules.
- Ablations of referent, construct, measurement, and temporal context produced zero measured change.
- The conformance battery establishes exact behavior over eight authored decision archetypes repeated across labels and identifiers; it does not establish population performance.
- The information-equivalent typed implementation tied the complete rule at 400/400, as it should.
- The strong semantic product’s 250/400 result is explicitly conditioned on its narrower information and output interface and is not presented as general superiority evidence.

The evidence does not establish independent value for every coordinate, superiority over deployed integration systems, raw-text extraction performance, naturalistic transport, population error rates, or downstream scientific utility. The manuscript correctly says so.

## Atomic coverage check

| Atomic claim | Evidence supplied | Coverage judgment |
|---|---|---|
| The holdout was prospectively frozen before outputs were examined. | Methods §2.2 describes the frozen digest, revisions, evaluators, seed, margins, and terminal rule. | Covered narratively; underlying protocol is said to reside in the repository. |
| Development and holdout contain 32 cases each and are case-identifier-disjoint. | Methods §2.2; development and holdout results are reported separately. | Covered, with the important adverse qualification that two locator/hash combinations recur. |
| The holdout spans three authored families of sizes 13, 13, and 6. | Methods §2.2. | Covered. |
| Coordinate-governed mapping made no holdout false merges. | Table 1 and Results. | Covered. |
| Flat canonicalization made six holdout false merges. | Table 1 and Results. | Covered. |
| All six flat-rule errors were polarity contrasts. | Results, paragraph following Table 1. | Covered. |
| The other 19 cases did not discriminate the rules. | Results and Abstract. | Covered and preserved as a null result. |
| The false-merge difference was −0.1875 with diagnostic [−0.34375, −0.0625]. | Table 1 and Methods §2.3. | Covered. |
| The false-split difference from the conservative rule was zero with diagnostic [0, 0]. | Table 1. | Covered. |
| Removing the modality/polarity/attribution/discourse group reproduced the false-merge increase. | Results. | Covered as a grouped ablation, not as evidence for the independent contribution of each member. |
| Four other coordinate ablations had zero measured effect. | Results. | Covered; the manuscript properly interprets the nulls as absent comparison opportunity rather than dispensability. |
| An independent implementation check reproduced the verdict. | Results. | Covered with the adverse qualification that it shares snapshot and custody and is not external replication. |
| The conformance battery contains 400 records but only eight unique candidate-visible states. | Methods §2.4 and Discussion. | Covered. |
| Complete, strong-product, canonical, and information-equivalent implementations scored 400/400, 250/400, 50/400, and 400/400. | Abstract and Results. | Covered. |
| The complete-minus-structured difference was +0.375 with diagnostic [0.3275, 0.4225] and 150–0 discordance. | Results. | Covered, subject to clarification of the relation between the three-decision scientific rule and four-output conformance interface. |
| The study does not establish population rates or general system superiority. | Abstract, Methods, Results, and Discussion. | Covered consistently. |
| Data and software are publicly available at a pinned repository snapshot. | Data and software availability statement. | Asserted with a commit-specific location; accessibility was not independently tested under this isolated review. |
| The contribution is distinct from extraction, ontology matching, alignment repair, variable modelling, provenance representation, and stance work. | Introduction and references. | Partly covered: adjacent fields are identified, but the exact rule-level distinction from the closest prior merge-decision formalisms remains insufficiently explicit. |

## Major strengths

- The inferential scope closely matches the actual design. The manuscript repeatedly distinguishes fixed-panel diagnostics from population uncertainty.
- Null and adverse results are not concealed or rhetorically diluted.
- The manuscript does not treat 400 generated rows as 400 independent scientific observations.
- Comparator limitations are explicit: the flat comparator is intentionally weak, the semantic product has a narrower interface, and the information-equivalent comparator must tie.
- Prospective freezing is presented as protection against outcome-contingent adaptation, not as independent adjudication.
- The distinction among non-merge, insufficient evidence, and admissible merge is conceptually useful for scientific-information integration.
- The discussion identifies appropriate future extensions while explicitly treating them as optional successors rather than requirements for this Brief Report.
- The standard Brief Report sections, declarations, and data/software statement are present, and the report is concise and readable.

## Major Concerns

### R2-MC-01

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Methods transparency and reproducibility
- **Claim pointer:** Methods §2.1, especially Equation (1) and the statements defining admissible merge, typed non-merge, and undetermined
- **Evidence pointer:** Equation (1) enumerates nine coordinates, but the manuscript supplies only verbal terminal conditions and no complete decision function, compatibility relation, precedence rule, or worked input-output example.
- **Concern:** The scientific rule being evaluated is not specified sufficiently within the article to permit repetition. A reader can see which coordinates exist and the intended three terminals, but cannot determine from the manuscript alone what constitutes compatibility or required incompatibility for each coordinate, which coordinates are load-bearing in which circumstances, how conflicting coordinate results are composed, or how terminal precedence is resolved.
- **Alternative interpretation:** The complete formal specification may be contained in the pinned repository, and the manuscript may intend the article to summarize rather than reproduce that contract.
- **Why it matters:** F1000Research’s supplied Brief Report criteria require methods that permit repetition. The central object of evaluation is the rule itself; therefore, its operative semantics cannot be delegated entirely to code or records without at least a compact normative specification in the article.
- **Resolution test:** Add a concise decision table, pseudocode block, or formal definition that maps coordinate-level states to the three scientific terminals, states precedence and missingness behavior, and includes at least one merge, one non-merge, and one undetermined example. Existing results need not be rerun if the added specification exactly documents the frozen implementation.

### R2-MC-02

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Technical soundness and bounded inference
- **Claim pointer:** Methods §2.1 and §2.4; Results conformance paragraph; Discussion first paragraph
- **Evidence pointer:** Section 2.1 defines three scientific decisions—admissible merge, typed non-merge, and undetermined—whereas §2.4 says the complete rule can return four outputs—merge, obstruction, plural view, and unresolved.
- **Concern:** The relationship between the three-decision evaluated mapping rule and the four-output conformance interface is not defined. In particular, it is unclear whether “plural view” is a subtype of typed non-merge, an additional scientific decision, or an interface-only state, and whether “obstruction” is exactly coextensive with typed non-merge.
- **Alternative interpretation:** The four conformance outputs may refine the three scientific terminals, with obstruction and plural view both mapping to typed non-merge.
- **Why it matters:** Without an explicit crosswalk, readers cannot tell whether the conformance battery tests the same rule as the holdout, a refinement of it, or a separate contract. This weakens the claimed connection between the fixed-panel observation and the executable interface result.
- **Resolution test:** Provide an exhaustive mapping between the four conformance outputs and the three scientific decisions, explain whether the mapping is lossless or many-to-one, and identify which reported metrics are computed before versus after that mapping. No new experiment is required unless this crosswalk reveals that currently combined results were scored under incompatible decision definitions.

### R2-MC-03

- **Severity:** Major
- **Blocking:** No
- **Target criterion:** Literature-context adequacy
- **Claim pointer:** Introduction, paragraphs 2–3; Discussion, final paragraph
- **Evidence pointer:** References [1], [4], [5], [8]–[11] establish adjacent work in ontological unpacking, matching, repair, provenance, FAIR interoperability, and stance, but the manuscript does not identify a closest rule-level antecedent or compare its terminal semantics with prior abstaining, inconsistency-aware, or provenance-sensitive alignment decisions.
- **Concern:** The manuscript positions itself against broad neighbouring programmes more clearly than against the closest prior decision-rule formulations. Consequently, the originality claim is plausible but underspecified: it is unclear whether the novel element is the coordinate tuple, the explicit non-merge/undetermined distinction, the combination of those elements, the prospective fixed-panel evaluation, or the executable contract.
- **Alternative interpretation:** The intended contribution may be primarily empirical and contractual—a frozen evaluation of a deliberately small rule—rather than invention of the underlying semantic distinctions.
- **Why it matters:** A Brief Report does not need transformative novelty, but readers should be able to distinguish the precise incremental contribution from established ontology-alignment, provenance, inconsistency-repair, and abstention concepts.
- **Resolution test:** Add a short closest-prior-work comparison stating which components are inherited, which are adapted, and which exact combination or evaluation is new. Bound originality to that identified increment; no additional benchmark or experiment is needed.

## Minor Comments

### R2-MI-01

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Readability and evaluability
- **Claim pointer:** Results, conformance paragraph
- **Evidence pointer:** The phrase “complete-minus-structured difference” appears after the comparator has been named “strong semantic product.”
- **Concern:** Comparator terminology changes without explanation.
- **Alternative interpretation:** “Structured” may be shorthand for the strong semantic product.
- **Why it matters:** Stable naming is important where multiple information interfaces and terminal alphabets are being compared.
- **Resolution test:** Use one comparator name consistently or define the abbreviation at first use.

### R2-MI-02

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Underlying-data accessibility
- **Claim pointer:** Data and software availability
- **Evidence pointer:** A commit-pinned repository path is provided, while the manuscript states that a repository DOI may be added and none is currently asserted.
- **Concern:** The statement identifies a precise snapshot but not a persistent archive identifier. This is appropriately presented as unresolved rather than falsely claimed.
- **Alternative interpretation:** A commit-pinned public repository may satisfy immediate access requirements even before archival deposit.
- **Why it matters:** Long-term preservation and immediate accessibility are related but distinct. The target-criteria card identifies the persistent archive identifier as an unresolved human filing input, not an established scientific defect.
- **Resolution test:** During filing, confirm that the cited snapshot is publicly accessible and, if required by the platform, add the eventual persistent archive identifier without altering the scientific claims.

## Blocking technical failings

- **R2-MC-01:** The manuscript does not yet contain a reproducible normative specification of the evaluated decision rule.
- **R2-MC-02:** The crosswalk between the three scientific decisions and four conformance outputs is absent.

No new experiment is required to resolve either issue unless the requested semantic crosswalk exposes an actual scoring contradiction.

## Assessment against target criteria

- **Brief Report scope and article-type fit:** Strong fit. The manuscript reports a small, preliminary, falsifiable observation and an associated protocol/interface contract within a concise standard structure.
- **Technical soundness and bounded inference:** The numerical claims are internally coherent in the supplied text, and limitations are unusually well bounded. The three-terminal/four-output ambiguity must be resolved.
- **Methods transparency and reproducibility:** The study design, panel sizes, freezing, comparator roles, margins, bootstrap settings, and scientific units are described. The operative mapping rule itself remains insufficiently specified in the article.
- **Underlying-data accessibility:** A commit-specific public repository location and licensing statement are supplied. Accessibility could not be independently checked within this isolated packet, and no persistent archive identifier is asserted.
- **Literature-context adequacy:** Relevant adjacent fields are cited, but the closest rule-level prior work and exact incremental originality require sharper positioning.
- **Readability and evaluability:** Generally clear, concise, and disciplined. Comparator terminology and decision-alphabet mapping need clarification.
- **Required declarations and policy compliance:** Data/software availability, ethics, author contributions, competing interests, funding, licensing, and AI-use statements are present. The remaining identity, ORCID, licence, fee, AI-policy, and portal confirmations are human filing inputs rather than scientific defects.
- **Target-specific significance:** The significance is appropriately modest: preventing six false agreements in one discriminating authored family while preserving a non-merge/undetermined distinction. This is sufficient as a potentially useful Brief Report observation if kept within the manuscript’s existing bounds. No broad-interest or field-transforming-impact criterion should be imposed.
- **Originality:** The frozen evaluation and executable-contract framing appear incrementally original, but the manuscript should state more precisely which rule components or combinations are new relative to the closest prior work.

## Recommendation posture

The report is potentially suitable for its stated Brief Report purpose after focused clarification of the rule specification, the three-to-four terminal mapping, and the exact incremental contribution relative to prior work. The null results, adverse comparator qualifications, same-programme adjudication limitation, eight-state conformance ceiling, and bounded disposition should remain unchanged. No additional experiment is indicated from the supplied material.