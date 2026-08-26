# Paper 3 V15--V21 hostile Nature Machine Intelligence Article review

**Date:** 2026-08-24  
**Review status:** Internal simulated hostile pre-submission review; not peer
review, not an editorial decision and not external authority  
**Target:** *Nature Machine Intelligence* (NMI), Article, initial submission  
**Target-source boundary:** Exact local NMI profile from public pages verified
2026-08-14; submission-critical requirements should be refreshed before an
actual upload  
**Independence boundary:** The three reports below are same-context reviewer
lenses, not mutually blind or independent reviews. No external-review or
custody claim is made.

## Review setup and evidence inspected

- Current Paper 3 manuscript source, theory claim ledger and V15--V21 sections.
- V15--V21 packet manifests. Every entry in every `SHA256SUMS` verified on
  2026-08-24 with `shasum -a 256 -c`; no pytest or repository CI result is used
  as publication authority. The manifest-file SHA-256 digests are V15
  `1dd1e8234c19e4e53dec4b96d5ecfa05473300a7e44e077dd8de92cc5d5da558`, V16
  `8c37aceda665a235088ffa62b0b0c9e718fe75c174184779ea3eeb635461fd96`, V17
  `c1d8bf3c9103b3eb39d15e49b0352552c4c2dcabb21ba8192ad8135c9d38d8ed`, V18
  `eaa0e352a2c4dd6774055e5b5cdd8edf81c55671924cf3f98fb884f016babedd`, V19
  `46792f76e285a9161950c89fc944b4c37e453c395de7d7ec466549a4b9783168`, V20
  `07e4965600e683e90546cb8b53442f7c9927c2e5fce69db2a59c4e5d2e0ec1ff` and V21
  `c6b888f1bdd54baa8eaddc3d9c0f29f4427836096cc9dd79a849e4f82f763baa`.
- V21 scientific report and exact metrics receipt. The analysis unit is one
  public OAEI 2004 test-103 case. Pair cells are not independent samples.
- A fresh temporary Tectonic build. It produced a 46-page PDF with no undefined
  reference, undefined citation, overfull box or fatal-error diagnostic. The
  log retains one undefined small-caps-italic font-shape substitution and two
  underfull boxes. Pages 1, 30--31, 36, 38--39 and 43--44 were visually
  inspected; no clipping, overlap, broken table or unreadable glyph was found.

The build was written only to `/tmp/p3-nmi-v21-build-20260824/`. No tracked PDF
or journal-package manifest was modified.

## Target criteria card

| Criterion | NMI Article requirement used for this stress test | Current Paper 3 readout |
|---|---|---|
| Scientific scope | Substantial original AI/ML research with a complex, well-supported story and intelligible consequence beyond a narrow benchmark community | The formal programme is broad, but the new comparator evidence is one historical ontology-alignment case; the naturalistic, downstream and multi-family bridges remain prospective |
| Abstract | At most 150 words, unreferenced | **Pass: 140 words** by LaTeX-to-plain-text conversion |
| Main text | At most 3,500 words, excluding abstract, Methods, references and legends | **Fail: roughly 14.5k words**. A conservative core-file audit gives 14,447 words after removing table environments and excluding the abstract, availability, references and the files most plausibly assignable to Methods; the exact count depends on the final Methods allocation, but the manuscript is already more than four times the allowance |
| Displays | At most six figures and tables combined | **Pass mechanically: 2/6** (two tables, no figures) |
| References | Typically at most 50 | **Pass mechanically: 33/50** bibliography entries |
| Article sequence | Unheaded Introduction, Results, Discussion, Methods | **Fail:** explicit Introduction plus Related work, Method, theory, dataset, Evaluation, post-saturation, Results, Limitations, Conclusion and availability sections; no conventional Discussion |
| Availability | Separate Data availability and Code availability; central data/code reviewable; precise access route and restrictions | Headings are now separate, but there is no public archive URL, archive DOI, immutable submission commit or verified repository-level licence; reviewer access to the exact snapshot is still required |

Mechanical format passes do not establish scientific priority or review
readiness.

## Editorial triage simulation

**Posture:** `scope_or_article_type_mismatch` together with
`central_case_requires_new_decisive_evidence`.

The revised abstract now obeys the NMI limit without increasing claim strength,
and the V21 table reports its unit and non-inferential boundary correctly. Those
are real improvements. They do not solve editorial triage. The submitted object
would ask an editor to evaluate roughly four NMI Articles' worth of theory,
development chronology, failure preservation and evidence while the newest
external comparator contrast has one analysis unit. The paper also lacks the
expected Article architecture and a reviewable immutable release.

The current evidence can support a bounded theory-and-mapping manuscript. It
does not yet support the broader NMI-level implication that epistemic portrait
envelopes improve scientific knowledge integration across systems, source
families or domains. Sending this version to NMI would make the length,
structure and evidence-class gaps visible before reviewers reach the formal
contribution.

