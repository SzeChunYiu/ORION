# Provider-root rights and historical-byte successor audit

**Frozen cutoff:** `2025-12-31T23:59:59Z`  
**Roots:** 16 across Crossref, Zenodo, GitLab.com, and NASA ESDIS CMR  
**Authority:** public policy, metadata, exact-revision, licence-text, and archive-index evidence only  
**Scientific terminal:** `CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING`

This is the outcome-blind successor to the frozen provider-diverse metadata census. It asks whether every proposed root has (i) exact pre-cutoff historical bytes where required and (ii) a root-bound permission for each intended content class. It does **not** decide legal rights, open case content, establish case eligibility, inspect labels/outcomes, or test any P1--P5 scientific claim.

## 1. Exact results

| Quantity | Result |
|---|---:|
| Audited roots | 16 |
| Rights/content-class cells | 66 |
| `ROOT_BOUND_PERMISSION` | 8 |
| `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` | 10 |
| `ACCESS_ONLY_NOT_REUSE` | 2 |
| `CANNOT_CHECK` | 30 |
| `NOT_ACCESSED` | 16 |
| Crossref roots requiring exact historical bytes | 8 |
| Crossref roots with exact pre-cutoff bytes | 0 |
| Crossref historical-byte terminals | 8 `CANNOT_CHECK` |
| Narrow successor gaps | 66 |

The eight root-bound cells are narrow: four Zenodo metadata records under the platform's CC0 metadata policy; two repository-code cells at exact GitLab commits; and the metadata plus collection-file cells of one NASA-led GES DISC/AIRS CMR root. They do not extend to eligibility, labels, outcomes, linked objects, issue prose, attachments, or third-party documentation.

## 2. Evidence-quality audit

- All 21 official policy/licence/robots evidence pages contained every predeclared assertion string at capture time.
- All 12 distinct URLs named in current Crossref licence/TDM fields returned live HTTP responses. Liveness is not proof of DOI-root scope. Crossref expressly says deposited licence URLs are not verified.
- The ideal January 2026 Crossref Metadata Plus snapshot route returned HTTP `404`. Crossref documents that monthly snapshots cover the preceding month, require Metadata Plus access, and have limited retention.
- The 2025 public-data torrent manifest was obtained without downloading its corpus:
  - infohash: `e0eda0104902d61c025e27e4846b66491d4c9f98`
  - torrent response SHA-256: `ec96ae51e674660f949bb3d239e463cc5f75c73f741a650fa7b7f82898726d15`
  - 33,402 files, 93,908 pieces, 2,097,152-byte piece length
  - root membership: `CANNOT_CHECK_WITHOUT_197GB_CORPUS_EXTRACTION_OR_PROVIDER_INDEX`
- Sixteen Internet Archive CDX queries were attempted: 11 returned HTTP 200 with empty capture rows; five timed out and therefore remain `REQUEST_ERROR_CANNOT_CHECK`; zero captures were confirmed. No replay body was fetched. The timeouts are not recoded as empty results.
- No publisher article, abstract, dataset payload, issue/comment, attachment, repository description, case label, comparator/candidate output, protected gold, or outcome was opened.

## 3. Crossref history and rights

The hashes below identify the **current sparse normalized metadata object**, not historical pre-cutoff bytes.

