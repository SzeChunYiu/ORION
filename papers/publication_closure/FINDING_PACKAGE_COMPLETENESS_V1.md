# Submission-package completeness across the actionable papers

Measured by listing what each paper's submission directories actually contain, after a first pass using `find` name patterns produced two wrong answers in opposite directions.

## What exists

| paper | package | contents |
|---|---|---|
| ORION-07 | `submission_tmlr/` | **complete** --- cover letter, availability statement, author filing checklist, anonymous source and review zips, `tmlr.sty`/`.bst`, compiled PDF |
| ORION-09 | `submission*/` | cover letter, availability, metadata, source zip |
| ORION-12 | `journal_package/` + `submission/` | manifests, cover letters, availability, source zip |
| ORION-13 | `journal_package/` | manifests, availability, cover letter, source zip |
| ORION-11 | `journal_package/` | `MANIFEST.json`, `COMPILE.md`, `LICENSE.md`, `SHA256SUMS`, `CLAIM_PDF_AUDIT.md`, `manuscript.pdf` |
| ORION-15 | `journal_package/` | same shape as ORION-11 |
| ORION-14 | --- | cover letter and availability present, no assembled package |
| ORION-10 | `journal_package/wave1_current/` | source and review zips, cover letter, manifest, visual audit |
| ORION-06 | --- | cover letter only |
| **ORION-08** | `submission_tmlr/` | **scaffold only** --- `build_tmlr_source.py`, `tmlr_pandoc_template.tex` |

## ORION-08 has no package

Its `submission_tmlr/` contains two files: a build script and a Pandoc template. There is no cover letter, no availability statement, no source archive, and no compiled submission PDF. The build script's own docstring describes it as preparing Markdown for the TMLR wrapper --- it is the machinery for producing a package, not a package.

This matters because ORION-08 was called the paper nearest to filing early in this session. That judgement was made from the presence of a `submission/` directory, which holds `independent-replay-v1` and `literature-closure-v1` --- evidence subdirectories, not submission materials. It was corrected once already on author-block grounds. It is less ready than either assessment implied, and ORION-07 --- not ORION-08 --- is the paper with a complete TMLR kit.

## Two measurement errors, in opposite directions

The first pass used `find` with name patterns (`*cover*letter*`, `*source*.zip`, `*SUBMISSION_MANIFEST*`).

- It reported **0** for ORION-11 and ORION-15, which both have full `journal_package/` directories. The patterns did not match `MANIFEST.json` or `manuscript.pdf`.
- It reported **0** for ORION-08, which was right, but for the wrong reason --- and the same run reported a `submission_tmlr/` directory existing, which invited the assumption that a package was there.

A name-pattern search answers "does a file matching this string exist", not "is this package complete". The reliable method was listing the directories and reading what is in them.

## Actionable

ORION-08 needs a package assembled. ORION-07's `submission_tmlr/` is the working template for the same venue, and ORION-08 already has the build script that produces the source form. ORION-06 and ORION-14 need assembly from partial materials.
