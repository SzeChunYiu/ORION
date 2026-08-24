# Paper 3 public-data successor: independent adversarial readiness audit

**Audit date:** 2026-08-23  
**Reviewed packet:** `development/p3-public-data-successor-2026-08-23/`  
**Review authority:** mechanics and scientific-readiness audit only  
**Execution boundary:** no manuscript or shared-ledger edits; no pytest or CI;
no public gold content opened; no empirical candidate output generated.

## Executive verdict

**Terminal:**
`ADVERSARIAL_AUDIT_FAIL__OAEI_INPUT_INDEX_REPLAY_ONLY__NO_END_TO_END_PUBLIC_RESULT`

The packet is unusually explicit about public-gold, rights, clustering and
four-coordinate limits. Those declarations should be retained. However, it is
**not ready for an empirical comparative run**. The only public-source
component that can be executed now without inflating evidence is OAEI's
input-only archive inventory and deterministic census serialization. That path
replayed byte-identically. No donor-specific source-to-case builder, P3
candidate, source-native terminal adapter, protected/public-gold custody
binding, or fair comparative estimator is executable end to end.

The failure is scientific rather than cosmetic. The current scorer collapses
`PLURAL` and `UNRESOLVED` into a binary glue/non-glue loss, accepts invalid
prediction relations, trusts system-supplied cluster IDs, accepts duplicate
system/case rows, and announces floor-adjusted decisions without enforcing
coordinate-opportunity gates. A public result produced through it would not
measure the epistemic portrait-envelope object defined by Paper 3.

## Preserved strengths and boundaries

1. Public gold is consistently declared non-protected; this packet does not
   rename it as independent confirmation.
2. OAEI numbered tests are correctly treated as one bibliographic seed-family
   cluster, not 21 independent natural units.
3. SciREX article-text rights are explicitly unresolved, and temporal-context
   opportunity is explicitly `CANNOT_CHECK`.
4. The protocol preserves the A004 adverse result and does not relabel this
   public successor as the frozen 768-cluster study.
5. The packet already forbids a broad superiority claim until a strongest
   source-native comparator is bound. That guard is correct and must remain.
6. Every source-packet SHA-256 entry verified before this audit.

## Severity-ranked blockers

### C1 — Critical: the score does not implement Paper 3's four-terminal semantics

`point_loss` treats every action other than `GLUE` and `UNRESOLVED` as
separation. Consequently `PLURAL` is scored as if it were `OBSTRUCTION`, and
an arbitrary invalid string is scored the same way. The robust floor optimizes
only over `GLUE`, `OBSTRUCTION`, and `UNRESOLVED`, even though both prediction
and gold contracts admit `PLURAL`.

The adversarial probe was accepted and showed that predicting `OBSTRUCTION`
on a `PLURAL` truth incurs zero excess harm in every declared loss regime.
This directly contradicts the manuscript's distinction between a legitimate
plural view and an obstruction. Until a fully declared action-by-state loss
matrix covers all four terminals, floor-adjusted harm is scientifically
undefined for the advertised interface.

**Required repair:** freeze a four-state decision contract before public
outcomes: define whether `PLURAL` is a state, an action, or set-valued output;
define loss for every action/state pair; validate relations; and prove that
`identified_relations`, admissible prediction sets, and the minimax floor all
use the same semantics.

### C2 — Critical: outcome and unit bindings are not integrity-preserving

Three independently executed probes passed when they should have failed:

- `sample` copied `gold_relation`, `gold_annotation_count`,
  `candidate_output`, and `effect_size` from an inventory row while emitting
  `gold_fields_used: []` and `selected_without_outcomes: true`.
- `seal-cases` accepted `gold_relation`, `annotation_count`, and nested
  evaluator gold because it rejects only three exact top-level keys. The case
  schema also permits arbitrary additional properties.
- `score-public` accepted duplicate `system_id`/`case_id` rows, an invalid
  relation `BANANA`, arbitrary input digests, fake source IDs, and three
  prediction-supplied cluster IDs for two gold rows whose authoritative gold
  cluster was one. It then reported `n_cases=3`, `n_clusters=3`.

Thus case selection, outcome separation and cluster weighting are declarations,
not enforced data lineage. A system can change its statistical weight or
import public labels without tripping the adapter.

**Required repair:** closed schemas at every stage; recursive forbidden-field
checks; source-archive/member digests; a signed case manifest; prediction
uniqueness on `(system_id, case_id)`; exact prediction coverage; immutable
input-digest lookup; and cluster/source/panel identity taken only from the
sealed case/gold authority, never from a prediction.