| DOI | Current publisher | Current deposit | Deposit after cutoff | Current sparse normalized SHA-256 | Article-body cell |
|---|---|---|---:|---|---|
| `10.1016/j.bj.2025.100874` | Elsevier BV | `2026-04-03T01:56:08Z` | yes | `6233e3fb59f6f038ec7974e997a6783964dbfc6415867d6472868cd2b36eeb54` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.53941/eesus.2025.100001` | Scilight Press Pty Ltd | `2025-09-08T06:10:29Z` | no | `cc4f1b1e6cecc016ad9409f5e03fba54cd507539aab67f3d32ddc2d0e06be5c6` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.1016/j.envsoft.2025.106834` | Elsevier BV | `2026-02-09T07:35:02Z` | yes | `58a7fb1152af7bc83c96a04eaf6e6f1eb40eaafaf2c5e2c6880512fdd756af62` | `CANNOT_CHECK` |
| `10.35896/ijecie.v9i1.914` | Universitas Al-Hikmah Indonesia | `2025-07-03T04:46:23Z` | no | `36cdc5e2b3602a15752fbe88956e86f92fc7fae62aa24710000a39f3fb5eb861` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.31354/globalce.v6isi6.283` | Global Clinical Engineering Journal | `2025-01-30T22:24:02Z` | no | `8e205677cac64254960b9f2f868983181296caf25df9747b411236c5ddf00881` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.30564/jees.v7i4.8039` | Bilingual Publishing Group | `2025-03-28T03:19:29Z` | no | `31b9408fc7520a96247538757d6320e96ba2962d358970e094fb1ecfd8bb527f` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.1016/j.sciaf.2025.e03156` | Elsevier BV | `2026-07-20T17:30:33Z` | yes | `5f4bd5bca3e66a3f668b08b20cdb1aa766f74db94b72e939393366df1bac12e6` | `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED` |
| `10.1208/s12248-025-01156-0` | Springer Science and Business Media LLC | `2026-02-11T18:02:00Z` | yes | `d1c4857adfafb94fdb4503c51307dd1f26bad2e39cf3b3d9e5c941c49325245f` | `CANNOT_CHECK` |

Four of eight current deposits are post-cutoff. Only `10.31354/globalce.v6isi6.283` could have appeared in the 2025 annual file by provider creation time, but root membership was not extracted. The other seven were created after that file's 12 March 2025 release. Hence all eight retain `CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES`.

The six article roots with current Creative Commons declarations remain `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED`: the declaration is member-supplied, Crossref does not verify it, and neither publisher-root byte scope nor depositor authority was bound. The other two article roots exposed TDM/policy links rather than a root-bound reuse grant and remain `CANNOT_CHECK`. All Crossref metadata-reuse and supplement/attachment cells remain `CANNOT_CHECK`.

## 4. Public sources that can feed a later P1--P5 naturalistic panel

The table separates what a public source can actually close from what it cannot. “Root-bound” below is the protocol status, not legal advice.

| Root and exact public API identity | Frozen revision/hash | Permission preflight | Blocker it can close | Blockers it cannot close |
|---|---|---|---|---|
| Zenodo `18092984`; `https://zenodo.org/api/records/18092984` | version DOI `10.5281/zenodo.18092984`; updated `2025-12-30T08:03:40.291943+00:00`; record SHA-256 `d6475ac958829903939c23188079cf3ec3343f20fa83637d2091781a56fd553b` | metadata CC0 root-bound; files declare CC BY 4.0 with uploader authority unverified | Exact metadata/version identity and a reusable metadata-only source-frame row | File acquisition, linked objects, case eligibility, labels/outcomes, empirical mechanism |
| Zenodo `18108141`; `https://zenodo.org/api/records/18108141` | version DOI `10.5281/zenodo.18108141`; updated `2025-12-31T18:54:15.026380+00:00`; record SHA-256 `9dc271d16bee6d93fdda76e46e4f37b32243440a681515960b7e1fcd8420bd5b` | metadata CC0 root-bound; files declare CC BY 4.0 with uploader authority unverified | Exact metadata/version identity and a reusable metadata-only source-frame row | File acquisition, linked objects, case eligibility, labels/outcomes, empirical mechanism |
| Zenodo `17852132`; `https://zenodo.org/api/records/17852132` | version DOI `10.5281/zenodo.17852132`; updated `2025-12-24T11:08:22.620362+00:00`; record SHA-256 `8ceff8e6fcdcbb7e53daf013dc2681856969b9375134e5833d5fa769bf120d57` | metadata CC0 root-bound; files declare CC BY 4.0 with uploader authority unverified | Replication-wave metadata/version identity | File acquisition, linked objects, case eligibility, labels/outcomes, empirical mechanism |
| Zenodo `18109101`; `https://zenodo.org/api/records/18109101` | version DOI `10.5281/zenodo.18109101`; updated `2025-12-31T15:24:31.201398+00:00`; record SHA-256 `ce142172b499c7b389c08763db7523a9fdc9664a569520a414bd42e2606eac1f` | metadata CC0 root-bound; files declare CC BY 4.0 with uploader authority unverified | Replication-wave metadata/version identity | File acquisition, linked objects, case eligibility, labels/outcomes, empirical mechanism |
| GitLab `gromacs/gromacs`; `https://gitlab.com/api/v4/projects/gromacs%2Fgromacs` | commit `7942c72d82739c8f5ad782eac75ab97e40f79992` at `2025-12-22T20:24:33.000+01:00`; `COPYING` content SHA-256 `b634ab5640e258563c536e658cad87080553df6f34f62269a21d554844e58bfe` | exact repository code LGPL-2.1 root-bound | A pre-cutoff, content-addressed code artifact for a software-revision source cell | Project-metadata reuse, issue/comment prose, attachments, case eligibility, labels/outcomes |
| GitLab `QEF/q-e`; `https://gitlab.com/api/v4/projects/QEF%2Fq-e` | commit `2d07d94fc9613bdc2a5fd1eb10d4035b57c053ae` at `2025-12-29T12:04:54.000+00:00`; `License` content SHA-256 `204d8eff92f95aac4df6c8122bc1505f468f3a901e5a4cc08940e0ede1938994` | exact repository code GPL-2.0 root-bound | A pre-cutoff, content-addressed code artifact for a replication software-revision cell | Project-metadata reuse, issue/comment prose, attachments, case eligibility, labels/outcomes |
| NASA CMR `C2210183595-GES_DISC`; `https://cmr.earthdata.nasa.gov/search/concepts/C2210183595-GES_DISC/15.umm_json` | revision 15 at `2025-05-20T15:52:55.278Z`; exact response SHA-256 `0fbf20946a63bb75cf5bd781860fc40d05ad7fe8b759485c7f5446b97904c99c` | NASA-led root metadata and collection data files root-bound under the cited NASA CC0 guidance | An exact pre-cutoff physical/instrument-data root whose metadata and data-file permission cells are closed | Third-party documentation/attachments, case eligibility, labels/outcomes, empirical mechanism |
| NOAA CMR `C2107094645-NOAA_NCEI`; `https://cmr.earthdata.nasa.gov/search/concepts/C2107094645-NOAA_NCEI/1.umm_json` | revision 1 at `2021-08-20T15:21:43.807Z`; exact response SHA-256 `14d66cd03771576ff5df01b10aa5656bf998387841f7ae566bee33a90951bdad` | metadata, files, and documentation all `CANNOT_CHECK`; NASA defers non-NASA data rights to the sponsor | Exact pre-cutoff source identity and negative-control provenance only | Any content acquisition or use until a NOAA root-bound grant is obtained; eligibility and all scientific results |

