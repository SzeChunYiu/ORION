# Provider-diverse metadata census: G01 outcome-blind successor

**Lane:** `provider-diverse-metadata-census-2026-08-23`  
**Gap:** G01, `PROVIDER_MODALITY_TRANSPORT_METADATA_CENSUS_V1`  
**Cutoff:** 2025-12-31T23:59:59Z  
**Scope:** public provider metadata and exact licence-file bytes only  
**Authority:** metadata-census conformance only; not a case frame, scientific result, legal opinion, or external custody binding

## Decision

The prior twelve-family tranche established only one metadata provider
(GitHub) and one modality (software repository).  This successor freezes and
verifies a **sixteen-record, two-wave candidate metadata frame** with four
metadata providers and four artifact modalities in each wave.

The structural metadata quotas pass:

- 8 candidate roots per wave;
- 4 candidate domains per wave, with 2 roots in each domain;
- 4 distinct metadata providers per wave;
- 4 distinct modalities per wave;
- the frozen domain-by-modality matrix is complete in both waves;
- no canonical source-family or persistent-identifier collision occurs across
  waves; and
- 16/16 exact live provider identities verify.

This is **not** a positive scientific result.  A provider metadata record or a
public URL is not an eligible case.  Crossref does not expose the exact
historical metadata bytes for the pre-cutoff DOI identity, protected-content
rights remain unresolved for every record, and no case eligibility or
scientific stratum membership was assessed.  The scientific terminal therefore
remains:

`CANNOT_CHECK_SOURCE_UNIVERSE`

The finer conformance terminal is:

`METADATA_CENSUS_CONFORMANCE_PASS__SCIENTIFIC_TERMINAL_UNCHANGED`

## Provider, host, and modality are different variables

The census counts `metadata_provider_id`, not publisher, repository owner, or
data centre.  `content_host_identity` is reported separately.  Artifact
modality is a third independent field.  For example, Crossref is the metadata
provider for an article whose content host is its publisher; NASA CMR is the
metadata provider for a calibration collection hosted by NOAA NCEI or GES
DISC.  No host is silently relabelled as a provider, and no provider name
determines modality.

| wave | candidate roots | metadata providers | content hosts | modalities | domains | roots/domain |
|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | 8 | 4 | 6 | 4 | 4 | 2 |
| REPLICATION | 8 | 4 | 7 | 4 | 4 | 2 |

Both waves contain:

- `CROSSREF_REST_API` / `PUBLISHER_ARTICLE`;
- `ZENODO_REST_API` / `DATA_REPOSITORY_DEPOSIT`;
- `GITLAB_COM_REST_API_V4` / `NON_GITHUB_PROJECT_TRACKER`; and
- `NASA_ESDIS_CMR_SEARCH_API` / `INSTRUMENT_CALIBRATION_ARCHIVE`.

The four-domain matrix in each wave is:

| candidate domain | required modalities |
|---|---|
| biomedical/clinical | publisher article; data-repository deposit |
| earth/environmental | publisher article; data-repository deposit |
| computational scientific software | publisher article; non-GitHub project tracker |
| physical/engineering | publisher article; instrument/calibration archive |

These are query-route domain candidates, not adjudicated scientific cases.

## Frozen candidate identities

| wave | domain | provider | modality | exact provider identity | content host | pre-cutoff token |
|---|---|---|---|---|---|---|
| PRIMARY | biomedical/clinical | Crossref | article | `10.1016/j.bj.2025.100874` | Elsevier BV | created `2025-05-20T11:57:00Z`; historical bytes `CANNOT_CHECK` |
| PRIMARY | biomedical/clinical | Zenodo | data deposit | `18092984` | Zenodo | version DOI `10.5281/zenodo.18092984` |
| PRIMARY | earth/environmental | Crossref | article | `10.53941/eesus.2025.100001` | Scilight Press Pty Ltd | created `2025-09-08T06:10:28Z`; historical bytes `CANNOT_CHECK` |
| PRIMARY | earth/environmental | Zenodo | data deposit | `18108141` | Zenodo | version DOI `10.5281/zenodo.18108141` |
| PRIMARY | computational scientific software | Crossref | article | `10.1016/j.envsoft.2025.106834` | Elsevier BV | created `2025-12-12T08:00:26Z`; historical bytes `CANNOT_CHECK` |
| PRIMARY | computational scientific software | GitLab.com | project tracker | `gromacs/gromacs` | `gromacs` | commit `7942c72d82739c8f5ad782eac75ab97e40f79992` |
| PRIMARY | physical/engineering | Crossref | article | `10.35896/ijecie.v9i1.914` | Universitas Al-Hikmah Indonesia | created `2025-07-03T04:46:17Z`; historical bytes `CANNOT_CHECK` |
| PRIMARY | physical/engineering | NASA CMR | calibration archive | `C2107094645-NOAA_NCEI` | NOAA NCEI | CMR revision 1, `2021-08-20T15:21:43.807Z` |
| REPLICATION | biomedical/clinical | Crossref | article | `10.31354/globalce.v6isi6.283` | Global Clinical Engineering Journal | created `2025-01-01T12:15:10Z`; historical bytes `CANNOT_CHECK` |
| REPLICATION | biomedical/clinical | Zenodo | data deposit | `17852132` | Zenodo | version DOI `10.5281/zenodo.17852132` |
| REPLICATION | earth/environmental | Crossref | article | `10.30564/jees.v7i4.8039` | Bilingual Publishing Group | created `2025-03-28T03:19:28Z`; historical bytes `CANNOT_CHECK` |
| REPLICATION | earth/environmental | Zenodo | data deposit | `18109101` | Zenodo | version DOI `10.5281/zenodo.18109101` |
| REPLICATION | computational scientific software | Crossref | article | `10.1016/j.sciaf.2025.e03156` | Elsevier BV | created `2025-12-29T16:28:20Z`; historical bytes `CANNOT_CHECK` |
| REPLICATION | computational scientific software | GitLab.com | project tracker | `QEF/q-e` | `QEF` | commit `2d07d94fc9613bdc2a5fd1eb10d4035b57c053ae` |
| REPLICATION | physical/engineering | Crossref | article | `10.1208/s12248-025-01156-0` | Springer Nature | created `2025-10-24T17:03:01Z`; historical bytes `CANNOT_CHECK` |
| REPLICATION | physical/engineering | NASA CMR | calibration archive | `C2210183595-GES_DISC` | NASA GES DISC | CMR revision 15, `2025-05-20T15:52:55.278Z` |