## Reviewer 1: validity and statistics

### Major concerns

#### R1-M1. The positive comparator result has one independent unit

**Blocking:** Yes for population, transport or general-superiority claims.  
**Claim pointer:** Abstract; Results, V15--V21; Limitations, V21; Conclusion.  
**Evidence pointer:** `COMMON_PAIR_METRICS_V21.json` and
`SCIENTIFIC_REPORT_V21.md`.

BERTMap recovers 33/33 common class pairs versus AML's 8/33 on test 103. The
full-task F1 values are `33/62` and `16/137`. These are exact finite-case
descriptions, not independent replications. The 33 class-pair cells cannot be
used as `n=33`; the analysis unit is the single ontology-pair case (`n=1`). No
confidence interval, p value or population estimand is warranted.

**Resolution test:** Freeze and execute V22 across source-disjoint cases from
multiple provider or track families and multiple ontology domains. Analyse at
the case or independently governed family level, retain both the common-class
and full-task estimands, use independent custody, and report worst-case as well
as aggregate gates.

#### R1-M2. The primary opportunity estimand does not cover properties

**Blocking:** Yes for a complete ontology-matching or broad scientific-
integration claim.  
**Evidence:** BERTMap leaves 58 reference property correspondences unmatched;
its full-task recall is `33/91`, not one.

The common-class estimand is useful and fair for the opportunity shared by both
systems, but it cannot stand alone as complete task performance. The manuscript
correctly keeps the full-task estimand visible. Any headline that turns the
class-only F1 of one into complete alignment would be false.

**Resolution test:** Preserve the dual-estimand design in V22 and add a
property-capable current comparator or a prospectively frozen property-mapping
component where the interface permits. A result remains bounded if the
property gap persists.

#### R1-M3. The 32-case and constructed-corpus results do not close naturalistic validity

**Blocking:** Yes for end-to-end scientific integration.  
**Evidence:** The confirmatory 32-case public-reference result concerns
host-constructed structured projections. The exact 27/36 ceiling is on a
constructed source-record corpus.

Both results are legitimate within their declared designs. Neither measures
raw-text coordinate extraction, naturalistic envelope misspecification,
expert agreement, downstream decision gains or prevalence across scientific
domains.

**Resolution test:** Pair V22 with an independently curated naturalistic panel
that measures extraction, envelope coverage and downstream harm at source-
cluster level. Do not pool constructed cases with naturalistic cases or rename
exact-contract conformance as external effectiveness.

### Minor comments

- Keep `n=1`, the non-independence sentence and the no-CI/no-p-value sentence in
  the V21 table caption even after any venue-specific rewrite.
- Keep exact fractions alongside decimal summaries; do not round the 58 false
  negatives away.
- The bootstrap interval for the separately frozen 32-case mapping result must
  remain attached only to that design, not to V21.

## Reviewer 2: novelty, priority and target fit

### Major concerns

#### R2-M1. The novelty residual is narrower than the manuscript's theoretical breadth

**Blocking:** Yes for NMI Article priority.  
**Claim pointer:** Title, theory, related work and conclusion.  
**Evidence:** Partial identification, robust decision theory, constraint
processing, ontology/schema alignment, provenance and pluralism are explicitly
donor theories. The proposed residual is a claim-relative envelope and
authority-aware decision interface.

The synthesis may be useful, but the formal apparatus alone does not show a
field-level AI advance. The strongest new comparator evidence is one historical
bibliographic case; the one-case result cannot demonstrate that the residual
changes scientific integration practice across modern systems or domains.

**Resolution test:** Before outcome access, name the nearest donor interfaces,
freeze the unique prediction made by the envelope/authority residual, and show
that prediction on the source-disjoint V22 panel with interface-fair current
comparators. Broader wording is not a substitute for this discriminator.

#### R2-M2. The paper is not shaped as an NMI Article

**Blocking:** Yes mechanically and editorially.  
**Evidence:** roughly 14.5k core main-text words versus 3,500;
explicit non-NMI section sequence; no conventional Discussion.

This is not a small copy-edit. A destructive roughly 14,500-to-3,500 compression would
either remove the evidence allocation and adverse-result record or produce an
unevaluable argument. The current source is closer to a long specialized
theory/systems paper than to the requested NMI Article.

**Resolution test:** First freeze a claim-to-evidence allocation. If V22 closes
the scientific bridge, author a new NMI main-text projection around one central
claim, one decisive empirical arc and one Discussion; move derivations,
development chronology, historical terminals and reproduction detail to
Methods/Supplementary Information without deleting them. If V22 does not close,
choose a venue and article type compatible with the bounded contribution.

### Minor comments

- The title remains broader than the one-case comparator evidence. It is
  defensible only as the name of a formal programme, not as an empirical claim
  of global integration performance.
