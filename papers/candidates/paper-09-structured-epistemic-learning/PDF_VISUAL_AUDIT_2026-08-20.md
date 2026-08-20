# P9 TMLR PDF visual audit — 2026-08-20

Status: `PASS_VISUAL_REVIEW_BRANCH_ARTIFACT`

Authority: publication/rendering receipt only; no scientific-claim authority.

## Exact artifact identity

- review branch head: `9d12f3a36051f54d4a8a01e2ba61a473d9c32d50`
- GitHub Actions workflow: `p9-tmlr-pdf`
- workflow run: `32340331816`
- artifact id: `9396990591`
- artifact name: `p9-tmlr-pdf-022cd7ce8dd914b8a024e757ddc5fc56808a2a44`
- artifact archive digest: `sha256:983e2cc82c9eb4ee6fa43ba1ea7877715f9bcc2e89639b053f12364702a94441`
- rendered PDF path inside artifact: `manuscript/main.pdf`
- PDF bytes: `322886`
- pages: `8`

The workflow regenerated the paired D1 analysis, official-result verification, evidence summary, result macros, headline tables and manuscript audit before compiling the PDF. It then required resolved references/citations, no overfull boxes, the expected title, no pending receipt marker, and blank rendered PDF Author metadata.

## Manual render review

The exact workflow artifact was downloaded and rendered page-by-page at 160 DPI after the workflow passed.

Observed:

- pages 1–8 render without clipped text, overlaps, black squares or broken glyphs;
- title/abstract and section hierarchy are readable at normal page scale;
- TMLR review header is consistent across pages;
- source remains anonymous and rendered PDF Author metadata is blank;
- Table 1 (M1 view ceilings) fits the text width;
- Table 2 (D1 whole-domain transfer) fits the text width and all numeric columns are readable;
- Table 3 (paired protected-case effects) fits the text width, including 95% intervals, discordant wins–losses and McNemar values;
- the D1 post-hoc wording remains adjacent to the table and explicitly says the analysis is not a new preregistered endpoint;
- equations and math symbols render correctly;
- bibliography entries on page 8 are readable and remain inside the page bounds;
- no visually material spacing/layout defect was found.

## Boundary

This receipt establishes that the exact review-branch PDF artifact passed automated structural checks and a manual visual rendering audit. It does not claim that the branch is already merged to `main`, that TMLR has accepted the submission, or that any stronger LLM/native-Lean result outside the bounded P9 paper has been established.
