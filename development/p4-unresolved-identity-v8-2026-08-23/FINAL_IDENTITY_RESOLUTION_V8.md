# P4 unresolved identity targeted pass V8

- Frozen targets: **10**
- Repaired to `RESOLVED_SAME_IDENTITY`: **3** — 59, 108, 196
- Remaining fail-closed: **7** — 36, 91, 133, 165, 185, 190, 199
- Provider archives fetched and checksum-verified: **10/10**
- Total measured execution runtime: **36.011085 s**
- Scope: exact frozen targets only; no replacements, proxies, broad harvesting, or unit inflation.

## Adjudication

| Index | Repository | Verdict | Repaired gate(s) | Exact residual / next discriminator |
|---:|---|---|---|---|
| 36 | `jaxionproject/jaxion` | `REMAINS_CANNOT_CHECK` | `accepted_archive_software_rights`, `public_transport_receipted` | `EXACT_ARCHIVE_VERSION_DOI_RELATION_AND_ARCHIVE_ROOT_TO_TAG_COMMIT_IDENTITY_CANNOT_CHECK`. Provider-native correction or immutable child metadata must bind the frozen concept DOI to version 0.0.3 and the deposited root to commit 069ab4f56d100d765d46c594ac1b06add7e49f9e; the current child description says 0.0.12 and the embedded 0.0.3 ref is historical rather than the archive HEAD. |
| 59 | `mohd-afeef-badri/psd` | `RESOLVED_SAME_IDENTITY` | `accepted_archive_software_rights` | Closed |
| 91 | `nutritionallungimmunity/pai` | `REMAINS_CANNOT_CHECK` | — | `ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK`. An authoritative provider relation or archive provenance record must name exact commit 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59, or provider archive content must exactly equal that immutable commit tree. |
| 108 | `cwru-sdle/fairlinked` | `RESOLVED_SAME_IDENTITY` | `archive_to_commit_content_or_authenticated_origin_identity` | Closed |
| 133 | `artefactory/woodtapper` | `REMAINS_CANNOT_CHECK` | — | `ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK`. The provider must expose an authenticated full revision edge to 7ac6d23d504404c4004faad663f6b889427109e6 or exact provider archive content must equal that immutable commit tree. |
| 165 | `alek050/databallpy` | `REMAINS_CANNOT_CHECK` | `accepted_archive_software_rights` | `ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK`. The provider must expose an authenticated full revision edge to b52a049f685af3fc849359673c4ac183e7ccc5d3 or exact provider archive content must equal that immutable commit tree. |
| 185 | `mit-psfc/disruption-py` | `REMAINS_CANNOT_CHECK` | — | `EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK`. A source-native restored v0.14.0 ref/release or provider-authenticated metadata must disclose its full immutable commit; only then can exact commit rights and archive identity be bound. |
| 190 | `ugurdar/datadriftr` | `REMAINS_CANNOT_CHECK` | — | `EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK`. A source-native restored 1.1.0 ref/release or provider-authenticated metadata must disclose its full immutable commit; only then can exact commit rights and archive identity be bound. |
| 196 | `watershedswildfireresearchcollaborative/separate` | `RESOLVED_SAME_IDENTITY` | `accepted_archive_software_rights`, `archive_to_commit_content_or_authenticated_origin_identity`, `exact_frozen_archive_version_doi_relation`, `public_transport_receipted` | Closed |
| 199 | `targene/targene-pipeline` | `REMAINS_CANNOT_CHECK` | — | `EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK`. Software Heritage or the source provider must expose a full revision edge for the archived 0f8b2db prefix and bind v0.13.4 to it; the current authenticated SWH release terminates at a directory, not a revision. |

## Closed identity chains

- **59 PSD:** exact version DOI/archive + V7 immutable-commit manifest equality + V8 Apache-2.0 archive license bytes equal exact-commit license bytes.
- **108 FAIRLinked:** checksum-verified provider archive embeds `refs/tags/v0.3.3.4 -> 1e831e074ae465956b66305df029bfcd286afe9f` and matching origin `FETCH_HEAD`; archive and commit rights are BSD-3-Clause.
- **196 SEPARATE:** DataCite `HasVersion` binds the concept DOI to unique Zenodo child `10.5281/zenodo.19141363` version `V1.1.0`; V7 SWH-directory/Git-tree equality binds the archive to commit `ba11b623cebc5d042f7bbe6c23b1f48c5d71c27f`; MIT license bytes match.

## Evidence receipts

- `PROTOCOL_V8.json` — `51a4428edad33536a6dcf69e8c8504342d6213b2a487257eeeb2f50e43581c23`
- `PROVIDER_PROBE_RECEIPT_V8.json` — `75be073efebf130ef5ab787420146ab857888df05e8bba9a2de5dd497def5a81`
- `SWH_199_PROBE_RECEIPT_V8.json` — `57983f04ac8410ba0cb6c2a375ffeabcf471cc04b3dc06c745ccf868c296883c`
- `FINAL_IDENTITY_RESOLUTION_V8.json` — written from the frozen gates and receipts above