Exact public record URLs, exact metadata URLs, content hosts, ISSN or concept
family roots, DOI/project/concept identifiers, provider receipts, selected
revision fields, content-class rights statuses, and record hashes are in
`SOURCE_CENSUS_V1.json`.

## Query, rank, exclusion, and deduplication freeze

`CENSUS_PROTOCOL_V1.json` freezes all routes and rules.  In outline:

1. **Crossref:** fixed 2025 creation interval, `journal-article`,
   `has-license:true`, four domain query strings, provider-native relevance,
   normalized DOI tie-break, and a sparse exact-identity query that does not
   request title or abstract.
2. **Zenodo:** fixed domain query plus `created:[2025-01-01 TO 2025-12-31]`,
   dataset type, most-recent ordering, numeric record-ID tie-break.
3. **GitLab:** predeclared exact official namespace identity, singleton rank,
   and the last public commit no later than the cutoff.
4. **NASA CMR:** predeclared exact concept plus exact historical revision,
   singleton rank, and revision-history proof.

Six broad query receipts (four Crossref and two Zenodo) retain exact query URL,
response SHA-256 and byte count, eligible count, and selected identity/rank
pairs.  Their response bodies were not archived.  All twelve selected
Crossref/Zenodo identities occupy their frozen ranks; the four exact
GitLab/CMR identities are singleton rank 1.

Metadata-only exclusions reject an identity mismatch, post-cutoff identity,
wrong record type, missing URL/root, deleted/private record, unresolved
deduplication collision, or an omitted rights status.  Rights ambiguity is
recorded as `CANNOT_CHECK`; it is never silently treated as permission.

Deduplication roots are:

- Crossref: sorted ISSN family; article identity by normalized DOI;
- Zenodo: concept DOI family; version identity by version DOI;
- GitLab: immutable numeric project ID; and
- CMR: provider ID plus native ID; revision identity by concept ID plus
  revision ID.

Cross-provider persistent identifiers are normalized before collision checks.
A later-ranked collision is excluded; failure to refill its frozen cell emits
`CANNOT_CHECK_SOURCE_DISJOINTNESS`.

## Pre-cutoff revision audit

| provider class | records | exact pre-cutoff state |
|---|---:|---|
| Crossref | 8 | DOI identity creation before cutoff verified; exact historical metadata bytes unavailable, so `CANNOT_CHECK_HISTORICAL_METADATA_BYTES` |
| Zenodo | 4 | exact version DOI and provider update timestamp before cutoff |
| GitLab.com | 2 | exact commit SHA and committer date before cutoff; licence bytes reverified at that commit |
| NASA CMR | 2 | exact concept/revision ID, revision date, and historical UMM response bytes reverified |

Thus 4/16 candidate roots have exact historical response bytes or commit
identity (two GitLab and two CMR), 4/16 have exact Zenodo version-record
identity with a pre-cutoff metadata update, and 8/16 Crossref records retain
the stricter historical-byte `CANNOT_CHECK`.  No Crossref creation timestamp is
called a historical byte revision.

## Rights boundary by content class

The four official provider terms URLs returned HTTP 200 to HEAD at verification
time.  Liveness is not a legal grant.

- **Crossref:** provider records declare licence URIs, content versions, and
  start dates.  Article and attachment bytes were not fetched.  The declared
  URI is evidence about provider metadata, not proof that a future case unit is
  processable or redistributable.
