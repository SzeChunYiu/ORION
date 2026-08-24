# Outcome-blind case construction rules

**Protocol:** `P3.PUBLIC.TRANSPORT.CRAFT_SCIREX_OAEI.V1`
**Status:** frozen construction contract; no source body or gold opened during
design
**Authority:** public transport only

## Common rule

The case builder and sampler may use raw inputs, provider split, source-native
type vocabularies and independently generated candidate scores. They may not
use public reference labels, annotation counts, candidate correctness or any
system output to decide which units or pairs enter the audit panel.

Each output case must satisfy `CASE_CONTRACT_V1.schema.json`. Public gold is
materialized later by a different invocation into
`PUBLIC_GOLD_CONTRACT_V1.schema.json`. The case `input_digest` is frozen before
the gold join.

## CRAFT evaluation panel

### Independent unit

One PMC article document. Mentions, token spans, concepts and coreference links
within an article are not independent units.

### Input side

Use only `craft-st-2019-2019_test_data.tar.gz`:

- the provider's 30 evaluation plain-text documents;
- provider-supplied ontologies and concept metadata;
- provider-supplied tokens required for coreference evaluation.

The census is determined from PMC identifiers in the input archive before the
evaluation-gold archive is opened.

### Candidate generation

Freeze one extractor or matcher revision before gold access. It may propose:

1. mention-to-ontology candidates using surface form and ontology labels;
2. within-document coreference candidates using text and frozen model scores;
3. cross-projection pairs created from candidate outputs, not gold concepts or
   gold chains.

Candidate blocking thresholds, maximum candidates per mention and tie rules
must be written to the execution manifest. Every retained candidate is scored;
no error-enriched subset is selected.

### Evaluator side

Only after outputs freeze, open `evaluation-data.tar.gz` and map reference
concept/coreference annotations to the common relation. Public labels remain
`CRAFT_PUBLIC_GOLD`, `protected_evidence=false`. Cases whose source-native gold
does not answer the P3 relation are `CANNOT_CHECK`, not negatives.

## SciREX official-test transport panel

### Rights gate

Do not download or parse `release_data.tar.gz` until a rights owner records a
content-class decision for the underlying article text. The Apache-2.0
repository licence is bound, but this packet does not infer that it settles
every embedded publication-text byte.

### Independent unit

One Semantic Scholar paper document (`doc_id`). Entity mentions, clusters,
n-ary relations and metric cells inside a paper are not independent.

### Input side and sampling

Honor the provider's official split. The public audit panel is a census of
`test.jsonl`; train/dev are development only. The sampler retains only
`doc_id`, official split, revision and rights status. Because annotations are
inline, this is procedural outcome blindness, not external custody.

### Candidate generation

Freeze a raw-text extractor before test labels are joined. It must emit
Method, Metric, Task, Material and Score mentions/clusters and candidate n-ary
relations. The official SciREX model at commit `7daad660…` is a lawful donor
candidate after its environment is reproduced, but it is not silently treated
as the P3 candidate or as a common portrait terminal.

### Missing-mention stratum

The pinned README states that approximately half of relations contain an
entity with no retained mention because tables were discarded. Preserve these
as an adverse partial-observation stratum:

- do not remove them from the portrait-coverage endpoint merely because the
  official end-to-end evaluator removes them;
- distinguish `NOT_OBSERVED_IN_RELEASED_TEXT` from a predicted negative; and
- require `identified_relations` from an independent source-aware evaluator
  before computing floor-adjusted harm.

No paper count or effect is quoted until the rights-gated archive is executed.

## OAEI 2004 stress panel

### Independent unit

The entire benchmark is one bibliographic seed family. Numbered tests are
systematic alterations, not independent natural observations.

### Input side

Inventory numbered directories containing `onto.rdf`. Do not open
`refalign.rdf` during candidate generation. Use test 101/the provider seed and
each altered ontology as the alignment input specified by the benchmark
documentation.

### Candidate generation

Enumerate entity candidates outcome-blind from labels, identifiers and local
ontology structure. Freeze blocking and score thresholds before reference
alignments are joined. The stress census may diagnose sensitivity to removed
labels, hierarchy, instances or other systematic representation changes, but
it contributes one cluster to any uncertainty calculation.

### Evaluator side

After outputs freeze, join `refalign.rdf` and label it
`OAEI_PUBLIC_REFERENCE`, `protected_evidence=false`. Reference pairs not
expressible in the P3 relation schema are `CANNOT_CHECK`.

## Coordinate opportunity audit

Before scoring any claim, an evaluator who has not seen system identities must
return denominators for:

- referent opportunities;
- construct opportunities;
- measurement opportunities;
- temporal-context opportunities;
- non-singleton identified sets; and
- valid-glue and invalid-glue opportunities.

The evaluator may return counts and exclusions only before prediction freeze.
For each coordinate, ``opportunity'' means that the coordinate differs between
the two registered members of a case; atlas-wide variation between unrelated
cases does not count. The evaluator must also return the joint binary contrast
pattern over all four coordinates so that a coordinate-specific claim cannot
silently rely on several coordinates moving together. Zero within-case
opportunity blocks that coordinate claim. Nonzero opportunity permits scoring
but does not itself identify a causal coordinate effect. This packet expects temporal
context to remain `CANNOT_CHECK`; it may not be manufactured from publication
dates or benchmark test numbers.

## Required execution custody

At minimum, record distinct roles even if public data prevent true secrecy:

1. rights owner;
2. input/case builder;
3. candidate and comparator runner;
4. public-gold joiner/evaluator; and
5. result verifier.

Same-machine role separation is procedural, not independent external custody.
The final receipt must state the actual custody achieved.
