# ORION-14 anonymous review-artifact manifest V1

Tracking: #1609 / PR #1610  
Purpose: bind the exact supplementary archive for double-blind TMLR review without exposing author identity, public-repository ownership, operational history, or protected per-case material.

This is an **internal packaging record** and is not itself part of the blind archive.

## Materialized archive

- Tracked filing object: `journal_package/orion14_anonymous_review_2026-08-28.zip`
- SHA-256: `ec842a56dc49b7363de847e7c015fa2730c810a04652c5e440d9a72af4b665a3`
- Member count: 10
- Uncompressed member bytes: 100,955
- ZIP timestamps: fixed to 1980-01-01 00:00:00
- Build determinism: two clean builds were byte-identical and had the same SHA-256
- ZIP integrity: all members passed `unzip -t`
- Headline verifier terminal: `ANONYMOUS_REVIEW_HEADLINES_VERIFIED`

## Exact blind-package contents

| Blind member | Canonical input or role | Purpose |
|---|---|---|
| `README.md` | generated neutral documentation | states V2/V3/P4-X separation and withheld-material boundary |
| `MANIFEST.json` | generated package manifest | binds neutral member hashes to canonical-source hashes without source paths |
| `SHA256SUMS` | generated member digest list | verifies all other member bytes |
| `verify_headlines.py` | generated standalone checker | checks headline counts, statuses, P4-X tie and independent-implementation boundary |
| `v2_publication_metrics.json` | V2 safe publication metrics | H1/H2 counts, V2 H3 retained negative, comparator and ablation aggregates |
| `v2_family_contrasts.json` | V2 safe family contrasts | per-family public false-promotion aggregates |
| `v3_identifiability.json` | V3 identifiability register | registered exact-axis nuisance-probe outputs |
| `v3_panel.json` | V3 panel result | 30/30 versus 0/30 and 15/30 interface-terminal result |
| `p4x_exact_result.json` | P4-X protected exact-result object | 400/400 versus 250/400, 50/400 and typed 400/400 tie |
| `p4x_independent_verification.json` | P4-X separate implementation receipt | canonical-row and count agreement without importing the execution module |

## Deliberate minimization

An earlier planning inventory proposed copying extensive protocol, custody and development records into the review supplement. The materialized archive instead follows a minimum-sufficient blind-review design: neutral safe aggregates, canonical-source digests, explicit boundaries, and a standalone verifier. This avoids exporting operational identity/history or protected gold while making the manuscript's released finite counts and negative/boundary statements directly checkable. The manuscript describes the scientifically relevant design and custody conditions; the archive does not claim to rerun protected scoring.

## Identity and protection audit

The exact ten-member tree and ZIP were scanned for the author name and email, account handles, public-repository URLs, API/workflow/PR terminology, local user paths, and manuscript-tree paths. No match was found. The archive contains no protected per-case gold, raw traces, secret seeds, credentials, or candidate-hidden fields. File names are neutral, member timestamps are fixed, and the generated manifest records `author_identity_exported: false`.

## Scientific boundary

The archive supports the released **bounded V2, V3 and P4-X aggregate claims**. It does not turn local code-path separation into external replication, disclose hidden gold, establish naturalistic transfer, execute cited authors' external software, or license general scientific-judgement superiority. V2 H3 remains `NOT_SUPPORTED`; V3 remains a distinct terminal/interface-attainability result.

Terminal: `ANONYMOUS_REVIEW_ARCHIVE_MATERIALIZED__DETERMINISTIC__IDENTITY_SCAN_PASS__BOUNDED_AGGREGATE_AUDIT_ONLY`.
