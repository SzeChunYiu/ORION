# P4 public naturalistic source audit V1

**Date:** 2026-08-23  
**Target:** `P4.H3.NATURALISTIC.V1`, planned 768 source--case-family clusters  
**Binding:** `P4.NAT.AXIS.768.ARXIV_CC_BY_POOL_1536.V1`  
**Terminal:** `PUBLIC_CC_BY_SOURCE_POOL_BOUND__NATURALISTIC_CASE_ADJUDICATION_REQUIRED`

This is a reproducible rights-screening record, not legal advice. The binding
uses the provider's explicit licence metadata and retains fail-closed exclusions;
submission counsel or the responsible data custodian remains the final rights
authority.

## Decision

The official arXiv OAI-PMH repository is accepted as the first lawful,
multi-domain **source-candidate provider** for P4's naturalistic successor.
This is a source binding, not a case panel and not an empirical result.

This P4-only binding is disjoint from the programme-level
`P4.NAT.METADATA.G01.V1` census. That census establishes candidate
provider/modality diversity but leaves content-class rights unresolved. The
present binding establishes attributed text reuse and immutable version identity
for a deep single-provider pool. It does not erase the census's provider/
modality or historical-byte `CANNOT_CHECK` terminals and cannot substitute
arXiv rows for the census's Crossref, Zenodo, GitLab or NASA cells.

The frozen pool contains 1,536 author-written scientific records, two candidates
for every planned case:

| P4 domain | Official arXiv OAI set(s) | Bound candidates | Planned adjudicated cases |
|---|---|---:|---:|
| Earth/environment | `physics:physics:ao-ph`, `physics:physics:geo-ph`, `physics:astro-ph:EP` | 384 (128 each) | 192 |
| Life/biomedical | `q-bio` | 384 | 192 |
| Scientific software | `cs:cs:SE` | 384 | 192 |
| Physical engineering | `eess` | 384 | 192 |
| **Total** | | **1,536** | **768** |

The source-pool SHA-256 is
`47dd24657752731cdf45bab95852f3e18b50946af8a29b5acee95956ec81d895`.
All 24 raw OAI XML pages are retained as deterministic gzip members and bound
by both compressed and uncompressed SHA-256 values in the harvest log.

## Why this provider is usable

### Official access

- Metadata came from arXiv's official OAI-PMH endpoint,
  <https://export.arxiv.org/oai2>, using the official `arXivRaw` format.
- The official schema contains record ID, version history, title, authors,
  categories, licence, abstract, DOI and journal reference where present.
- The harvest was rate-limited to one request every 3.1 seconds and used a
  declared research user agent.

### Content rights, not merely metadata visibility

arXiv's official licence page states two materially different things:

1. **all arXiv metadata is CC0 1.0**; and
2. **CC BY 4.0 article content may be distributed, remixed, adapted and built
   upon, including commercially, with attribution**.

The same page warns that arXiv's default perpetual non-exclusive distribution
licence gives limited rights to arXiv and limits reuse by others. Public
availability is therefore not treated as permission.

The pool accepts article content only when the contemporaneous official
`arXivRaw` record explicitly reports CC BY 4.0. It excludes:

- the default arXiv non-exclusive distribution licence;
- missing/unknown licences;
- CC BY-NC-ND and CC BY-NC-SA;
- CC BY-SA, conservatively, to avoid share-alike ambiguity in later benchmark
  case adaptations.

Every retained row includes authors, title, exact versioned identifier, licence
URL and an attribution string. This binding applies only to the arXiv-hosted
version. It does not confer rights over a publisher-formatted version reached
through the DOI.

### Immutable revision identity

arXiv's official version page states that every public version is a permanent
part of the scientific record, replacements and withdrawals create a new
version number, and a version may be cited with the full `arXiv:YYMM.NNNNNvX`
identifier. The pool therefore forbids unversioned content URLs and binds only
the exact latest `vN` present in the retained OAI record.

Because arXiv notes that different versions may have different licences, the
record-level licence observation is interpreted only for the exact latest
version present in the same retained snapshot. No earlier version inherits that
licence in P4 without a separate version-specific check.

## Live spot check

`source_binding/ARXIV_CC_BY_LIVE_SAMPLE_RECEIPT_V1.json` selected the first
frozen row in each domain. On 2026-08-23:

- 4/4 exact versioned abstract pages returned HTTP 200 and displayed a CC BY
  4.0 licence link;
- 4/4 exact versioned PDF URLs returned HTTP 200 with
  `Content-Type: application/pdf`.

This is a rights/availability diagnostic only. Four live checks do not replace
the official OAI licence filter or establish case eligibility.

## Metadata availability versus content rights versus case eligibility

