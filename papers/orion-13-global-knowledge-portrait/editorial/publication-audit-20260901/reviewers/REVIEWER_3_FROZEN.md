sha256:db9e60ba90507adb485e04aac1e76f1cdfb61b63101607bba5889e04bee1b36f manuscript.pdf

## Overall assessment

This is a concise, carefully bounded Brief Report describing a fixed-panel evaluation of a coordinate-governed merge rule. The manuscript preserves its adverse and null results: all observed holdout discrimination comes from six polarity contrasts in one authored family; the remaining 19 holdout cases do not discriminate the rules; four coordinate-ablation cells show no measured change; the holdout is not fully source-disjoint; and the 400 generated records represent only eight unique candidate-visible states.

The numerical claims are internally coherent, and the conclusions generally remain within the evidence. The principal issue is reproducibility from the scientific description: the manuscript names the coordinates and terminal outcomes but does not fully specify the decision function, compatibility relations, or mappings between the holdout and conformance outcome vocabularies. The cited frozen repository may contain these details, but the article should identify them precisely enough for readers to locate and interpret the executable specification.

## Central claim and evidence readout

The central claim is appropriately narrow: on the authored, prospectively frozen 32-case holdout, retaining polarity and an explicit non-merge terminal prevented six false agreements made by the registered flat comparator, without increasing false splits relative to the conservative comparator.

The direct evidence is:

- Coordinate-governed rule: 0/32 false merges and 0/32 false splits.
- Flat comparator: 6/32 false merges, all polarity contrasts.
- Paired false-merge difference: −0.1875, with fixed-panel bootstrap diagnostic [−0.34375, −0.0625].
- False-split difference from the conservative rule: 0, with diagnostic [0, 0].
- The other 19 holdout cases did not distinguish the rules.
- Ablating referent, construct, measurement, or temporal context produced no measured change on this panel.
- The conformance battery establishes deterministic agreement with authored interface expectations, not population performance: 400 records reduce to eight unique decision states repeated across labels and identifiers.
- The information-equivalent typed implementation’s 400/400 result is an expected equivalence check, not independent evidence of superiority.
- The independent scorer is correctly described as an implementation check sharing repository custody, not an external replication.

These observations support the stated fixed-panel result. They do not independently establish the value of every coordinate, performance on raw text, naturalistic transport, population error rates, downstream utility, or superiority to deployed integration systems.

## Atomic coverage check

| Atomic claim | Evidence supplied | Coverage judgment |
|---|---|---|
| The holdout was prospectively frozen | Methods §2.2 describes the frozen digest, revisions, evaluator identities, seed, margins, and terminal rule | Covered narratively; artifact locations are not identified individually |
| Development and holdout identifiers are disjoint | Methods §2.2 | Covered narratively |
| The holdout is not fully source-disjoint | Methods §2.2 reports two recurring locator/hash combinations | Covered and appropriately adverse |
| Coordinate-governed mapping had no holdout false merges | Table 1 | Covered |
| Flat canonicalization had six false merges | Table 1 and Results text | Covered |
| All six false merges were polarity contrasts | Results text | Covered |
| The other 19 cases did not discriminate the rules | Results text | Covered and preserved as a null result |
| False-merge difference was −0.1875 | Table 1 permits direct calculation; caption reports it | Covered |
| Bootstrap diagnostic was [−0.34375, −0.0625] | Table 1 caption; resampling count and seed in Methods §2.3 | Covered, conditional on the repository implementation |
| False-split difference from the conservative rule was zero | Table 1 and caption | Covered |
| Four coordinate ablations produced zero measured change | Results text | Covered and correctly interpreted as absent comparison opportunity |
| Removing the grouped coordinates reproduced the 0.1875 change | Results text | Reported, but the exact ablation definition is not recoverable from the article |
| The independent scorer reproduced decisions and verdict | Results text and repository availability statement | Covered by report; correctly not called external replication |
| The conformance battery has 400 records but only eight unique states | Methods §2.4 | Covered and prominently bounded |
| Complete, strong semantic, canonical, and typed results were 400/400, 250/400, 50/400, and 400/400 | Abstract and Results | Covered |
| The complete-minus-structured difference was +0.375 with 150–0 discordance | Results | Arithmetically consistent with 400/400 versus 250/400 |
| The typed comparator is information-equivalent and must tie | Methods §2.4 and Results | Covered; this is a contract-equivalence check rather than independent validation |
| The panels do not establish broad generalization or downstream utility | Abstract and Discussion | Covered and appropriately bounded |
| Frozen data and software are publicly available at the stated commit | Data and software availability statement | Claimed with a commit-pinned URL; persistence and exact artifact navigation remain unresolved |
| Code and manuscript licences are Apache-2.0 and CC BY 4.0 | Data and software availability statement | Reported; external verification is outside the supplied packet |
| No human, personal-data, or animal involvement occurred | Ethics statement | Covered |
| Null/adverse results and bounded successor-study disposition are preserved | Results and Discussion | Covered; optional successors are explicitly not made conditions of this Brief Report |

## Major strengths

- The manuscript distinguishes fixed-panel diagnostics from population uncertainty.
- It identifies the true scientific-unit counts rather than presenting 432 rows as independent observations.
- The outcome-blind freezing procedure, disjoint case identifiers, seed, margins, and non-compensatory gates are reported.
- The intentionally weak comparator is described honestly and is not presented as a deployed state-of-the-art system.
- Same-programme gold construction, incomplete source disjointness, and shared custody of the implementation check are disclosed.
- Null results are not suppressed or converted into evidence of coordinate dispensability.
- The conformance battery is correctly framed as an executable contract test.
- The Discussion states generalization boundaries unusually clearly and treats broader validation as optional successor work, not as evidence already obtained.
- Required ethics, competing-interest, funding, contribution, AI-use, and data/software statements are present.

