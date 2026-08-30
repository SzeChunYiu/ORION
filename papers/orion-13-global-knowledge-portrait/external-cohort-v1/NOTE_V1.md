# ORION-13 external corpus acquisition v1

**Terminal: `ACQUISITION_ONLY__NO_SCORING__NO_COORDINATE_CASES_CONSTRUCTED`.**
No reference alignment was opened, no MELT run, no correspondence scored.

## The problem this addresses

`manuscript/tables/coordinate_branch_census.tex` records that in both public
reference holdouts, **10 of the 11 comparison coordinates decide zero cases**.
Only `polarity` fires (6/32 confirmatory, 4/32 initial); everything else is
"no branch fired (compatible)" in 26/32 and 28/32. Because `{polarity}` is the
unique reduct, the current corpus does not test whether the other coordinates are
necessary. The successor needs a corpus in which polarity alone cannot solve the
task.

`protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json` names the target precisely:
nonzero variation is required on **REFERENT, CONSTRUCT, MEASUREMENT and
TEMPORAL_CONTEXT**, across 4 domains and 768 independent units, and its status is
`PROSPECTIVE_LOCAL_PREFLIGHT_COMPLETE__EXTERNAL_ATLAS_REQUIRED`.

## What I acquired

**bench23 (OAEI 2025 benchmark tests) — downloaded and verified.**
`gold/OAEI_TRACK_LICENSE_MANIFEST_V1.json` had this source at
`LICENSE_VERIFIED__SELECTED` but `NOT_DOWNLOADED`. It is the only licence-cleared
source in that manifest. It is now downloaded:

- DOI `10.5281/zenodo.15827289`, licence `cc-by-4.0` re-verified at fetch time
- **1,034,779 bytes** — matches the manifest exactly
- MD5 `5c70ace8a58d828de693509440eae762` — matches the published MD5
- **SHA-256 `0e23db186d856dc97cd825aef65b63d983053d268716f793e1c185736bf6dfff`**,
  computed locally

That SHA-256 discharges a standing requirement: the manifest noted the Zenodo
record publishes MD5 only, and required a locally computed SHA-256 recorded
before any scoring run.

**The payload itself is not in the repository.** The zip was fetched to
session-local scratch, verified, inspected, and deliberately not committed — it is
third-party CC-BY data, and this record commits only derived, compact evidence.
What is durable is the *identity plus integrity*: re-fetch from the DOI and check
against the SHA-256 above. Read the status as "this archive was obtained and
verified", not "this archive is in the repository".

Structure observed: 60 ontology files, 56 reference alignments **left unopened**,
seed ontology `benchmarks/104/onto.rdf` with 33 classes, 24 object properties and
39 datatype properties. This confirms the manifest's recorded limitation — the
archive is systematic alteration of **one** seed ontology in one domain, so it
cannot alone satisfy the natural-ontology-pair requirement (#1086 box 3).

## A measured result: the corpus is anti-confounded on polarity

This is the one substantive measurement here, and it is checkable. I counted OWL
negation/distinctness constructs across all 60 ontology files, with `owl:Class` as
a positive control that must match:

| construct | files |
|---|---|
| `owl:complementOf` | 2 / 60 |
| `owl:disjointWith` | 2 / 60 |
| `owl:NegativePropertyAssertion` | 0 / 60 |
| `owl:differentFrom` | 0 / 60 |
| **control `owl:Class`** | **60 / 60** |

The control matched 60/60, so the zeros are real absences and not a broken search.

Negation is absent from 58 of 60 ontologies, and alignment correspondences are
positive equivalence assertions carrying no polarity contrast. **Polarity is
therefore near-constant in this corpus and cannot be the coordinate that decides
cases** — which is exactly the anti-confounding property the successor needs, and
the property the SciFact-derived corpus lacks.

Stated at its true strength: this is a property of the source vocabulary as
measured. It is *not* a claim that any case set has been built, nor that some
other coordinate does decide.

## Coordinate coverage: what I can and cannot claim

Turning an ontology into ORION-13 probe cases requires the projection and
annotation step in `protocol/ANNOTATION_HANDBOOK_V1.md` and
`ANNOTATION_SCHEMA_V1.json`. That is human annotation work; acquisition cannot
discharge it. So every row below reports whether the acquired vocabulary **can
express** variation on a coordinate — never that a case **does** exercise it.

| coordinate | capacity in bench23 | evidence |
|---|---|---|
| referent | PRESENT | entity identity is what the systematic alterations vary |
| construct | PRESENT | 33 named classes |
| measurement | PRESENT IN VOCABULARY | 10 quantitative datatype properties (`chapter`, `edition`, `endPage`, `issue`, `number`, `numberOrVolume`, `price`, `size`, `startPage`, `volume`) |
| temporal context | PRESENT IN VOCABULARY | 5 temporal datatype properties (`day`, `month`, `year`, `firstPublished`, `periodicity`) |
| predicate | PRESENT IN VOCABULARY | 24 object properties |
| modality | ABSENT | OWL class axioms carry no epistemic modality |
| discourse relation | ABSENT | alignment has no connected prose |
| attribution | NOT ESTABLISHED | bibliographic authorship exists, but attribution of a *claim to a source* is not carried by a correspondence |
| assumption context | NOT ESTABLISHED | no assumption vocabulary observed |
| unresolved ambiguity gate | NOT ESTABLISHED | would arise in annotation, not in the source |

All four successor-required coordinates are expressible; four of the remaining six
are absent or not established.

## What I could not get

- `CANNOT_CHECK` — **a natural ontology-pair track.** Every OAEI candidate is
  blocked: Bio-ML and LargeBio are `EXCLUDED__UMLS_ASSOCIATED_UNAUTHORIZED`,
  eClass is excluded by directive, and Conference, Biodiv and SemTab are all
  `LICENSE_CANNOT_CHECK`. Bio-ML is the track that would otherwise carry
  biomedical natural pairs, so biomedical pairs **cannot** be taken from OAEI.
  I did not upgrade any of these: the manifest's own boundary says a
  `CANNOT_CHECK` licence terminal is never upgraded by inaction, elapsed time, or
  upstream-licence adjacency, and I found no new explicit evidence for them.
- `CANNOT_CHECK` — **EFO licence.** The disposition matrix names the successor
  corpus as "E10 GO / Uberon / EFO". GO (CC BY 4.0) and Uberon (CC BY 3.0) are
  licence-clear in the OBO Foundry registry, along with CL, CHEBI, DOID and PATO.
  EFO is not in that registry, and the EBI OLS4 record (v3.93.0) returned no
  licence annotation. I did not infer one from EBI adjacency. EFO is neither
  acquired nor proposed.
- `CANNOT_CHECK` — **matched-polarity opposite-verdict pairs.** These require the
  annotation step above. Not produced and not estimated.

The licence-verified OBO list is recorded in `COHORT_V1.json` as *evidence*, of the
kind the manifest requires to upgrade a `CANNOT_CHECK`. Selecting a natural-pair
track remains a protocol decision, which this record does not make. Note also the
standing boundary that an incomplete reference alignment never makes absent entity
pairs true negatives.

## Honest bottom line

bench23 is acquired, verified, and measurably anti-confounded on polarity — a real
unblock of the manifest's primary benchmark. It is also **one seed ontology in one
domain**, against a successor design calling for 4 domains and 768 independent
units. It is a necessary step, not a sufficient corpus.
