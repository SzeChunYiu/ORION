# Four committed manuscript PDFs do not reproduce, and the check that says so had never run

**Status:** `FINDING__FOUR_PAPERS_BLOCKED_ON_PDF_REPRODUCIBILITY`
**Scientific authority delta:** `NONE`.

## What the audit found the first time it could

`manuscript-clipping-audit` ends by rebuilding every manuscript under a pinned
`SOURCE_DATE_EPOCH` and diffing the result against the committed PDF:

```bash
git diff --exit-code -- ':(glob)papers/orion-??-*/manuscript/main.pdf' \
  ':(exclude)papers/orion-05-tare-expressivity/manuscript/main.pdf'
```

It had never reached that step. The rebuild loop died earlier, at ORION-10, because
`quantumarticle.cls` requires `ltxgrid` and the workflow's pinned apt list did not install
`texlive-publishers`. Every run failed on the missing package, and the failure read as a
clipping-audit failure.

With that installed (#2054), the loop completes and the final step reports:

| paper | committed `main.pdf` vs clean rebuild |
|---|---|
| `orion-08-typed-state` | **differs** |
| `orion-10-certified-static-forecasting` | **differs** |
| `orion-12-open-world-scientific-discovery` | **differs** |
| `orion-19-structured-epistemic-learning` | **differs** |

Four of the twenty rebuilt manuscripts ship a PDF that a clean rebuild does not produce.

## Two things the same run establishes, which should not be confused with it

The clipping audit proper is **clean**: `audited=23 findings=0 new=0 accepted_debt=0
stale_baseline=0 unreadable=0`. No manuscript has text running off the paper. That was the
gate's original purpose and it passes.

Four journal packages are skipped as `SKIP_SUPERSEDED` — ORION-11, ORION-12, ORION-13,
ORION-15 — which is the separate, already-declared fact that their packaged PDF renders
inputs that have since changed.

So three distinct states are visible in one run, and only the third is new:

1. no clipping anywhere;
2. four packages whose PDF renders superseded inputs, each already saying so in its own
   `RENDER_CLOSURE_STATE.json`;
3. **four manuscripts whose committed PDF does not reproduce from its own sources.**

## Why (3) is the freeze-blocking one

A superseded package can be brought current by rebuilding it. A non-reproducing PDF cannot
be brought current by any rebuild, because rebuilding is precisely what disagrees with it.
Either the committed bytes were produced by a different toolchain or a different source
state, or the render is not deterministic under the pinned epoch. Until that is settled, the
artifact a referee receives cannot be tied to the sources in the repository.

ORION-19 is the sharpest illustration. A render of it inside an unrelated pull request
produced a PDF of **identical byte length and a different digest**, which is the signature of
a non-reproducible render rather than an edit. Reverting to the committed bytes clears the
drift and restores a PDF that still does not reproduce.

## What would settle each case

For each of the four, in order, stopping at the first that explains it:

1. Does a clean rebuild at the paper's own `SOURCE_DATE_EPOCH` differ from the committed PDF
   in **length** as well as digest? A length change means the sources moved and the PDF was
   not rebuilt — the ORION-12 shape.
2. Does it differ in digest at **identical length**? That points at a non-deterministic
   render, and `SOURCE_DATE_EPOCH`/`FORCE_SOURCE_DATE` coverage is the thing to check.
3. Does the committed PDF's own metadata name a toolchain the workflow no longer pins?

None of that is done here. This document records the finding and the fact that it was
invisible until the toolchain gap closed; the per-paper diagnosis is the next piece of work
and is queued, not claimed.

## Provenance

Job `99938627807` of run `33532447098`, on the head of PR #2049 after it was rebased onto
#2054. The same four names appear in the `git diff` output there verbatim.