- **Zenodo:** all four records declare `cc-by-4.0` in provider metadata.  No
  dataset file or attachment was fetched, so file-byte scope remains
  `CANNOT_CHECK` for case construction.
- **GitLab.com:** exact licence-file bytes at the two frozen commits were hashed:
  `b634ab5640e258563c536e658cad87080553df6f34f62269a21d554844e58bfe`
  for `gromacs/gromacs/COPYING` and
  `204d8eff92f95aac4df6c8122bc1505f468f3a901e5a4cc08940e0ede1938994`
  for `QEF/q-e/License`.  SPDX is deliberately `NOASSERTION`; repository-code
  rights do not settle issue, comment, or attachment rights.
- **NASA CMR:** one historical record contains a use-constraints metadata
  object and one does not.  Neither supplies a verified explicit file licence
  for this lane.  Collection files and documents remain `CANNOT_CHECK`.

No legal status is inferred from HTTP accessibility.

## Exact quota terminals

| gate | observed | terminal |
|---|---:|---|
| frozen structural metadata cells | 16/16 populated | `POPULATED_FOR_ALL_SIXTEEN_FROZEN_METADATA_CELLS` |
| provider diversity | 4 per wave | `PASS_FOUR_METADATA_PROVIDERS_PER_WAVE` |
| modality diversity | 4 per wave | `PASS_FOUR_MODALITIES_PER_WAVE` |
| cross-wave canonical-root collision | 0 | `PASS_NO_CANONICAL_ROOT_COLLISION` |
| records without exact historical revision bytes | 8 | `CANNOT_CHECK_PRE_CUTOFF_REVISION` for those Crossref roots |
| records with future case-content rights unresolved | 16 | `CANNOT_CHECK_CONTENT_CLASS_RIGHTS` |
| records with case eligibility assessed | 0/16 | `METADATA_CANDIDATE_ONLY__CASE_ELIGIBILITY_NOT_ASSESSED` |
| overall G01 source universe | incomplete | `CANNOT_CHECK_SOURCE_UNIVERSE` |

The metadata frame verifies **zero** of the downstream case quotas: P1 R7A
still requires 896 clusters, while the P3, P4, and P5 successors each still
require 768.  No count in this lane can be substituted for one of those
independent units.

## Negative-result recursion opened

The original provider/modality monoculture is narrowed but not erased.  The
new adverse facts are separate research problems:

1. **Historical metadata reconstruction:** obtain signed or independently
   archived pre-cutoff Crossref record bytes, or preregister identity-only
   handling as a distinct stratum.  Until then, exact article-metadata revision
   transport is `CANNOT_CHECK`.
2. **Content-class permission binding:** a legal/custody owner must bind article
   body, dataset file, issue/comment, and attachment handling per selected
   root.  Repository or metadata licences cannot be promoted across classes.
3. **Outcome-blind eligibility census:** an external custodian must apply the
   frozen routes and return counts/exclusions without exposing content, labels,
   or outcomes.  Zero eligible cases in any frozen cell is a new negative
   source-universe result, not a licence to drop the cell.
4. **Transport discriminant:** if eligible counts exist, freeze a provider ×
   modality interaction estimand before scoring.  Metadata diversity alone
   cannot show that decisions transport across providers or modalities.

Every adverse result remains immutable and opens a new successor identity; none
is rewritten as a positive predecessor result.

## Reproducibility and artifacts

- `CENSUS_PROTOCOL_V1.json` — query routes, ranks, exclusions, quotas,
  deduplication, and fail-closed terminals.
- `SOURCE_CENSUS_V1.json` — 16 normalized provider metadata records and exact
  quota/unresolved counts.
- `build_metadata_census.py` — metadata-only snapshot builder.
- `verify_metadata_census.py` — exact provider-identity, byte-fixity, quota,
  deduplication, and terminal verifier.
- `VERIFICATION_RECEIPT_V1.json` — 13/13 conformance checks and 16/16 live exact
  provider identity receipts.
- `SHA256SUMS` — file-level integrity manifest.

Commands used (no pytest or CI was run):

```bash
rtk python development/provider-diverse-metadata-census-2026-08-23/build_metadata_census.py
rtk python development/provider-diverse-metadata-census-2026-08-23/verify_metadata_census.py
rtk python -m json.tool development/provider-diverse-metadata-census-2026-08-23/CENSUS_PROTOCOL_V1.json
rtk python -m json.tool development/provider-diverse-metadata-census-2026-08-23/SOURCE_CENSUS_V1.json
rtk python -m json.tool development/provider-diverse-metadata-census-2026-08-23/VERIFICATION_RECEIPT_V1.json
rtk shasum -a 256 -c development/provider-diverse-metadata-census-2026-08-23/SHA256SUMS
```

No manuscript, existing harness, frozen paper protocol, branch, or commit was
changed by this lane.
