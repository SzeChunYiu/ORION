# Reader-surface correction — 2026-08-28

## Reason for correction

The prior eight-page PDF (`aff2be33f907a21549776ed888364f04351b0fb8e481087e3b7936516aef0a4b`)
was not reader-surface clean. Its Data and code availability section printed two
archive digests. That contradicted the author's rule that internal identifiers,
hashes, repository transport and machine terminals must not appear in
manuscript-facing text. The earlier zero-leakage statement is therefore
withdrawn for that PDF.

This is a surface-only correction. It changes no scientific value, claim,
comparison, limitation, citation or editorial terminal. The digests remain in
the private evidence and package manifests where they serve integrity checks.

## Current filing PDF

- title: *Coordinate-Governed Mapping of Source-Local Scientific Projections*
- pages: 8
- PDF SHA-256: `7137a9a9d8c88c0b64f69550596d000db5f6bf9d267c4b0852e0e94b87ce6176`
- source-PDF byte match: exact

The manuscript availability section now states the scientific access and
licensing conditions without printing internal identifiers. The source-only
private protocol comment was also removed. The conclusion now restates the
confirmatory effect and three-valued evidence boundary explicitly. Filing-facing
cover-letter and availability placeholders were replaced with plain author
instructions.

## Verification

- exact PDF text scan: zero paper/study codes, machine terminals, repository
  paths, filenames, hashes, branch/CI/issue/PR history or internal release
  states;
- every-page visual inspection: all 8 pages inspected after the correction;
  no clipping, overlap, broken references, sparse spill page or final-page
  defect observed;
- PDF metadata: real title and author present;
- bounded-publication-track check: pass;
- separate-implementation replay: pass;
- deterministic package rebuild and checksum verification: pass.

## Current package bindings

- source archive SHA-256: `e81720d03d1b05b92d45c6c4bbb3111b1566ff4845fb1aa2c3b1c51a45e21c99`
- review-resource archive SHA-256: `02aad4b045c04a66da61778e3429f7fc4dc74a97b741024640dff801c065c983`
- submission manifest SHA-256: `9cc8b2657551ecd38d3f7b68549175e65b9222aa8d3644eb96894334027b3918`

The generic archives pass content and entry-name scans for project codes, transport metadata, hashes and machine release strings. The earlier unsanitized archives are retained only as private audit evidence. These identifiers are audit-only and must not be copied into manuscript prose.