### C3 — Critical: no donor produces executable P3 cases or a candidate output

The adapter downloads, inventories, serializes, seals already-built cases,
runs four generic functions, and scores manually supplied gold. It never
converts CRAFT text/ontology/coreference inputs, SciREX documents, or OAEI
ontologies into `CASE_CONTRACT_V1`. It also implements no
`P3_EPISTEMIC_ENVELOPE_CANDIDATE` and no independent identified-relations
builder. Therefore the advertised public scientific question cannot currently
be executed.

**Required repair:** implement and freeze one donor at a time. Each builder
must specify its candidate universe, negative opportunities, blocking recall,
source-native terminal mapping, coordinate extraction, provenance, and input
member digests without accessing evaluator gold.

### H1 — High: protocol gates are stated but not enforced

The scorer does not ingest or validate:

- nonzero opportunity for a claimed coordinate;
- a declared envelope-coverage threshold;
- source-native external-comparator binding;
- panel/source-family stratification;
- raw-text stage attribution; or
- the prohibition on a pooled cross-donor pass.

`coordinate_opportunities` is optional and unconstrained in the gold schema.
The adversarial scoring fixture omitted it entirely, yet the scorer returned
`floor_adjusted_status: DECIDED_DESCRIPTIVELY`. Zero denominators merely yield
`null`; they do not force a blocking terminal.

**Required repair:** make every gate machine-required and noncompensatory.
Emit one terminal per donor family and claimed coordinate. A missing or zero
opportunity must stop that claim before system scoring.

### H2 — High: comparator and action-set fairness is not established

The four runnable arms are intentionally weak label/type/complete-case rules.
No source-native external system is bound. The candidate may emit `PLURAL` and
arbitrary admissible sets; the generic comparators do not receive a matched
four-action contract or a matched calibrated set-construction mechanism.
`TYPE_AWARE_PAIRWISE_V1` and `COMPLETE_CASE_CONSERVATIVE_V1` also receive
information defined by host-authored cases rather than demonstrably equivalent
source-native sufficient statistics.

**Required repair:** for each donor, bind the strongest runnable source-native
comparator at an exact revision and map all systems onto the same frozen action
space, candidate universe, input information, abstention budget, and coverage
constraint. Report a candidate-minus-comparator cluster-level contrast, not
only per-system descriptive rates.

### H3 — High: rights acknowledgement and byte verification are incomplete

The rights registry honestly records the principal cautions, but the executable
gates are not authority receipts:

- `--ack-scirex-content-rights` is a boolean with no rights-owner identity,
  rationale, scope, timestamp, or licence evidence. The SciREX body has no
  expected checksum, yet a successful download is labelled
  `DOWNLOADED_AND_VERIFIED`.
- `--ack-craft-terms` likewise does not record who accepted which terms, and
  the acquisition receipt does not bind the attribution/share-alike delivery
  plan or per-article notices.
- OAEI packages inputs and public references in one archive. The input-only
  inventory can avoid reading reference content, but this is same-container
  procedural separation, not protected custody.

**Required repair:** obtain a human-owned rights decision outside the adapter;
record identity, scope, evidence and permitted transformations; hash every
acquired body; quarantine evaluator-only members under a separate role; and
carry licence/attribution obligations into derived-case manifests.

### H4 — High: inference and comparison are absent

The scorer produces descriptive per-system means and no paired contrasts,
uncertainty intervals, multiplicity logic, missing-cluster policy, or donor-
family interaction. OAEI supplies one independent seed family, so it cannot by
itself support a sampling interval or broad generalization. Pooling its rows
with CRAFT/SciREX documents would not create independent OAEI replication.

**Required repair:** freeze donor-specific estimands and cluster-level paired
contrasts. Treat OAEI 2004 as one descriptive perturbation trajectory; obtain
additional independent ontology families before any family-level inference.

### B1 — Blocking boundary: temporal context remains absent

No bound donor supplies natural temporal-context mapping opportunities. The
protocol is correct to say `CANNOT_CHECK`. Publication dates and OAEI test
numbers must not be repurposed as temporal scientific context. This public
panel can never promote the frozen four-coordinate/768-cluster claim unless a
new lawful temporal donor and nonzero opportunity audit are added.

### B2 — Blocking boundary: SciREX is intrinsically public-inline

The SciREX inventory function parses each full JSON line to read `doc_id`, so
public inline annotations are present in the same process before prediction
freeze. A test-split census avoids outcome-conditioned sampling but does not
create outcome secrecy; the corpus is public and historically visible. A
separate custodian can reduce accidental leakage, but the result must remain a
public development/transport study, never protected confirmation.

