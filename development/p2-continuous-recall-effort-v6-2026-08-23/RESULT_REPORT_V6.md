# P2 V6: outcome-unopened continuous recall--effort source freeze

**Exact terminal**

`P2_KIFMS_V6_LAWFUL_EXACT_SOURCE_AND_LABEL_BLIND_DISJOINT_POPULATION_FROZEN__INDEPENDENT_PROTECTED_EXECUTION_CANNOT_CHECK`

## What is new

V6 does not rerun SWIFT or SYNERGY and does not reinterpret their adverse
results.  It binds a different public family: **Medical Guidelines Dutch
Association Medical Specialists**, OSF node `vt3n4`.  The source comprises all
14 revision-one CSV files exposed by the node.  OSF declares **CC-By
Attribution 4.0 International** under licence identity
`563c1cf88c5e4a3877f9e96a`.  Each CSV is bound by OSF file id, file GUID,
revision-one API URL, byte count and SHA-256.  The companion public adapter
documentation is pinned at `asreview/paper-guidelines-KIFMS` commit
`e056573791bfbdd339fa5ffd628a6443fdf220fb`.

This answers the source question in two layers:

- **Yes:** a lawful public source-body and exact file-level execution interface
  were found.
- **No:** a confirmatory execution is not yet ready, because no independent
  protected custodian has signed the source/protocol/runner, and the selected
  `expert_inclusion` semantics and both-class existence remain unopened.

No KIFMS label value, class count, seed, ranking, candidate score or comparator
score was opened in this packet.

The companion repository does contain public historical ASReview simulation
artifact paths for the same named datasets.  Their metric contents were not
opened here.  Thus “outcome-unopened” means the exact V6 labels, arm rankings
and endpoints were not inspected by this design packet; it does **not** mean
that the family is globally unstudied or historically outcome-sealed.

## Label-blind population result

Only `key`, `title`, `abstract` and `pubmed_id` were used.  The three outcome
columns were checked by header name only.  Content identity is
SHA-256(case-sensitive whitespace-normalized title, one ASCII space, abstract).
Rows were also matched by normalized PubMed identifier.  Empty rows and
within-review duplicates were removed; then every row matching raw SWIFT/V5
content or PMID and every identity shared by two KIFMS reviews was removed
symmetrically.

| Review unit | Raw | Final canonical |
|---|---:|---:|
| Distal radius fractures: approach | 195 | 186 |
| Distal radius fractures: closed reduction | 277 | 269 |
| Hallux valgus: prognostic | 640 | 640 |
| Head and neck cancer: bone | 311 | 306 |
| Head and neck cancer: imaging | 56 | 52 |
| Obstetric emergency training | 188 | 163 |
| Post-intensive-care treatment | 435 | 433 |
| Pregnancy medication | 428 | 427 |
| Shoulder replacement: diagnostic | 342 | 335 |
| Shoulder replacement: surgery | 397 | 391 |
| Shoulder dystocia: positioning | 218 | 181 |
| Shoulder dystocia: recurrence | 335 | 300 |
| Total knee replacement | 480 | 479 |
| Vascular access | 772 | 772 |
| **Total** | **5,074** | **4,934** |

The preflight found one real adverse overlap: one provisional
`Shoulderdystocia_recurrence` row matched a V5 raw-work content identity.  It
was excluded before outcomes.  It also found 65 identities shared within the
new family, affecting 132 rows; all were excluded from every owning review.
The final population has zero content matches to SWIFT and zero to V5.
Although `pubmed_id` is a declared column, all 5,074 KIFMS values are empty;
therefore zero PMID matches are **vacuous** rather than a second corroborating
channel.  Content identity is the operative disjointness test.
The canonical union hashes are:

- content: `731d87e66b3e1195826c82e0a94fef19c044d63503ba2a36e41d38f811df0b12`
- empty PMID set: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

These receipts establish source/population identity, not class validity,
independence or performance.

## Frozen continuous estimand

For a complete arm ranking (i=1,\ldots,N_r), binary hidden labels (y_i), and
(P_r=\sum_i y_i), V6 freezes

\[
\operatorname{CRE20}_r =
\frac{1}{0.20 P_r}\sum_{i=1}^{N_r}
y_i\max\left(0.20-\frac{i}{N_r},0\right).
\]

This is the normalized integral of the full-ranking recall--effort step
function over the first 20% screened.  It replaces retrospective interpretation
of the V5 R@5/R@20 tail by one prospectively fixed, rank-continuous functional.
R@10 remains a coprimary endpoint with its V5 magnitude threshold
`0.010858985820770889` and 80% sign rule (12 of 14 here).  CRE20 receives the
same magnitude and sign rules.  Both must pass; neither compensates the other.

The four V5 factorial cells, active `R1_L1` u4 comparator, deterministic
class-seed rule, batch cadence, full ordering, unweighted review aggregation,
learner WSS@95 gate, learner harm gate, full candidate-minus-u4 R@10/WSS@95
gates, worst-review harm gate and candidate absolute-work-saving gate are all
unchanged.  Row pooling, review deletion, post-result tuning and endpoint
substitution are forbidden.

## Negative and unresolved evidence retained

1. V5 remains adverse: learner R@10 was `+0.008834277869043594`, strictly
   positive in 3/5 and zero in 2/5; candidate-minus-u4 R@10 and WSS@95 remained
   negative.
2. A tempting CSMeD computer-science review source was rejected because its
   loader declares the constituent dataset licence `Unknown`.
3. CLEF TAR was not selected: it requires a separate task/finite-population and
   PubMed binding, and the inspected public task documentation already contains
   aggregate test-example outputs.  This is not a claim that CLEF is unusable.
4. The OSF project is mutable rather than a registered OSF registration.  V6
   therefore claims only exact file-revision identity, not immutable-node
   custody.
5. Public documentation names `expert_inclusion` but does not independently
   prove its construct semantics or that both classes occur in every frozen
   review.
6. Independent custody, execution, performance, harm, work saving and
   superiority all remain `CANNOT_CHECK`.
7. The missing PMID values prevent identifier-channel corroboration; final
   disjointness rests on normalized title/abstract content hashes.
8. Prior public ASReview simulation artifacts prevent a claim that the source
   family is globally unstudied, even though no exact V6 metric was opened.

## Next discriminator

An external custodian must re-download and verify the 14 revision-one files,
reproduce the 4,934-row hashes, sign a frozen runner/dependency/container and
protected evaluator, establish the `expert_inclusion` mapping and both-class
existence, and then run every one of the four arms to a complete order.  Only a
conjunction of every binding, CRE20, R@10, work-saving and harm gate can issue
the narrow exact-family positive terminal.  Otherwise the adverse or
`CANNOT_CHECK` terminal is mandatory.

## Reproduction boundary

`capture_kifms_source_metadata_v6.py` refreshes metadata only.
`run_label_blind_overlap_preflight_v6.py` reproduces the label-blind population
receipt when supplied the exact public KIFMS, SWIFT and V5 source bodies.  Large
source bodies are not redistributed in this packet.  `validate_p2_v6_packet.py`
checks packet integrity without opening outcomes or running repository tests.
