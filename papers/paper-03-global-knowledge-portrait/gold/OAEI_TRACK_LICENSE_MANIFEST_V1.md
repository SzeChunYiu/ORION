# OAEI_TRACK_LICENSE_MANIFEST_V1 — licence and selection record

- **Canonical artifact:** `OAEI_TRACK_LICENSE_MANIFEST_V1.json` (same directory). JSON is authoritative.
- **Frozen (UTC):** 2026-08-24T10:20:24Z — `FROZEN_LICENSE_AND_SELECTION_RECORD__EXECUTION_NOT_PERFORMED`, `outcome_accessed: false`.
- **Issue:** SzeChunYiu/ORION#1086 (P3 boxes 1 and 3).
- **Checker:** `check_oaei_track_license_manifest_v1.py`; **tests:** `tests/unit/p3/test_p3_oaei_track_license_manifest.py`.
- **Builds on:** `development/p3-selective-envelope-harm-successor-v4-2026-08-23/SOURCE_FAMILY_RIGHTS.json`
  (audit `P3.V4.SOURCE.FAMILY.RIGHTS.METADATA_ONLY.2026-08-23`), which opened no dataset payloads,
  no reference alignments, no matcher outputs, and performed no execution. This manifest inherits
  that boundary.

## Selection state

| Source | Role | Licence | Status |
|---|---|---|---|
| bench23 (Zenodo 15827289) | primary benchmark | **CC-BY-4.0 — VERIFIED** 2026-08-24 via `https://zenodo.org/api/records/15827289` (`metadata.license.id`) | SELECTED; not downloaded |
| OAEI 2025 Conference ra1 | natural-pair track (primary candidate) | **CANNOT_CHECK** (no explicit licence on track or OntoFarm pages) | pointer-only, unselected |
| OAEI 2025 Biodiv | natural-pair track (secondary) | **CANNOT_CHECK** + advertised archive 404 | pointer-only, unselected |
| SemTab 2025 | licensed fallback | **CANNOT_CHECK** (2025 page carries no licence statement) | NOT_ACTIVATED |

bench23 record facts bound in the JSON: DOI `10.5281/zenodo.15827289`, created 2025-07-07,
`bench23.zip` 1,034,779 bytes, published checksum **MD5 only** (`5c70ace8…e762`) — SHA-256 must be
computed locally at download time before any scoring run. The record description confirms bench23
is the systematic alteration of **one seed ontology** (bibliographic domain), which is exactly why
a natural-pair track is mandatory alongside it (P3 box 3).

## Exclusions (P3 box 1 rule: exclude UMLS/eClass or registration-restricted unless authorized)

- **OAEI LargeBio (legacy 2015)** — `EXCLUDED__UMLS_ASSOCIATED_UNAUTHORIZED`: UMLS-derived
  references; SNOMED CT `LICENCE_REQUIRED`; UMLS needs an individual licence/UTS account. Inherited
  audit bundle terminal: `NOT_LAWFUL_PUBLIC_PANEL_READY`.
- **OAEI Bio-ML** — `EXCLUDED__UMLS_ASSOCIATED_UNAUTHORIZED__VIA_CAMPAIGN_SUCCESSION`: OAEI 2025
  states Bio-ML supersedes LargeBio/Phenotype. Bio-ML was **not** separately audited; re-audit
  before any reversal.
- **eClass** — `EXCLUDED__ISSUE_DIRECTIVE` (issue box 1); also not among the seven audited
  campaign families, so no separate presence/licence record exists.

## Not selected, not excluded

- **Anatomy** — inputs CC BY 4.0, reference provenance MGI-derived (Ringwald/Hayamizu, later
  Beisswanger). It is **not UMLS-associated** in the bound audit and is not excluded under the
  UMLS rule; it is blocked solely by the absent explicit reference-alignment licence and the
  missing snapshot-to-upstream mapping.
- **MultiFarm** (translation derivative of Conference; collapses for replication), **Knowledge
  Graph** (gold explicitly partial), **Common KG** (no repository/track-level licence; gold
  explicitly partial) — all `CANNOT_CHECK`, pointer-only to the inherited audit.

## Scoring framework

MELT — **MIT** (LICENSE sha256 `6259170d…64cd` at audited head `db893731`), execution status
`NOT_EXECUTED_IN_REPOSITORY`.

## Non-bypass boundaries

1. Licence verification precedes download; nothing listed here has been downloaded or opened.
2. A CANNOT_CHECK licence terminal is never upgraded by inaction or upstream-licence adjacency;
   only new explicit evidence upgrades it.
3. Natural-pair selection requires the recorded licence unblock; bench23 alone cannot satisfy
   the natural-pair requirement.
4. Incomplete reference alignments never make absent entity pairs true negatives (issue
   boundary); this manifest grants no labelling semantics.