## Major Concerns

### R3-01

- **Severity:** Major
- **Blocking:** Yes
- **Target criterion:** Methods transparency and reproducibility
- **Claim pointer:** Methods §§2.1–2.4; all rule-comparison and ablation claims in Results
- **Evidence pointer:** Equation (1); prose definitions of merge, non-merge, and undetermined; commit-pinned repository statement
- **Concern:** The article does not operationally specify the evaluated coordinate-governed rule. It lists nine projection fields and gives high-level terminal conditions, but it does not define which coordinate relations are required, how compatibility or incompatibility is determined, which missing values are “load-bearing,” how precedence among terminal outcomes is resolved, or exactly how the registered ablations alter the rule. The comparator descriptions are similarly high-level. The repository may contain the executable specification, but the manuscript gives only a directory-level link rather than precise artifact names and roles.
- **Alternative interpretation:** For an executable methods observation, a commit-pinned repository containing frozen records, protocols, and deterministic analyses may provide sufficient operational detail even when the article contains only a conceptual summary.
- **Why it matters:** Readers cannot independently reconstruct the decision function, evaluate whether the comparators differ only in the claimed conditions, or understand what the ablation results mean without locating and interpreting unspecified repository files. This falls short of the target criterion that Methods permit repetition.
- **Resolution test:** Add compact pseudocode or a complete decision table defining coordinate relations, missingness handling, precedence, and terminal outputs; define each comparator and ablation against that specification; and cite exact repository paths for the frozen protocol, case manifest, evaluator, expected outputs, and independent scorer. No new experiment is required.

## Minor Comments

### R3-02

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Readability and evaluability
- **Claim pointer:** Methods §2.1 versus §2.4; Discussion, first paragraph
- **Evidence pointer:** The holdout rule has “admissible merge, typed non-merge, or undetermined,” while the conformance rule has “merge, obstruction, plural view or unresolved”
- **Concern:** The relationship between the three scientific decisions used for the holdout and the four conformance outcomes is not explained. “Typed non-merge,” “obstruction,” and “plural view” may be related, but the manuscript does not provide a mapping.
- **Alternative interpretation:** The holdout evaluator and conformance interface may intentionally expose different terminal alphabets for distinct purposes.
- **Why it matters:** Without an explicit crosswalk, readers may incorrectly assume that the 400-record contract battery directly validates the same three-way decision function used in the holdout.
- **Resolution test:** Add a sentence or small table showing which outcomes correspond, which are conformance-only refinements, and whether any aggregation occurs for holdout scoring.

### R3-03

- **Severity:** Minor
- **Blocking:** No
- **Target criterion:** Underlying-data accessibility; Required declarations and policy compliance
- **Claim pointer:** Data and software availability
- **Evidence pointer:** Commit-pinned GitHub URL; statement that no repository DOI is asserted
- **Concern:** The availability statement supplies a frozen commit but no persistent archive identifier. This is already recognized in the target-criteria card as an unresolved human filing input rather than a scientific defect.
- **Alternative interpretation:** A content-addressed Git commit provides exact version identification and may be sufficient for initial review if it is publicly accessible.
- **Why it matters:** Repository hosting and account state are not equivalent to long-term archival preservation, and durable access is central to reproducibility.
- **Resolution test:** Before final filing, provide a persistent public archive identifier for the same frozen snapshot, or document that the journal accepts the commit-pinned repository at this stage. Do not alter or silently replace the evaluated snapshot.

## Blocking technical failings

R3-01 is the only blocking technical failing identified from the supplied material. It concerns specification and artifact-level traceability, not a contradiction in the reported results, and can be resolved without new experiments.

No numerical contradiction, suppression of null/adverse results, or unbounded generalization claim was identified.

## Assessment against target criteria

- **Brief Report scope and article-type fit:** Meets. The report presents a small, preliminary methods observation in a concise conventional structure.
- **Technical soundness and bounded inference:** Meets. The reported arithmetic is internally coherent, and the manuscript repeatedly limits inference to the fixed authored panels.
- **Methods transparency and reproducibility:** Partially meets. The panel design, gates, bootstrap settings, and scientific-unit structure are reported, but the operative decision rule and ablations require a more explicit specification or exact artifact pointers.
- **Underlying-data accessibility:** Provisionally meets. A commit-pinned public snapshot is stated, but no persistent archive identifier is yet supplied.
- **Literature-context adequacy:** Meets from the supplied material. The work is situated relative to extraction, ontology matching, interoperability, provenance, and stance literature without claiming to solve those broader problems.
- **Readability and evaluability:** Largely meets. The main ambiguity is the unexplained relationship between the three holdout outcomes and four conformance outcomes.
- **Required declarations and policy compliance:** Largely meets. Data/software, ethics, contributions, competing interests, funding, licensing, and AI assistance are addressed. The target-criteria card appropriately leaves identity, ORCID, licence, AI-policy, fee, portal, and final-author confirmations to human filing checks.
- **Conciseness and structure:** Meets. The six-page manuscript appears consistent with a concise Brief Report; exact main-body word-count compliance is not independently established by the supplied metadata.
- **Supplementary-material policy:** Meets as presented. The manuscript points to repository data and software rather than presenting journal supplementary material.
- **Impact threshold:** Not applicable under the supplied target criteria.

## Recommendation posture

Scientifically suitable for a bounded F1000Research Brief Report once R3-01 is resolved through a reproducible rule specification and exact artifact-level pointers. R3-02 and R3-03 are non-blocking clarifications or filing matters. No new experiments are requested, and the manuscript’s null results, adverse disclosures, generalization limits, and optional-successor-study disposition should be preserved unchanged.