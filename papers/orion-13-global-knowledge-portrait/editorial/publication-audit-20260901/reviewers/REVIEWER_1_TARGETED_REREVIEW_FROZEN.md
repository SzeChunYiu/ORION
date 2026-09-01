sha256:114b4d2bd22c85dacf88a3741623f62ad45a1fad8d748abb4f1f214645a1c990 revised-manuscript.pdf

## Targeted rereview scope

This targeted rereview reassesses only the five concerns in the prior frozen R1 review and checks whether the revision introduces any contradiction, new overclaim, omitted null or adverse result, or atomic-coverage gap. The supplied text and PDF present the same substantive manuscript. No repository, external source, other review, or editorial material was consulted.

## Prior-concern closure table

| Prior ID | Status | Exact evidence pointer | Closure reason |
|---|---|---|---|
| R1-01 | CLOSED | Methods §2.1, Equation 1 and normative Table 1; Methods §2.3; Data and software availability | The revision now specifies an ordered, first-applicable-condition rule; exact identifier/enum equality; handling of empty, unresolved, and unnormalizable coordinates; all typed non-merge conditions; polarity/modality logic; and the admissible-merge terminal. Methods §2.3 defines comparator and ablation behavior, while the availability statement identifies the normative frozen evaluator. This resolves the requested operational specification without new experiments. |
| R1-02 | CLOSED | Methods §2.4, especially the paragraph beginning “This four-way contract refines…” | A total crosswalk is now explicit: merge → admissible merge; obstruction and plural view → typed non-merge; unresolved → undetermined. The manuscript states that plural view retains both projections, that the mapping is many-to-one, and that four-way scores are calculated before the crosswalk. The conformance battery is also correctly described as confirming its own interface rather than duplicating the holdout evaluation. |
| R1-03 | CLOSED | Methods §2.3, paragraph beginning “All rates use the 32 cases…”; Table 2 | False merge, false split, abstention, and their common 32-case denominator are explicitly defined. The revision states that unresolved predictions are abstentions rather than either error and explains that abstention on a gold non-merge case may reduce exact-match accuracy without constituting a false split. |
| R1-04 | CLOSED | Abstract, Conclusions; Results ablation paragraph; Discussion opening paragraph | The central wording now attributes the observation to the complete “polarity-sensitive non-merge condition,” not independently estimated effects of polarity and terminal design. The manuscript reports the grouped ablation and force-compatibility results without claiming separable component effects, and expressly disclaims the independent value of every coordinate. |
| R1-05 | PARTIAL | Data and software availability; target-criteria.json, unresolved human filing inputs | The exact public repository snapshot, commit, artifact paths, licences, and absence of an asserted DOI are clearly disclosed. A persistent archive identifier is still not supplied, but the manuscript preserves the bounded note that one may be added after deposit and does not falsely imply that one exists. This remains a human filing/preservation item rather than a scientific or technical blocker. |

## Independent atomic coverage check

