# P4 DataCite M5 disjoint-provider census V2

**Date:** 2026-08-23

**Authority:** public DataCite metadata source feasibility only

**Mechanism:** `M5_ARTICLE_TO_DATA_DOCUMENTATION`

**Files, descriptions, cases, labels, and model outcomes accessed:** no

**Exact scientific terminal:** `P4_NATURAL_PAIR_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_SOURCE_UNIVERSE`

## 1. Distinct mechanics successor and immutable negatives

V2 is a distinct mechanics successor. It does not modify or reinterpret:

- Zenodo V1: `P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400`;
- Zenodo V2: `P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER`;
- DataCite V1: `P4_DATACITE_M5_CENSUS_V1_CANNOT_CHECK_TRANSPORT_OR_SCHEMA`.

Before V2 was frozen, every identity exposed by the four DataCite V1 responses was bound into `P4_DATACITE_M5_V2_PREFREEZE_DISCLOSURE.json`: 4,000 query-specific DOI rows, 3,479 unique DOIs, and 468 DOIs occurring in more than one V1 query. Every disclosed DOI was excluded before V2 eligibility counting.

Disclosure payload SHA-256: `af79d50ebac3c5282dc9ac19c3c7d6df3d84103d8df34d9a3921e2a99d31cf73`

Disclosure file SHA-256: `18dd9ca008aa4e02110a61c6157715b57cd2a7b2c33729db8a3c2ccda839cdab`

V2 made only the predeclared mechanics repairs:

1. added the DataCite `client` relationship to the sparse field set;
2. kept descriptions, subjects, funding, XML, metrics, and content bytes out of the response;
3. applied the existing Zenodo publisher/prefix exclusion at query and row levels;
4. used the exact Markdown-linked documentation assertion `OpenSearch [query string syntax]`;
5. retained the four domains, M5 identity, 48 gate, exact rights declarations, HTTPS `contentUrl`, accepted typed relations, publication target types, and all nonclaims unchanged.

Protocol payload SHA-256: `982ee0a2ecf7a64048e2c32c84c4c8c49867b31ecd7e2eeff99bc9aded1023fb`

Protocol file SHA-256: `2f2b78793781fca66a1b614f8c4c4df2e100e6ed2467badcf84fbbf79021a62a`

## 2. Mechanics result

The mechanics repair succeeded in its narrow sense:

- all four authoritative evidence pages passed every frozen assertion;
- all four API responses returned HTTP 200;
- all four response schemas and page-integrity checks passed;
- all 4,000 rows carried the requested client relationship (`missing_client_exclusions = 0`);
- after excluding 968 V1-disclosed DOI rows, 3,032 rows passed provider/root disjointness.

This is a transport/schema result only, not a scientific positive.

| Frozen M5 cell | Reported search upper bound | Raw | V1 disclosed excluded | Provider-disjoint | Exact CC BY 4.0/CC0 declaration | HTTPS `contentUrl` | Publication-typed admitted | Response SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Earth/environment | 1,100,442 | 1,000 | 299 | 701 | 678 | 0 | 0 | `c60bb9f374cb8c8714dd6857177c22261627fa0a7ac58227a42f09a3120f3011` |
| Life/biomedical | 2,405,738 | 1,000 | 424 | 576 | 525 | 0 | 0 | `47c164e88c1403788502a8c9903449acaee2192275c9c659806ca956cf0d108e` |
| Physical/engineering | 19,383,977 | 1,000 | 132 | 868 | 762 | 0 | 0 | `041ad76f5659a4f19971588a37f3dab9661fa709e87314cfb65ea407fa09d01d` |
| Scientific software | 456,229 | 1,000 | 113 | 887 | 754 | 0 | 0 | `eab2efc83cecdf88ec23dde4339ad2dc11216534dc4ca20b92999d0ac9386e6c` |
| **Total** | — | **4,000** | **968** | **3,032** | **2,719** | **0** | **0** | — |

