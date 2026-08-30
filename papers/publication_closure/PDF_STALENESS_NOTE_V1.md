# Manuscript PDF staleness: content vs provenance

Checker: `check_pdf_build_staleness_v1.py`. Result: `PDF_BUILD_STALENESS_V1.json`.

## Result on `main`

**22 manuscripts carry a `main.pdf`. 19 FRESH, 0 STALE_CONTENT, 3 provenance-only.**

No manuscript PDF in the programme renders something its sources no longer say.

## Why the distinction exists

The audit workflow derives a manuscript's render epoch from the whole directory:

```
git log -1 --format=%ct -- <manuscript_dir> ":(exclude)<manuscript_dir>/main.pdf"
```

That glob includes files the LaTeX build never reads. These directories hold `.md`
drafts and separately-rendered `FINAL_V*.pdf` documents beside the `.tex` sources, so
editing a companion `.md` moves the epoch and marks `main.pdf` stale even though its
build inputs are untouched.

Three papers sit in exactly that state:

| paper | commits after the PDF | what changed |
|---|---:|---|
| ORION-16 | 1 | `FINAL_V2_1.md`, `FORMAL_CORE_V2.md` |
| ORION-17 | 1 | `DRAFT.md` |
| ORION-18 | 2 | `FINAL.md`, `FINAL_V3.md`, `FORMAL_CORE_V1.md`, `FORMAL_CORE_V2.md` |

In every case **zero `.tex` files changed**, and each `main.tex` `\input`s no `.md` at
all. Confirmed independently by extracting the rendered text: the identifier prefixes in
the render match the current source exactly (ORION-16 `P6.` 2 in render and 2 in source;
ORION-17 zero in both; ORION-18 `P8.` 1 and 1). The renders are correct.

These three date to 2026-08-27, when the R0 namespace commit `3a1a83178` committed the
PDFs and two later commits — `0deff0ad4` and `68a652f70` — repaired R0's damage in
Markdown only. One of those repairs actually *restored* `P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`
from an R0-rewritten `ORION-18.` form, so the later commit moved the epoch while making
the tree more correct, not less.

## What each state means for work

- **`STALE_CONTENT`** — a real build input changed after the PDF. The render disagrees
  with the source; the manuscript needs a rebuild and the claim needs re-checking.
- **`STALE_PROVENANCE_ONLY`** — only companions changed. The render is right, but CI's
  epoch check will not reproduce these bytes, so the fix is a fresh **CI-built** PDF
  import. It is not a content correction, and treating it as one sends someone to rewrite
  a manuscript that is already correct.

Because a branch-side PDF is invalidated by its own squash-merge, that import has to be a
post-merge commit on `main` touching only `main.pdf` — the shape used for ORION-08, -11
and -13, whose epochs were verified unmoved after their merge.

## Checker validation

Both directions exercised, not just the passing one:

| case | expected | got |
|---|---|---|
| tree as-is | 0, no content staleness | **0** |
| synthetic `.tex` build-input change | 1, `STALE_CONTENT` | **1**, flagged ORION-14 on `main.tex` |

The alarm case matters: a staleness checker that cannot fire is indistinguishable from
one that has nothing to report.
