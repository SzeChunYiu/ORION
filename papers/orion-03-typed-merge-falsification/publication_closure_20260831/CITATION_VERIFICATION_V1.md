# ORION-03 citation and literature-closure record

**As of:** 2026-08-31  
**Machine record:** `CITATION_METADATA.json`  
**Refresh command:** `python verify_references.py --output CITATION_METADATA.json`

## Source roles and publication state

| Keys | Role | Publication state | Verification |
|---|---|---|---|
| `doyle1979`, `martins1988`, `agm1985` | truth maintenance and belief revision foundations | journal versions of record | DOI, title, authors, year and bibliographic fields checked against Crossref |
| `kifer1992` | generalized annotated logic programming | journal version of record | Crossref/OpenAlex identity and status verified; OpenAIRE/CORE abstract inspected and fingerprinted in `audits/kifer1992-primary-content.json` |
| `green2007`, `cheney2009`, `bourgaux2022`, `abokhamis2022`, `bonatti2011` | semiring/recursive/trust provenance and database-provenance foundations | peer-reviewed proceedings or journal versions of record | Crossref verified |
| `buneman2002`, `meliou2010` | deletion propagation and database causality | peer-reviewed proceedings/journal versions | Crossref verified |
| `thapa2026minimal` | closest current work on minimal supports, causality and deletion robustness in recursive Datalog | arXiv v2; author metadata states accepted for RuleML+RR 2026 | Official arXiv metadata and full abstract checked; retained visibly as non-final proceedings metadata |
| `thapa2026stratified` | closest current boundary work for stratified negation | preprint only | Official arXiv v1 metadata and full abstract checked; no peer-reviewed version located by the search end date |
| `cutler2024` | Cedar language and native authorization context | journal version of record | Crossref verified |
| `rfc5280` | X.509 validation profile | official RFC/DOI primary record | Crossref verified |
| `openssl364` | exact third-party software/test-corpus source | official tagged source release | tag, commit and tarball digest bound in the evidence packet |

## Claim–source audit

- The manuscript credits fixed-point, proof-tree, truth-maintenance, annotated-provenance, deletion and causality machinery as prior work.
- The two closest 2026 works are included rather than hidden; their preprint/accepted status is explicit.
- No project-internal document carries an external novelty claim.
- The OpenSSL citation supports source identity only. It does not support security, deployment or prevalence claims.
- The RFC supports X.509 context; the native receipts, not the RFC, support the measured task outcomes.
- The Kifer and Subrahmanian citation is supported at the abstract level for its annotation-domain and logic-programming donor role. The audit does not claim full-text verification of unrelated theorems or applications.
- No citation is used in the abstract, consistent with the target instruction.

**Decision:** `PASS__METADATA_AND_CLAIM_ROLES_VERIFIED`. Future corrections, retractions or final publication of the two frontier sources require refresh before an actual later filing.