### Direct panel-design implication

The currently strongest legally conservative next panel is not “all 16 roots.” It is an **outcome-blind, rights-gated panel construction**:

1. Use the four Zenodo rows only for source-frame metadata until uploader authority is independently bound.
2. Use the two GitLab roots only for exact licensed code revisions; do not infer that the code licence covers issue discussions or uploads.
3. Treat the NASA GES DISC root as the only current root with both exact historical metadata bytes and root-bound collection-file permission; send documentation and eligibility to a separate custodian gate.
4. Keep NOAA and all Crossref content outside acquisition until their named successors close.
5. Only after rights closure may an external custodian apply frozen eligibility rules and return aggregate counts/exclusions without revealing labels or outcomes.

This can close source identity, exact-revision, and selected content-class permission blockers. It cannot by itself produce a naturalistic empirical estimate, identify a revision mechanism, validate transport across providers, or support a positive P1--P5 claim.

## 5. Immutable negative-result recursion

Every unresolved cell maps to exactly one narrower successor in `SUCCESSOR_GAP_LEDGER_V1.json`:

| Unresolved cell family | Count | Required next discriminator |
|---|---:|---|
| Crossref exact pre-cutoff metadata bytes | 8 | Original member deposit XML plus receipt/hash, or an independently preserved January 2026 snapshot extraction with root proof |
| Crossref public metadata reuse | 8 | An authoritative grant covering the exact retained member-supplied field whitelist |
| Publisher article-body rights | 8 | Publisher-signed DOI/version-specific assertion binding intended processing |
| Publisher supplement/attachment rights | 8 | Root policy enumerating those classes separately |
| Outcome-blind case eligibility | 16 | External custodian returns counts/exclusions only after rights closure |
| Zenodo uploader authority | 4 | Depositor-signed authority statement or independent file-level rights audit |
| Zenodo linked/derived objects | 4 | Enumerate and independently bind every external object's licence |
| GitLab project-metadata reuse | 2 | Project-root or provider grant for the retained metadata fields and use |
| GitLab issue/comment rights | 2 | Root-bound grant covering user prose |
| GitLab issue-attachment rights | 2 | Root-bound grant covering each attachment class |
| CMR documentation/third-party attachments | 2 | Classify authorship and bind separate permission before retrieval |
| NOAA collection metadata | 1 | NOAA-root authoritative metadata reuse grant |
| NOAA collection files | 1 | NOAA-root authoritative data-use grant |

Positive, negative, and continuing-`CANNOT_CHECK` conditions are explicit for every successor. No missing permission, archive timeout, absent historical byte object, or unopened content class is converted into a positive result.

## 6. Verification and artifact authority

`VERIFICATION_RECEIPT_V1.json` validates self-hashes and cross-artifact hashes; 16 unique roots; eight Crossref history negatives and zero positives; all 66 rights cells and their status counts; a one-to-one mapping from each unresolved cell to 66 unique successors; evidence URL/hash/timestamp completeness; and the no-content/no-label/no-outcome boundaries.

Its structural status is `PASS_STRUCTURAL_INTEGRITY_WITH_SCIENTIFIC_CANNOT_CHECK`. This means the negative-result ledger is internally consistent. It does not change the scientific terminal.

Authoritative machine-readable artifacts:

- `PROTOCOL_V1.json`
- `EVIDENCE_SNAPSHOT_V1.json`
- `ROOT_RIGHTS_HISTORY_LEDGER_V1.json`
- `SUCCESSOR_GAP_LEDGER_V1.json`
- `VERIFICATION_RECEIPT_V1.json`
