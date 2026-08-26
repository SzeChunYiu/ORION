# ORION-19 TMLR venue audit V1

Checked: **2026-08-19** against current official TMLR/JMLR sources.

## Official sources

- TMLR Author Guide: `jmlr.org/tmlr/author-guide.html`;
- TMLR Editorial Policies / Action Editor guidance;
- official JMLR organization repository: `JmlrOrg/tmlr-style-file`.

## Current standard-PDF requirements relevant to ORION-19

1. TMLR uses **double-blind review**; the submitted manuscript must be anonymized.
2. Standard submissions must be **PDF files generated with the TMLR LaTeX stylefile and template**.
3. The unmodified official style is a format gate; format violations / non-anonymized submissions can be desk rejected.
4. A submission PDF may include an appendix after references; reviewers are not required to read it.
5. Supplementary material may include supporting data/code/video, subject to TMLR size/format rules and anonymization; reproducibility-supporting material is explicitly encouraged.
6. The authors must also comply with TMLR editorial, ethics, conflict, OpenReview-profile and disclosure requirements at submission time.
7. TMLR also has a newer Beyond-PDF route, but ORION-19 is currently targeting the **standard PDF route**; no interactive-format requirement is introduced.

## ORION-19 package consequence

Before readiness:

- vendor/use the then-current official `tmlr.sty`/template **without modification**;
- keep author identity anonymous in the review PDF and supplementary materials;
- ensure the historical ORION repository/preprints do not create an explicit identity link in the submitted anonymized manuscript;
- compile the final ORION-19 source through the official style rather than the current drafting `article` wrapper;
- include only result artifacts and supplements that are actually accessible/reproducible;
- run final PDF visual/citation/anonymity checks after all official result values are frozen.

## Timing rule

This audit freezes the venue requirements early, but **style conversion happens after M1/A2-A4/D1 result integration** so layout reflow cannot pressure scientific wording or encourage premature result insertion.

Recheck the official TMLR Author Guide and style repository immediately before the final package freeze. If requirements changed materially, update this receipt and the submission package; do not silently rely on this 2026-08-19 snapshot.