| Layer | Current state | What it permits | What it does not permit |
|---|---|---|---|
| Metadata | `BOUND`, official OAI, CC0 | discovery, deduplication, stratification, immutable-ID binding | reuse of article content without its own licence |
| Article text | `BOUND FOR CANDIDATES`, CC BY 4.0 only | attributed text extraction and adaptation from the exact arXiv version | third-party figures/data, publisher PDFs, or differently licensed versions |
| Naturalistic P4 case | `UNADJUDICATED` | nothing outcome-authorizing yet | treating an abstract, paper, or metadata row as an eligible cluster |
| External scientific panel | `MISSING` | none | naturalistic superiority, independent evaluator authority, replication |

## Case-eligibility gates still required

Each final source cluster must pass all of the following before it can enter the
768-case panel:

1. **Rights:** exact source version remains CC BY 4.0; every used text span is
   attributable; third-party material is excluded or separately cleared.
2. **Atomic material claim:** the target is a scientifically material,
   adjudicable claim, not only a title, aspiration or generic background fact.
3. **Identifiable control:** the full permitted source view contains sufficient
   evidence for a qualified evaluator to resolve the target terminal.
4. **Unidentifiable pair member:** the paired restricted view genuinely lacks a
   load-bearing fact needed for that resolution; absence must not be inferred
   from a formatting shortcut.
5. **Mechanism assignment:** exactly one frozen primary mechanism is changed
   while answer wording and irrelevant surface coordinates are controlled.
6. **No nuisance recovery:** missingness, list length, template, version string,
   path, source count, metadata and field order do not recover pair membership
   under the frozen probe class.
7. **Independent adjudication:** producer and evaluator lineages differ, raw
   source custody is external to the candidate, and disagreements are retained.
8. **Replication eligibility:** no source family, author cluster, DOI lineage or
   exact artifact crosses into the source-disjoint replication panel.

The 2:1 candidate pool allows screening attrition, but it does **not** guarantee
that 192 eligible clusters will remain in every domain or that all eight
mechanisms will receive 24 clusters. If a cell is short, the terminal is a
source-cell shortfall and the harvest must be expanded under a disjoint binding;
cases may not be reassigned after outcomes.

## Third-party and research-ethics boundary

- V1 case construction is text-only unless a figure, table, dataset, code
  archive or supplement has its own recorded reuse permission.
- Personal data, clinical participant data and access-controlled supplements
  are excluded even when a paper discussing them is CC BY.
- Author names and affiliations are retained only for attribution,
  deduplication and source-disjoint grouping; they are not prediction features.
- DOI and journal references are discovery metadata. They do not authorize use
  of publisher content.
- Withdrawal markers were excluded during harvest. Later withdrawal or
  correction creates a new scientific-state event; it does not silently rewrite
  a frozen case.

## Alternatives screened but not selected as the primary content source

- **Crossref/DataCite metadata:** useful for discovery and licence pointers, but
  metadata access does not itself grant rights to article full text and record
  content/licence coverage varies. These can enrich deduplication later.
- **PubMed Central Open Access:** strong explicit article-licence information,
  but biomedical-only and therefore not a multi-domain frame by itself.
- **Public Git repositories/issues:** repository visibility is not a dataset
  licence; code licences often do not clearly cover issue text, attachments or
  third-party artifacts. Only separately licensed releases are eligible.
- **Wikidata/Wikimedia:** metadata/text rights are explicit, but secondary
  encyclopedia statements do not by themselves provide the primary scientific
  evidence structure required by P4.

These are not permanently rejected. They require their own source-specific
rights and eligibility bindings and cannot be silently pooled with arXiv V1.

## Exact artifacts

- `source_binding/harvest_arxiv_oai.py` — frozen outcome-blind harvester.
- `source_binding/ARXIV_CC_BY_SOURCE_POOL_V1.jsonl` — 1,536 attributed source candidates.
- `source_binding/ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json` — rights, identity and claim boundary.
- `source_binding/ARXIV_CC_BY_POOL_HARVEST_LOG_V1.json` — requests, exclusions and hashes.
- `source_binding/raw_oai_pages/*.xml.gz` — all 24 retained official OAI responses.
- `source_binding/verify_arxiv_sample.py` — live four-domain rights/availability check.
- `source_binding/ARXIV_CC_BY_LIVE_SAMPLE_RECEIPT_V1.json` — diagnostic receipt.
- `source_binding/validate_arxiv_pool.py` and `source_binding/ARXIV_CC_BY_SOURCE_POOL_VALIDATION_RECEIPT_V1.json` — 15/15 structural, rights-field and byte-fixity checks.
- `source_binding/policy_snapshots/` and `source_binding/OFFICIAL_ARXIV_POLICY_SNAPSHOT_RECEIPT_V1.json` — retained official policy/API/schema pages and hashes.
- `source_binding/SHA256SUMS` — file-level hashes for all 39 source-binding artifacts.

No pytest, CI, protected outcome access, case adjudication or scientific scoring
was performed.
