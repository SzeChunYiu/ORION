# P4 Zenodo related-object census V2

**Date:** 2026-08-23  
**Authority:** public metadata source feasibility only  
**Case/model outcomes accessed:** no  
**Files downloaded:** no

## Preserved V1 transport failure

The frozen V1 identity requested an unauthenticated page size of 200. Zenodo
returned HTTP 400 with the provider message that unauthenticated requests may
not exceed 25 records. No census or model outcome ran. The immutable retained
terminal is:

`P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400`

Retained receipt SHA-256:
`433968a0d98c858781b6cd45a48dbd34b12e359dfe479b95ae0b14016c5d398c`.

## Distinct V2 successor

V2 was frozen after disclosing and excluding 162 record identities seen in
outcome-free transport/schema probes. It repairs the API page size to 25,
fixes nine pages per query, binds the actual Zenodo licence vocabulary, requires
public HTTPS file-link evidence, and evaluates the 48-record gate on accepted
publication-typed related identifiers rather than on any relation. These are
mechanics/schema repairs under a new identity; V1 is unchanged.

Protocol SHA-256:
`01c1bb250accfaee4103a162565cd2107515cd306adf690713a5c1372e953d1f`.

## Result

All 72 responses passed the frozen schema checks. Each page returned 25 rows;
there were no within-query duplicates. The candidate file contains 173
query-specific rows corresponding to 98 unique Zenodo records; 38 records occur
in more than one frozen query. Candidate JSONL SHA-256:
`d6f767e88cdc401dd1f7643ed76e4460645fcc3dff9744dc504fed01351c1247`.

| Frozen cell | Raw | Pre-freeze exclusions | Open-licence + public-file | Accepted typed relation | Publication-typed candidate | Gate >=48 |
|---|---:|---:|---:|---:|---:|:---:|
| Earth/environment data | 225 | 25 | 174 | 51 | 37 | no |
| Life/biomedical data | 225 | 26 | 178 | 63 | 44 | no |
| Physical/engineering data | 225 | 32 | 161 | 38 | 29 | no |
| Scientific-software data | 225 | 31 | 169 | 45 | 30 | no |
| Earth/environment software | 225 | 25 | 183 | 122 | 6 | no |
| Life/biomedical software | 225 | 26 | 181 | 156 | 10 | no |
| Physical/engineering software | 225 | 30 | 172 | 104 | 10 | no |
| Scientific-software software | 225 | 38 | 170 | 113 | 7 | no |

The data route is near but below quota in every domain (29--44). The software
route has many typed relations but few publication-typed targets (6--10), so
its bottleneck is article linkage rather than record or relation availability.
The preserved V2 terminal is:

`P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER`

Result SHA-256:
`683c2ec074c04d92276dcd185f3c06750f6e1dd9817310ecd6e879f87f99e62d`.

## Scientific consequence and next discriminator

Zenodo alone cannot instantiate the registered four-domain M5/M6 cells under
the frozen 48-signal gate. The failure is informative and must not be converted
into a positive case result. The next source-expansion iteration should keep
the domains, mechanisms, quota and linked-publication requirement unchanged,
and test disjoint metadata/content routes:

1. DataCite relation metadata for publication--dataset links, followed by exact
   repository-record licence and byte binding;
2. Software Heritage/Codemeta or repository release DOI linkage for M6, with
   exact code licence and immutable archive identity;
3. PMC Open Access linked records for protocol/result, correction and
   supplement cells;
4. external adjudication only after a complete 32-cell source frame exists.

Public metadata and file-link evidence do not establish natural-pair identity,
linked-object rights, eligibility, case gold, scientific performance,
confirmation, provider generality or ORION superiority.
