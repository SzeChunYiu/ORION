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
- PDF SHA-256: `80850e789d396dceaa0a28d85446dd1ff0ffe7666c4bc5d2f50f3dc563dcfadd`
- source-PDF byte match: exact

The manuscript availability section now states the scientific access and
licensing conditions without printing internal identifiers. The source-only
private protocol comment was also removed. Filing-facing cover-letter and
availability placeholders were replaced with plain author instructions.

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

- source archive SHA-256: `0ad10b8d6abcd1a72f56826e20b5a5c21f093edbc87597e7c217a1e28408e662`
- review-resource archive SHA-256: `5c89e144e4a495c98d11afda6f9d73a01c5638974c61b6a90861273564f16460`
- submission manifest SHA-256: `b0173782363fd90ae3022aa0223d17f993a60930f64d12c57f2bc590807c4b7f`

These identifiers are audit-only and must not be copied into manuscript prose.