| Atomic claim or boundary | Evidence pointer | Coverage assessment |
|---|---|---|
| Development and confirmatory panels each contain 32 cases | Methods §2.2; Results opening paragraph | Covered |
| Holdout case identifiers are development-disjoint, with two recurring locator/hash combinations | Methods §2.2 | Covered as an explicit design statement and limitation |
| Holdout freezing preceded inspection of outputs | Methods §2.2 | Covered as a protocol statement |
| Scientific breadth is three authored families, not 32 independent generalization units | Introduction; Methods §2.2 | Covered |
| Holdout coordinate-governed result is 0 false merges and 0 false splits | Table 2 | Covered |
| Flat comparator made 6/32 false merges | Abstract; Table 2; Results | Covered and arithmetically consistent |
| False-merge difference is −0.1875 with diagnostic [−0.34375, −0.0625] | Abstract; Methods §2.3; Table 2 | Covered and consistently described as a fixed-panel diagnostic |
| Conservative comparison has zero false-split difference and six abstentions | Table 2 | Covered; the scoring taxonomy is now explicit |
| All six discriminating errors were polarity contrasts | Abstract; Results | Covered as the observed panel result |
| The other two families, comprising 19 cases, did not discriminate the rules | Abstract; Results; Methods §2.2 family counts | Covered and internally consistent |
| Development results are not pooled with the holdout | Results opening paragraph; Methods §2.3 | Covered |
| Four coordinate-ablation cells were null | Results | Preserved |
| Null ablations mean absent comparison opportunity, not dispensability | Results | Preserved without overclaim |
| The weak comparator is intentionally weak and not a contemporary deployed system | Methods §2.3; Discussion | Covered |
| The 400 conformance rows instantiate only eight unique candidate-visible states | Abstract; Methods §2.4; Results | Covered |
| Complete/strong/canonical/typed scores are 400/250/50/400 | Abstract; Results | Covered |
| The strong product has a narrower interface and terminal alphabet | Methods §2.4; Discussion | Preserved as an adverse comparator limitation |
| The four-way and holdout alphabets have an explicit many-to-one crosswalk | Methods §2.4 | Covered |
| Information-equivalent typed implementation must tie the complete rule | Methods §2.4; Results | Covered without treating the tie as independent scientific evidence |
| Independent scorer shares custody and is not external replication | Results | Preserved |
| Same-programme gold and partial source overlap limit independence | Methods §2.2; Discussion | Preserved |
| No population rates, deployed-system superiority, raw-text performance, independent coordinate value, or downstream utility are established | Abstract; Discussion | Covered repeatedly and consistently |
| Data and software point to a pinned repository commit and named artifacts | Data and software availability | Covered |
| No repository DOI is currently asserted | Data and software availability | Preserved explicitly |

No contradiction, new overclaim, lost null result, lost adverse result, inflated scientific-unit count, or material atomic-coverage gap was identified. The result remains limited to the frozen authored panels and deterministic contract states.

## New Major Concerns

None identified from the supplied material.

## New Minor Comments

None identified from the supplied material.

## Blocking technical failings

None identified from the supplied material. The two prior blocking specification failings, R1-01 and R1-02, are closed.

## Assessment against target criteria

| Target criterion | Targeted assessment |
|---|---|
| Brief Report scope and article-type fit | The manuscript remains a concise report of a bounded fixed-panel methods observation with the expected Introduction, Methods, Results, and Discussion structure. |
| Technical soundness and bounded inference | Reported arithmetic, denominators, scientific units, diagnostics, comparator limitations, and inference boundaries are internally coherent. |
| Methods transparency and reproducibility | The normative precedence table, equality and missingness rules, scoring taxonomy, comparator definitions, conformance crosswalk, and pinned artifact locations now address the prior reproducibility defects. |
| Underlying-data accessibility | A commit-specific public snapshot and exact artifact paths are stated. Persistent archival identification remains an explicitly bounded filing item. |
| Literature-context adequacy | The contribution is situated relative to extraction, ontology matching, alignment repair, provenance, and interoperability work without claiming a new general ontology or extraction method. |
| Readability and evaluability | Terminal vocabularies, precedence, crosswalk, scientific units, and limitations are now sufficiently clear for evaluating the reported observation. |
| Required declarations and policy compliance | Data/software, ethics, contributions, competing interests, funding, licensing, and AI-use statements are present. Remaining human filing inputs in the criteria card are not scientific defects. |

## Recommendation posture

All prior scientific and technical specification concerns are closed except the bounded persistent-archive note, which remains a non-scientific filing item. No new blocking concern is identified, and no new experiment is warranted. The manuscript should preserve its present null results, adverse comparator qualifications, authored-panel and source-overlap limitations, non-independence disclosures, and explicit restrictions on population, deployment, extraction, component-value, and downstream-utility inference.