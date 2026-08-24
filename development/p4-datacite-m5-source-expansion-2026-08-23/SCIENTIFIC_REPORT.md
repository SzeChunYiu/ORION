# P4 DataCite M5 disjoint-provider census V1

**Date:** 2026-08-23  
**Authority:** public DataCite metadata source feasibility only  
**Mechanism:** `M5_ARTICLE_TO_DATA_DOCUMENTATION`  
**Case/model outcomes accessed:** no  
**Content files or descriptions accessed:** no  
**Exact terminal:** `P4_DATACITE_M5_CENSUS_V1_CANNOT_CHECK_TRANSPORT_OR_SCHEMA`

## 1. Frozen lineage and unchanged scientific gate

This census is a provider-disjoint successor to the retained Zenodo results. It does not replace or reinterpret either negative identity:

- `P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400`
- `P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER`

The four domains remain `EARTH_ENVIRONMENT`, `LIFE_BIOMEDICAL`, `PHYSICAL_ENGINEERING`, and `SCIENTIFIC_SOFTWARE`. The M5 identity, publication-link requirement, and 48-signal gate remain unchanged. No count may move between domains. The 48 signals still decompose into 24 primary, eight source-disjoint replication, and 16 reserve signals.

Frozen protocol:

- payload SHA-256: `494089214d5509850c7812fea2a68ac753e8eaa8e09491b0ba170e8dc7b14456`
- file SHA-256: `210b446ff205c6f9cf25cc7c3231d388bfd4187e97006f3c897aabbecb16f691`

## 2. Frozen execution

Four unauthenticated official DataCite REST queries requested only the registered metadata fields needed for DOI identity, client disjointness, dataset type/state, exact rights declarations, HTTPS content-URL evidence, and typed related identifiers. Descriptions, subjects, funding, geolocations, metrics, XML, repository files, linked publications, case text, labels, and outcomes were not requested.

Each query froze `resource-type-id=dataset`, a domain term set, `page[size]=1000`, page 1, `sort=-updated`, and facet suppression.

| Frozen cell | Provider-reported total upper bound | Returned rows | Response bytes | Response SHA-256 | Provider/root-disjointness exclusions |
|---|---:|---:|---:|---|---:|
| Earth/environment M5 | 1,181,497 | 1,000 | 4,461,382 | `0eeb7b37ea34745cf9c48e0863cf5141a5a50b46b2eb4c206ea13a24f51c986c` | 1,000 |
| Life/biomedical M5 | 2,497,727 | 1,000 | 2,615,608 | `acf02d2ecd1829035d5b84ed5555b15966998c21add09fab39cba732bb6b101b` | 1,000 |
| Physical/engineering M5 | 19,452,912 | 1,000 | 1,583,838 | `a6e056829002af7349b2a3b7ad6125818a3e09274412dcefc08f98dc0e4d8e1c` | 1,000 |
| Scientific-software M5 | 626,258 | 1,000 | 2,025,899 | `c644d628e7f266af8c65a5b0a6911bc347f5fadcbd5d0933f067689f8865600b` | 1,000 |

All four API responses returned HTTP 200, satisfied the top-level JSON:API/list schema, returned the frozen 1,000 rows, and passed page-integrity checks. The provider totals are search upper bounds, not candidate or pair counts.

## 3. Retained adverse result

The sparse field selection did not request the JSON:API `client` relationship. Provider disjointness had been frozen to require a nonempty client identity in addition to excluding the Zenodo client, publisher, DOI prefix, and every bound Zenodo V2 DOI. Because the required client relationship was absent from every sparse row, all 4,000 rows failed closed at the provider/root-disjointness gate. No row reached rights, content-URL, or publication-relation admission, and `P4_DATACITE_M5_CANDIDATES_V1.jsonl` is the zero-byte empty set with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

A second, independent mechanics mismatch was retained. The DataCite query documentation returned HTTP 200 and contained the documented OpenSearch statement, but the predeclared literal `OpenSearch query string syntax` did not match the Markdown-linked phrase `OpenSearch [query string syntax]`. Three of four evidence pages passed all assertions; this one literal failed. It is an assertion-string mismatch, not evidence that DataCite lacks query support, and it is not silently repaired under V1.