- Two displays leave budget for an evidence-first figure, but adding a
  conceptual graphic cannot repair the missing multi-family result.

## Reviewer 3: reproducibility, availability and claim boundaries

### Major concerns

#### R3-M1. The exact submission snapshot is not publicly and legally bound

**Blocking:** Yes for review readiness.  
**Evidence:** No public archive URL, archive DOI, immutable submission commit or
verified repository-level licence is bound. The manuscript now states this
explicitly.

Packet hashes and a successful local build establish integrity of retained
bytes. They do not give editors and reviewers an access route or establish
redistribution rights for the full submission snapshot.

**Resolution test:** Freeze one immutable submission commit, verify the
repository-level licence and third-party redistribution boundaries, deposit
the reviewable release in a durable archive, record its DOI/URL, and confirm
that editors and reviewers can access every central data and code artifact.

#### R3-M2. Adverse terminals are scientifically necessary and must survive compression

**Blocking:** Yes for causal and procedural interpretability.  
**Evidence:** The chain includes the exact preserved terminals

- `P3_V17_BERTMAP_NATIVE_ATTEMPT_FAIL__NO_RETRY__COMMON_SCORING_NOT_AUTHORIZED`;
- `P3_V18_STRUCTURAL_REASONER_COMPATIBILITY_FAIL__V19_BERTMAP_NOT_AUTHORIZED`;
- `P3_V20_BERTMAP_NATIVE_PASS__TYPED_DECODER_OR_STRUCTURAL_CONTRACT_FAIL__COMMON_SCORING_NOT_AUTHORIZED`.

V21 is interpretable because it repairs a localized direct-IRI interface only
after both matcher outputs were frozen. Removing the failures would make the
successful scoring path look post-hoc or erase the reason scoring was
previously withheld.

**Resolution test:** Preserve the exact terminals and artifact identities in a
content-addressed supplement/ledger, cite that ledger from the compressed
Results, and state that V21 does not overwrite any predecessor.

### Minor comments

- The temporary PDF is legible, but the plain article-class layout is not an
  NMI submission projection and several long identifiers make the manuscript
  hard to scan.
- The abstract, V21 table, limitations, conclusion and both availability
  headings are mutually consistent in the inspected build.

## Editor synthesis (post-review; simulated)

**Decision posture:** `central_case_requires_new_decisive_evidence` and
`scope_or_article_type_mismatch`.

The V15--V21 chain is a meaningful research advance over the earlier blocked
state: it reaches a valid positive finite-case description while preserving
every failed interface and the 58-property limitation. That is not a negative
result to hide. It is the correct starting point for a wider test.

The present manuscript is not ready for NMI Article review. Four blockers are
noncompensatory:

1. one independent comparator case and no population/generalization authority;
2. incomplete task coverage for BERTMap, with 58 property false negatives;
3. a roughly 14.5k-versus-3.5k main-text and Article-structure mismatch;
4. no immutable public release, DOI/URL or verified repository-level licence.

The highest-value next scientific action is V22. Another same-case rerun,
another manuscript-only claim expansion or inferential treatment of pair cells
cannot close the central bridge.

## Minimum valid repair path

1. **Freeze V22 before opening new gold.** Use source-disjoint cases across at
   least two provider/track families and two ontology domains; fix seeds,
   thresholds, model and matcher revisions.
2. **Retain fair dual estimands.** Report the common class opportunity and full
   equivalence task, including properties, for every case.
3. **Add authority and modern comparison.** Use independent custody and a
   current stronger comparator where interfaces permit; predeclare aggregate
   and worst-case gates.
4. **Preserve all outcomes.** Keep V17, V18 and V20 exact terminals and report a
   V22 failure, null or heterogeneous result without post-outcome relabelling.
5. **Only after the evidence gate, author the NMI projection.** Allocate one
   central claim to one decisive empirical arc, move the research chronology
   and derivations to Methods/Supplementary Information, use the unheaded
   Introduction--Results--Discussion--Methods sequence, and remain within
   150/3,500/six/approximately-50 limits.
6. **Bind the release.** Archive the exact submission commit and central
   artifacts, bind DOI/URL and verified licence, and test reviewer access.

## Do not waste effort on

- treating the 33 pair cells as independent samples or manufacturing a p value;
- repeating test 103 to create pseudo-replication;
- hiding the 58 unmatched property pairs;
- deleting V17, V18 or V20 to make the route look uniformly positive;
- widening claims by prose before V22 supplies wider evidence;
- spending the scientific lane on pytest or repository CI as a substitute for
  evidence, release or reviewer access.

## Current bounded verdict

**Scientifically valuable finite-case advance; not ready for NMI Article peer
review.** The minimum bridge is V22 plus an immutable reviewable release. If
that bridge is not executed or does not meet its prospective gates, the honest
publication route is a focused specialized theory-and-mapping paper, not a
broader unsupported NMI claim.
