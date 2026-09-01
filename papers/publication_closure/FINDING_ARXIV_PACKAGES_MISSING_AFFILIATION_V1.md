# The landed arXiv packages are clean except for one field

Five assembled arXiv submission packages now sit on `main` (landed from a branch that had been open since 25 August). Their rendered front matter is the cleanest in the corpus.

| paper | title as rendered |
|---|---|
| ORION-01A | Zero-Sum Deletion Normal Forms for a Multi-Tag Pauli Grammar |
| ORION-01B | Zero-Sum Deletion Complexity and Support-One Normalization in a Pauli Model |
| ORION-02 | Low-Order Decision Certificates and Value Limits in a Pauli-String Partition Model |
| ORION-03 | Typed Evidence Licenses for Finite Positive Rule Graphs |
| ORION-04 | Conditional Davenport Corridors and Saturated Obstructions in C5³ |

No internal labels, no version suffixes, no catalogue numbers, no provenance banners. Each carries `Sze Chun Yiu` and `sze-chun.yiu@fysik.su.se`, a real title and a date. Each package holds a `.tex`, a `.pdf`, an arXiv source zip, a journal source zip, a cover letter, a submission checklist and ancillary verification scripts.

**ORION-02, ORION-03 and ORION-04 are among them.** All three were recorded in this session's readiness table as having no LaTeX source and being unbuildable.

## The one defect

All five omit the affiliation. The source reads:

```latex
\author{Sze Chun Yiu\\\texttt{sze-chun.yiu@fysik.su.se}}
```

The canonical block in `AUTHOR_IDENTITY_V1.json` is:

```latex
\author{Sze Chun Yiu\\Independent Researcher\\\texttt{sze-chun.yiu@fysik.su.se}}
```

Name and email are present; `Independent Researcher` is missing from all five rendered PDFs.

## Why it was not repaired here

Editing the `.tex` is trivial. Rendering it is not: no build path exists for these packages. `paper-writeback-source-gate.yml` compiles the paper-programme sources (P1, P2), not these; neither `pandoc` nor `pdflatex` is installed on the test host; and no `build.sh` or Makefile sits beside the sources.

Changing the `.tex` alone would leave the source stating an affiliation that the committed PDF does not, and the arXiv and journal source zips would still contain the old file. That is the divergence shape this corpus already guards against, and it would convert five clean packages into five inconsistent ones.

## What would close it

Any one of: a CI job that compiles these submission sources; a local TeX toolchain on a machine permitted to run it; or accepting name-and-email as sufficient for these venues, which is a defensible editorial choice rather than a defect, since arXiv does not require an affiliation line in the PDF.

The third option is worth weighing before building infrastructure for the first.