Response byte counts were respectively 3,166,695; 1,669,365; 5,369,964; and 2,850,710 bytes.

## 3. Scientific negative and exact interpretation

The unchanged next gate required at least one HTTPS `attributes.contentUrl` after exact rights-declaration screening. None of the 2,719 sequentially rights-eligible metadata rows exposed such a value. Consequently no row reached accepted-relation or publication-target screening and no candidate was admitted.

The zero relation count is therefore a **not-reached sequential count**, not evidence that the returned DOI records lacked typed publication relations. Likewise, the zero candidate count is bounded to these four frozen most-recent pages; it is not a global claim about DataCite or repository availability.

`P4_DATACITE_M5_CANDIDATES_V2.jsonl` is the deliberate zero-byte candidate set with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Result payload SHA-256: `e31c2fe27062ce02253cda0945e0eece859ae60bd9c18514397cc60690ac99bb`

Result file SHA-256: `a8e65f7cfe7f2cdaed413ece8f14b9072f3b283eb943e76aa080d742939e156f`

## 4. Unchanged M5/M6 gate state

| Domain | Zenodo V2 M5 | New DataCite V2 | Combined M5 | M5 deficit to 48 | Preserved M6 | M6 deficit to 48 |
|---|---:|---:|---:|---:|---:|---:|
| Earth/environment | 37 | 0 | 37 | 11 | 6 | 42 |
| Life/biomedical | 44 | 0 | 44 | 4 | 10 | 38 |
| Physical/engineering | 29 | 0 | 29 | 19 | 10 | 38 |
| Scientific software | 30 | 0 | 30 | 18 | 7 | 41 |

No unchanged M5 cell, no unchanged M6 cell, and not the eight-cell conjunction passes the 48-signal gate.

## 5. Rights and `CANNOT_CHECK` boundary

DataCite metadata is bound to the cited CC0 policy. The `rightsList` values counted above remain repository/depositor declarations; they do not independently establish uploader authority or exact file scope. An HTTPS content URL would establish visibility, not permission. DataCite relations remain deposited identity assertions, not natural-pair adjudications.

Accordingly:

- metadata permission: `DATACITE_METADATA_CC0_ROOT_BOUND`;
- dataset content permission: `DECLARED_PERMISSION_AUTHORITY_UNVERIFIED`;
- linked publication rights: `CANNOT_CHECK`;
- natural-pair eligibility: `NOT_ADJUDICATED`;
- scientific performance/confirmation/provider generality: not assessed.

The exact source-signal terminal is therefore the shortfall terminal, not a positive or execution-ready result:

`P4_NATURAL_PAIR_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_SOURCE_UNIVERSE`

## 6. Narrow next research discriminator; not executed here

The retained failure identifies a provider-bound mismatch: DataCite's sparse DOI-list metadata can bind DOI/client/rights/relation declarations, but the frozen `contentUrl` availability signal is absent in these pages. A future, separately frozen successor must not simply drop that gate. It must instead bind a repository-specific public-file manifest or exact repository-record API to each DataCite DOI, preserve the same rights/authority checks, and only then evaluate the already frozen publication relation. If exact file identities and root permissions remain unavailable, the cell stays `CANNOT_CHECK` or shortfall.

No additional provider route or natural-pair adjudication was executed here.

## 7. Verification

`VERIFICATION_RECEIPT_V2.json` verifies the V1 exclusion disclosure, immutable V1 terminals, V2 payload/file links, four exact response hashes, 4,000 raw rows, 968 prefreeze exclusions, 3,032 provider-disjoint rows, 2,719 exact-rights declarations, zero HTTPS content URLs, zero candidate rows, unchanged M5/M6 deficits, and every no-content/no-outcome boundary.

Its status is `PASS_STRUCTURAL_INTEGRITY_WITH_RETAINED_SOURCE_SIGNAL_SHORTFALL`. Structural consistency does not convert the negative source result into eligibility or evidence.
