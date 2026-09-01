sha256:114b4d2bd22c85dacf88a3741623f62ad45a1fad8d748abb4f1f214645a1c990 revised-manuscript.pdf

## Targeted rereview scope

This targeted rereview assesses only closure of concerns R3-01 through R3-03 from the prior frozen review and checks the revised manuscript for contradictions, new overclaims, lost null/adverse results, atomic-coverage gaps, and relevant F1000Research Brief Report compliance issues. No new experiments are requested.

## Prior-concern closure table

| ID | Status | Exact evidence pointer | Closure reason |
|---|---|---|---|
| R3-01 | CLOSED | Methods §2.1, Table 1; Methods §2.3, paragraphs 1–2; Data and software availability, paragraph 1 | Table 1 now provides a normative, ordered decision rule with first-applicable-condition precedence, coordinate comparisons, missingness handling, fine relations, and terminal decisions. Methods §2.3 operationally defines both comparators, registered coordinate ablations, and the force-compatibility ablation. The availability statement supplies exact paths for the protocol, cases, analysis, independent scorer, normative evaluator, four-way contract, and independent reconstruction. These additions satisfy the prior resolution test without requiring a new experiment. |
| R3-02 | CLOSED | Methods §2.4, final paragraph | The revision explicitly maps merge to admissible merge; obstruction and plural view to typed non-merge; and unresolved to undetermined. It identifies this as a many-to-one crosswalk, explains the special retention semantics of plural view, gives the archetype composition, and states that the four-way scores precede the crosswalk and do not constitute a second holdout evaluation. |
| R3-03 | OPEN | Data and software availability, final sentence; target-criteria.json, “unresolved_human_filing_inputs” | The manuscript still provides no persistent public archive identifier and explicitly states that no repository DOI is asserted. The commit-pinned snapshot and exact artifact paths support version-specific access, so this remains a bounded archival/filing matter rather than a demonstrated scientific defect or blocking technical failing. Closure requires a persistent identifier for the same frozen snapshot or confirmation that the journal accepts the commit-pinned repository at the relevant filing stage. |

## Independent atomic coverage check

| Atomic claim or boundary | Revised evidence | Judgment |
|---|---|---|
| Prospectively frozen 32-case holdout | Methods §2.2 identifies the frozen case digest, source revisions, evaluator identities, seed, margins, terminal rule, and outcome-blind selection | Covered |
| Development and holdout case identifiers are disjoint | Methods §2.2 | Covered |
| Holdout is not fully source-disjoint | Methods §2.2 reports two recurring source-locator/content-hash combinations | Covered; adverse result preserved |
| Coordinate-governed rule had 0/32 false merges and 0/32 false splits | Results, Table 2 | Covered |
| Flat comparator had 6/32 false merges | Results, Table 2 and following paragraph | Covered |
| All six discriminating errors were polarity contrasts | Abstract; Results, paragraph after Table 2 | Covered |
| The other 19 holdout cases did not discriminate the rules | Abstract; Results; Discussion, paragraph 2 | Covered; null result preserved |
| Fixed-panel false-merge difference and diagnostic | Abstract; Methods §2.3; Table 2 caption | Covered |
| False-split difference from the conservative comparator was zero | Abstract; Table 2 caption | Covered |
| Four single-coordinate ablations showed no measured change | Results, paragraph after Table 2 | Covered and explicitly not interpreted as dispensability |
| Grouped-coordinate and force-compatibility ablations reproduced the 0.1875 change | Methods §2.3; Results, paragraph after Table 2 | Covered with operational ablation definitions |
| Independent scorer is not external replication | Results, independent-scorer paragraph | Covered; shared custody is disclosed |
| Conformance battery contains 400 records but only eight candidate-visible states | Abstract; Methods §2.4; Discussion | Covered |
| Complete, strong-semantic, canonical, and information-equivalent results | Abstract; Results, final paragraph | Covered and internally coherent |
| Typed comparator must tie because it is information-equivalent | Methods §2.4; Results | Covered without treating the tie as independent superiority evidence |
| Three-way holdout and four-way contract alphabets are related but not identical | Methods §2.4, final paragraph | Covered by an explicit many-to-one crosswalk |
| No population, deployed-system, raw-text, coordinate-specific, or downstream-utility generalization is claimed | Abstract conclusion; Discussion | Covered; boundaries remain prominent |
| Broader studies are optional successors, not conditions imposed on this Brief Report | Discussion, final paragraph | Covered; bounded note disposition preserved |
| Data and software snapshot and artifact roles are identifiable | Data and software availability | Covered at commit and path level; persistent archival identifier remains open |
| Ethics, contributions, competing interests, funding, licensing, and AI-use statements | End matter and Data and software availability | Covered from the supplied manuscript |

No contradiction, new overclaim, lost null/adverse result, or material atomic-coverage gap was identified in the revision.

## New Major Concerns

None identified from the supplied material.

## New Minor Comments

None identified from the supplied material.

## Blocking technical failings

None identified from the supplied material.

The prior blocking reproducibility concern R3-01 is closed. The remaining open item, R3-03, is a bounded archival/filing matter already classified by the target criteria as an unresolved human filing input.

## Assessment against target criteria

- **Brief Report scope and article-type fit:** Meets. The manuscript remains a concise preliminary methods observation with conventional Introduction, Methods, Results, and Discussion sections.
- **Technical soundness and bounded inference:** Meets. The numerical claims are internally coherent, and the fixed-panel and contract-test evidence is not generalized beyond its design.
- **Methods transparency and reproducibility:** Meets from the supplied manuscript. The operative rule, precedence, missingness handling, comparators, ablations, scoring definitions, resampling settings, and exact repository artifacts are now specified.
- **Underlying-data accessibility:** Provisionally meets. A commit-pinned snapshot and exact artifact paths are supplied; persistent archival identification remains an open human filing input.
- **Literature-context adequacy:** Meets. The manuscript locates its narrow increment relative to extraction, ontology matching, interoperability, provenance, and stance work.
- **Readability and evaluability:** Meets. The former ambiguity between the holdout and conformance terminal alphabets is resolved.
- **Required declarations and policy compliance:** Largely meets from the supplied material. Data/software, ethics, contributions, competing interests, funding, licensing, and AI assistance are addressed. Identity, ORCID, licence-policy, AI-policy, fee, portal, and final-author confirmations remain human filing checks under the supplied criteria card.
- **Main-body concision and structure:** Meets on inspection as a concise Brief Report; no contrary word-count evidence is present in the supplied material.
- **Supplementary-material policy:** Meets as presented. Repository-hosted underlying data and software are identified rather than submitted as journal supplementary material.
- **Generalization boundaries:** Meets. Same-programme gold, incomplete source disjointness, weak-comparator scope, eight-state conformance support, absent raw-text evaluation, and lack of downstream validation are all disclosed.
- **Impact threshold:** Not applicable under the supplied target criteria.

## Recommendation posture

The prior blocking technical concern is closed, and no new substantive scientific or reporting concern is identified. R3-03 remains open only as a non-blocking persistent-archive filing item. The manuscript’s null results, adverse disclosures, bounded inference, and optional-successor-study disposition should be preserved.