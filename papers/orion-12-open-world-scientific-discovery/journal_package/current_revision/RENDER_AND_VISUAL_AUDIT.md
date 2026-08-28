# Render and page-level visual audit — ORION-12 current revision

**Subject:** `journal_package/current_revision/manuscript.pdf`, compiled from
`manuscript/main.tex` at the revision recorded in this package's `SHA256SUMS`.
**Date:** 2026-08-28.
**Auditor:** automated agent pass; the record below states exactly what was
inspected and by what means, so a human reviewer can judge its weight.

## 1. Build

Engine: Tectonic (XeTeX), six passes to bibliography convergence.

The repository also tracks a working PDF at `manuscript/main.pdf`, which is
the pinned `latexmk` rebuild that `manuscript-clipping-audit` requires. It is
a different engine on the same source and lands on the same 47 pages. That
file was refreshed from the pinned rebuild in this pass; the audit below was
performed on the Tectonic render archived beside this document.

| Property | Value |
|---|---|
| Pages | 47 |
| Undefined references or citations | 0 |
| Multiply-defined labels | 0 |
| Overfull boxes | 0 |
| Underfull boxes reported as errors | 0 |
| Build exit status | 0 |

The previous packaged PDF renders an earlier manuscript at a different length.
This render is taken from the current source, not from that record.

## 2. Page-level visual inspection

All 47 pages were rasterised at 50 dpi and inspected as three contact sheets
(pages 1--16, 17--32, 33--47). Every page was viewed. Findings:

- **Front matter (p1).** Title, abstract and keywords set correctly; abstract
  fits its page with no spill.
- **Body flow (p1--p34).** No stranded section headings, no page whose only
  content is a heading, no blank page, and no text crossing the margin.
- **Figure 1, pipeline diagram (p3).** Renders in full, inside the text block,
  with its caption attached.
- **Theorem and proposition environments (p5--p14).** Numbering runs in
  sequence; no proof environment is split in a way that orphans its closing
  square.
- **Tables (p20, p25, p26).** All three render inside the text block with
  headers and rules intact; none overflows the column.
- **Availability section (p35--p38).** Dense monospace paths and digests break
  at legal points, which is what the `xurl` and `\idt` setup in the preamble
  exists to guarantee. No line runs past the margin.
- **References (p42--p44).** All entries resolve; no `?` markers.
- **Figures 2--6 (p45--p47).** The discovery-pipeline diagram, the two
  recall/precision plots, the Jaccard heatmap and the terminal-classification
  bar chart all render with axes, labels and captions.

No render defect was found.

## 3. Claim audit against the manuscript

`scripts/check_claim_ledger.py --check` reports the ledger clean with zero
violations at this revision. That check is stronger than string matching: for
every ledgered sentence it re-derives the bound numbers from the cited evidence
artifacts and fails if a manuscript number no longer matches the evidence it
cites, and it hard-fails any outcome asserted in the abstract or conclusion
with no ledger entry behind it.

Four ledger locator sentences were re-verified during this pass after a
house-style rewording, and one claim retains its two bound SHA-256 digests
inline because for that claim the digest binding is the claim.

## 4. What this audit does not establish

It does not establish that the scientific content is correct, and it does not
grant submission authority. The package's recorded terminal is unchanged and
the historical packaged PDF remains a superseded record. Whether this revision
is authorized for submission is a separate decision, made by a person, and this
document is evidence for that decision rather than a substitute for it.