These failures occur before scientific candidate evaluation. They do not constitute evidence against M5, against DataCite's underlying relation coverage, or for/against ORION.

## 4. Exact counts and preserved deficits

| Domain | Retained Zenodo V2 M5 signal | Admitted disjoint DataCite V1 signal | Combined signal | Deficit to 48 |
|---|---:|---:|---:|---:|
| Earth/environment | 37 | 0 | 37 | 11 |
| Life/biomedical | 44 | 0 | 44 | 4 |
| Physical/engineering | 29 | 0 | 29 | 19 |
| Scientific software | 30 | 0 | 30 | 18 |

The counts therefore remain exactly where Zenodo V2 left them. V1 neither closes nor narrows any scientific source-cell deficit. The exact result payload SHA-256 is `c9e55d910438b8fa0331a1810d6d3600ac8020846984a4e195c0cecbb2c39b20`; the result file SHA-256 is `793d2698957529653e708aff9c886ec9cdbc99beaca4247e1350a8fab877c5f7`.

The M6 cells were not re-queried or pooled into M5. Their immutable Zenodo V2 publication-typed counts remain 6, 10, 10, and 7 for earth/environment, life/biomedical, physical/engineering, and scientific software. Therefore no unchanged M5 cell, no unchanged M6 cell, and not the eight-cell conjunction passes the 48-signal gate.

Exact bounded census accounting is: one new metadata provider, four queries, four pages, 4,000 raw rows, 1,000 unique DOI identities within each query, 4,000 fail-closed provider/root-disjointness exclusions, zero rows reaching the exact-rights-declaration gate, zero rows reaching HTTPS-content-URL or publication-link gates, and zero admitted candidate records. DataCite metadata itself remains under the cited CC0 policy; the count of admitted dataset-content permission cells is zero.

## 5. Rights and claim boundary

The authoritative evidence establishes that DataCite's public REST API can be queried without authentication and that DataCite makes its registered metadata public under CC0. This authorizes the narrow metadata use asserted here; it does not license repository content or linked publications.

Even a later row containing CC BY 4.0 or CC0 in `rightsList` and an HTTPS `contentUrl` would remain a **depositor declaration plus accessibility signal** until repository-root scope and depositor authority are independently bound. A DataCite relation is a deposited identity assertion, not natural-pair adjudication. Accordingly V1 makes no claim about:

- repository-file permission or byte identity;
- linked-publication rights;
- natural-pair identity, eligibility, or material-claim relation;
- case resolution or protected gold;
- scientific performance, confirmation, provider generality, or ORION superiority.

## 6. Narrow successor discriminator; not executed in this turn

Any repair must use a distinct successor identity and retain this V1 result unchanged. Before a successor query is executed it must:

1. bind and exclude every DOI identity exposed in the four V1 response hashes;
2. add the DataCite `client` relationship to the sparse field set while continuing to exclude descriptions and content bytes;
3. exclude Zenodo at both query and row levels without weakening exact DOI/client/source-family disjointness;
4. replace the failed documentation literal with the exact linked-Markdown wording, recording this as a mechanics-only repair;
5. keep all four domains, M5, the 48 gate, atomic publication-typed relation screening, exact record-rights declarations, HTTPS content-URL evidence, and every rights/nonclaim boundary unchanged;
6. preserve a source shortfall if any combined cell remains below 48 and preserve `P4_NATURAL_PAIR_SOURCE_RIGHTS_CANNOT_CHECK` even if all metadata-signal cells reach quota.

No successor provider/query was opened in this checkpoint.

## 7. Verification

`VERIFICATION_RECEIPT_V1.json` recomputes protocol/result payload hashes and file links; validates four query receipts, 4,000 raw rows, 4,000 fail-closed disjointness exclusions, the four exact response hashes, the empty candidate file, the one retained assertion mismatch, the unchanged domain deficits, the immutable Zenodo terminals, and every no-content/no-outcome flag.

Its status is `PASS_STRUCTURAL_INTEGRITY_WITH_RETAINED_TRANSPORT_SCHEMA_CANNOT_CHECK`. That is structural verification of an adverse result, not a positive scientific or source-feasibility result.
