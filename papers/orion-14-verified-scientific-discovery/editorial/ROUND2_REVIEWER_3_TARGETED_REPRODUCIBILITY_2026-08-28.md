# ORION-14 targeted re-review — Reviewer 3: reproducibility, anonymity and exact PDF

**Ownership:** E14-C06, E14-C07, E14-C08, shared E14-C05  
**Subject PDF SHA-256:** `d9b8fbf3b9f16a7c35b478a810121d8803ae2d848a7817d0cff33e6d47126110`  
**Mode:** simulated targeted pre-submission re-review plus page-level production QA; not journal peer review

## Exact build binding

The subject PDF was taken from GitHub Actions run `33167703059`, which rebuilt `manuscript/main.tex` from source revision `b1c0d26096a822e8294b8b60dbbbec3c4e73bc5d` with Ubuntu latexmk 4.83, pdfTeX 1.40.25 and `SOURCE_DATE_EPOCH=1787916820`. The tracked `manuscript/main.pdf` and `journal_package/manuscript.pdf` are byte-identical.

The clean workflow intentionally failed only at its pre-update equality gate because the then-tracked PDF was a local Tectonic render; rebuild, clipping audit and artifact upload had already succeeded. Replacing the tracked PDF with the uploaded clean build closes that mismatch rather than suppressing it.

## Every-page visual and surface QA

All 19 pages were rendered and inspected, first as a complete contact sheet and then at page scale for the title/abstract, proof pages, all five figures, three tables, adverse-evidence page, Availability/Conclusion and final reference pages.

- geometry/clipping audit: 0 findings on both PDF copies;
- fonts: all embedded;
- metadata: anonymous author, correct title/subject/keywords, no JavaScript or forms;
- figures: five 1440 x 900 rasters render cleanly at about 222 ppi with legible labels, axes, whiskers and captions;
- tables/equations/references: no truncation, overlap, missing glyph or broken citation observed;
- text extraction: 19 page breaks and all headline carriers present;
- adverse evidence: V2 H3 saturation and excluded 39-case arm remain visible;
- surface scan: no author name/email/account handle, public repository ownership, local path, branch/issue/workflow chronology or unresolved placeholder wording in reader-facing PDF text.

The official initial-review `MM`, `YYYY` and `XXXX` fields remain because the TMLR template reserves their replacement for camera-ready preparation.

## Anonymous artifact

The exact review ZIP has SHA-256 `ec842a56dc49b7363de847e7c015fa2730c810a04652c5e440d9a72af4b665a3`, 10 members and 100,955 uncompressed bytes. Two clean builds were byte-identical; ZIP integrity and the standalone headline verifier passed. Identity/path scanning found no author-linked surface. The archive exposes safe aggregates and checksums, not protected gold or raw traces.

## Reproducibility boundary

The package supports public checking of released aggregates, figures, exact P4-X counts and interpretation guards. Separate project code paths are not called external replication. Protected scoring cannot be reconstructed from the blind archive, by design, and this limitation is explicit.

## Decision

E14-C06, E14-C07, E14-C08 and Reviewer-3's part of E14-C05 satisfy their frozen resolution tests. The exact current PDF and supplement are fit for blind filing. Human OpenReview profile, author/affiliation/ORCID and declarations remain upload-time inputs and do not alter the audited anonymous bytes.

**Targeted recommendation:** close all owned concerns.
