# Build and visual QA

**Date:** 2026-08-28  
**Canonical source:** `submission_tmlr/main.tex`  
**Canonical PDF:** `submission_tmlr/main.pdf`  
**Toolchain:** Tectonic 0.15.0_5 with official TMLR style pinned at `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992`

## Build

- Canonical source compiled with bibliography resolution.
- Deterministic source archive was unpacked into a new empty directory, its neutral manuscript entry renamed to the conventional build name, and compiled successfully.
- Clean-build PDF: 10 pages.
- Required text present: 53-row null panel, 39,489-case zero-mismatch census, anonymous authorship and the no-rate boundary.
- No unresolved citation token was found.
- The only layout warning was a sub-point one-point table-box excess; inspection found no clipping or overlap.

## Hyperlink-border QA

The canonical source uses `hidelinks` and a zero PDF border. No coloured hyperlink rectangles are visible.

## Page-by-page inspection

All 10 pages were rendered to PNG and individually inspected at 120 dpi.

| Page | Content | Result |
|---:|---|---|
| 1 | title, disclosure, abstract, introduction | pass |
| 2 | introduction and related work | pass |
| 3 | methods and scored coordinates | pass |
| 4 | lifecycle schematic and chronology | pass |
| 5 | all three scientific questions | pass |
| 6 | complete case and alignment tables | pass |
| 7 | retained-event table and discussion | pass |
| 8 | discussion, limitations and availability | pass |
| 9 | ethics, conclusion and references | pass |
| 10 | references | pass |

No text, figure, table, footer, citation or page number is clipped or overlapped. Fonts and equations are legible. The lifecycle schematic is fully contained within the text block.

## Reader-surface audit

The exact PDF, source, source-archive payload and entry names, review-archive payload and entry names, cover letter and availability statement were scanned. No internal programme/paper/study identifiers, internal repository paths or filenames, project hashes, branch/issue/pull-request/continuous-integration history, or machine authority/release strings were found. The anonymous files contain no author identity.

**Result:** pass.
