# A reproducibility gate that had never run, and the four PDFs it found when it could

**Status:** `RESOLVED_ON_MAIN__KEPT_AS_THE_ACCOUNT_OF_A_GATE_THAT_COULD_NOT_RUN`
**Scientific authority delta:** `NONE`.

## Resolved, and by the repair this document prescribed

All four are fixed on `main`. Every committed `main.pdf` now carries a `CreationDate` equal
to the `SOURCE_DATE_EPOCH` derived from its own source commit:

| paper | committed `CreationDate` | epoch | |
|---|---|---|---|
| `orion-08-typed-state` | `D:20260901115822Z` | `D:20260901115822Z` | match |
| `orion-10-certified-static-forecasting` | `D:20260901130335Z` | `D:20260901130335Z` | match |
| `orion-12-open-world-scientific-discovery` | `D:20260901171947Z` | `D:20260901171947Z` | match |
| `orion-19-structured-epistemic-learning` | `D:20260901121303Z` | `D:20260901121303Z` | match |

`997b26aa6` — *"papers: bind deterministic manuscript renders"* (#2070) — regenerated three
of them, and `aa7018400` regenerated ORION-12. ORION-10, the sub-case whose PDF carried no
`CreationDate`, `ModDate` or `/Producer` at all, now carries one; that open question is
closed with it.

The repair applied is the repair this document prescribed before seeing it: regenerate each
PDF *through the workflow's own loop* with the epoch exported. Two routes reaching the same
place is worth more than either alone, and it is the reason this file is kept rather than
deleted.

**What it is now.** Not a live defect report. An account of a reproducibility gate that had
never once run, why it could not, what it found in the single window where it could, and the
mechanism behind that finding. The finding itself is spent.

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

## Diagnosed

The three-step diagnostic below was run, and it resolves all four.

**The committed PDFs were rendered outside the pinned render path.** Each carries a
`CreationDate` that is the author's wall clock at render time, not the
`SOURCE_DATE_EPOCH` the workflow derives from the manuscript's own source commit:

| paper | committed `CreationDate` | what `SOURCE_DATE_EPOCH` gives | gap |
|---|---|---|---|
| `orion-08-typed-state` | `D:20260901114631Z` | `D:20260901115822Z` | 12 minutes early |
| `orion-19-structured-epistemic-learning` | `D:20260901095132Z` | `D:20260901121303Z` | 2h 22m early |
| `orion-12-open-world-scientific-discovery` | `D:20260901023132Z` | `D:20260901150101Z` | 12h 30m early |

For ORION-08 and ORION-19 the PDF and its sources were committed in the *same* commit, so
the pinned epoch would be that commit's timestamp. The PDF instead carries a time shortly
*before* it — the moment someone rendered locally, minutes before committing. CI renders with
the epoch exported, so it cannot help but produce different bytes.

That is why ORION-19's re-render inside another pull request had **identical byte length and
a different digest**. The documents are the same; only the embedded timestamp and the
resulting `/ID` differ.

ORION-12 is the compound case: rendered outside the path *and* stale, its sources having
moved in `4b8e4cdb5` after the PDF was written in `d163369a9`.

**ORION-10 is a different sub-case.** Its PDF carries no `CreationDate`, no `ModDate` and no
`/Producer` at all, where the other three carry `pdfTeX-1.40.25`. It was produced by some
other route, and naming that route is the one piece still open.

## The repair this implies

Regenerate each committed PDF *through the workflow's own loop*, with `SOURCE_DATE_EPOCH`
and `FORCE_SOURCE_DATE` exported, and commit the result. After that the committed bytes and
the CI rebuild are produced by one procedure and agree by construction.

Nothing here says the PDFs are wrong as documents. It says the committed artifact and the
rebuilt artifact were made by different procedures, so no comparison between them could ever
have succeeded — and a reproducibility gate that cannot succeed is not a gate.

## The original three-step diagnostic, for the record

## What would settle each case

For each of the four, in order, stopping at the first that explains it:

1. Does a clean rebuild at the paper's own `SOURCE_DATE_EPOCH` differ from the committed PDF
   in **length** as well as digest? A length change means the sources moved and the PDF was
   not rebuilt — the ORION-12 shape.
2. Does it differ in digest at **identical length**? That points at a non-deterministic
   render, and `SOURCE_DATE_EPOCH`/`FORCE_SOURCE_DATE` coverage is the thing to check.
3. Does the committed PDF's own metadata name a toolchain the workflow no longer pins?

That diagnostic was run; its result is the Diagnosed section above. Only ORION-10's
producing route remains unnamed.

## Provenance

Job `99938627807` of run `33532447098`, on the head of PR #2049 after it was rebased onto
#2054. The same four names appear in the `git diff` output there verbatim.