## What is safely executable now

### Executed in this audit

1. Source packet SHA-256 verification: all entries passed.
2. OAEI input-only `inventory` followed by deterministic `sample`, using the
   already provider-MD5-verified archive. Both outputs were byte-identical to
   the packet's frozen files:
   - inventory SHA-256 `ef0d7100bcba19d934f2c05cc4fe7a547a87f6d4cd51c505a933adc598bb9dab`;
   - sample SHA-256 `3db4e32d6d3f7b04a2825e543d7f3d19ad0e19e9eb4c08b40e32d0e70cc8ef62`.
3. Synthetic adversarial mechanics probes. These are not source data or
   scientific outputs.

No `refalign.rdf` content, CRAFT archive, SciREX data body, or public gold row
was opened by this audit.

### Runnable but non-empirical

- metadata refresh;
- rights-conditioned download after a human rights decision;
- input inventory and deterministic census serialization;
- case sealing and generic comparator mechanics on an independently built,
  gold-free synthetic case file.

### Not runnable as a public scientific result

- source package to P3 case construction;
- the P3 envelope candidate;
- independent identified-set construction;
- strongest source-native comparators;
- valid four-terminal scoring;
- coordinate-gated, donor-stratified comparative inference; and
- any protected or frozen-768-cluster endpoint.

## Highest-leverage scientific successor

Do not pool all three donors prematurely. Close one complete, fair public lane
first: **OAEI input-only ontology-perturbation transport as a descriptive
mechanism falsifier**, while preserving the one-family limit.

### Unit and sampling

- unit for uncertainty: one bibliographic seed family (there is only one now);
- descriptive subunits: all 21 numbered perturbation directories;
- no confidence interval or population generality from those 21 directories;
- acquire multiple disjoint OAEI seed families or other independently authored
  ontology families before inferential promotion.

### Required arms

1. frozen P3 set-valued envelope candidate;
2. flat label equality;
3. forced token similarity;
4. complete-case conservative abstention;
5. at least one exact-revision, maintained source-native ontology matcher; and
6. an information-equivalent ideal product required to tie when given the same
   coordinates and authority rules.

All arms must receive the same ontology pair, candidate correspondence
universe, permissible external resources, four-terminal action set and
abstention/coverage rules. Gold reference alignments remain evaluator-only
until every output digest is frozen.

### Endpoints

- primary descriptive contrast: candidate-minus-strongest-source-native
  floor-adjusted harm under a valid four-terminal loss table;
- hard gates: gold-in-envelope coverage, nonzero opportunity, candidate-universe
  recall, exact output coverage, and no duplicate rows;
- adverse endpoints: false integration, false obstruction, loss of legitimate
  plurality, unjustified point resolution, unresolved rate, and perturbation-
  stage sensitivity;
- no temporal-coordinate endpoint.

### Falsifiers

The OAEI mechanism claim is negative if any of the following occurs:

1. the candidate's envelope excludes public reference relations beyond the
   frozen tolerance;
2. it fails against the strongest source-native comparator in any declared
   noncompensatory endpoint;
3. apparent benefit disappears under matched actions/information;
4. the candidate universe omits a material fraction of reference pairs;
5. the information-equivalent ideal product does not tie; or
6. sensitivity is driven only by a hand-authored host coordinate unavailable
   from the raw ontology inputs.

### Promotion boundary

Even a positive OAEI result would support only a named, public, one-seed-family
ontology perturbation mechanism. It would not establish raw-text scientific
integration, natural prevalence, temporal-context handling, multi-domain
validity, protected confirmation, or completion of
`P3.PARTIAL_IDENTIFICATION.EXCESS_HARM.V1`.

After that lane is valid, CRAFT should be a separate raw-text/coreference lane
with its own rights custody and source-native comparators. SciREX should remain
blocked until article-text rights are resolved and the official model is
reproduced through a terminal-preserving adapter. A truly upward result still
requires independent natural temporal-context sources and protected evaluator
custody.

## Artifact map

- `ADVERSARIAL_EXECUTION_RECEIPT_V1.json` — replay and probe outcomes.
- `BLOCKER_LEDGER_V1.json` — machine-readable blockers and promotion boundary.
- `fixtures/` — synthetic adversarial inputs only.
- `outputs/` — synthetic mechanics outputs and OAEI input-index replay only.
- `SHA256SUMS` — audit artifact integrity.
