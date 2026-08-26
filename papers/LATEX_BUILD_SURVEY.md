# LaTeX build survey

Produced by compiling every `main.tex` under `papers/` with Tectonic 0.15.0
on LUNARC. Recorded rather than summarised, because "the papers build" is a
claim that should carry its own denominator.

**17 of 26 targets produced a PDF.** The 9 that did not
split into three classes, and only one of them is a defect.

## Built

| Target | PDF bytes |
|---|---|
| `orion-05-tare-expressivity` | 74,186 |
| `orion-06-recursive-recovery` | 56,244 |
| `orion-07-dual-instrument` | 53,907 |
| `orion-08-typed-state` | 57,754 |
| `orion-09-compilation-regime-geometry` | 66,312 |
| `orion-10-certified-static-forecasting` | 72,002 |
| `orion-11-recursive-epistemic-reconstruction` | 326,930 |
| `orion-12-open-world-scientific-discovery` | 322,155 |
| `orion-13-global-knowledge-portrait` | 289,341 |
| `orion-14-verified-scientific-discovery` | 553,370 |
| `orion-15-self-orion` | 278,879 |
| `orion-16-formal-epistemic-structures-and-mechanics` | 69,042 |
| `orion-17-epistemic-navigation-open-worlds` | 61,786 |
| `orion-18-epistemic-authority-autonomous-science` | 68,194 |
| `orion-19-structured-epistemic-learning` | 98,411 |
| `orion-20-structured-problem-solving` | 65,842 |
| `orion-25-orion-research-harness` | 116,922 |

## Not build targets (preserved fragments)

These are not manuscripts and their failure is not a defect. Commit `1f545b8d` preserved 575 files from 447 un-PR'd branches; these `paper/` trees are part of that sweep and are listed individually in `papers/candidates/BRANCH_FOREST_PRESERVATION_2026-08-23.md`.

The fragments are `.md` files while the accompanying `main.tex` inputs `.tex` files, so these trees were never coherent. `paper-11`'s tree inputs ten chapters and contains one. A sweep that compiles every `main.tex` will always fail here; that is the sweep's error, not the repository's.

- `orion-21-state-as-computation_paper`
- `orion-22-adaptive-state-reasoning_paper`
- `orion-23-responsibility-carrying-state_paper`
- `orion-24-orion-rse_paper`

## Engine-dependent (real, toolchain)

These are genuine manuscripts that Tectonic cannot build. Two causes, both in the toolchain rather than the prose:

1. `\DeclareUnicodeCharacter` is a pdflatex + `inputenc` command and is undefined under XeTeX, which is what Tectonic runs. XeTeX needs no such declarations because it handles the code points natively.
2. The LaTeX `markdown` package shells out to `texlua`. Even with `-Z shell-escape`, Tectonic could not execute it.

So these require a full TeX Live with `pdflatex` and `texlua`, not a self-contained engine. That matters at submission time: a journal building with a different engine than the author will not reproduce the author's PDF.

- `orion-21-state-as-computation`
- `orion-22-adaptive-state-reasoning`
- `orion-23-responsibility-carrying-state`
- `orion-24-orion-rse`

## Other

- `candidates_orion-19-structured-epistemic-learning` — :: error: main.tex:3: ! LaTeX Error: File `tmlr.sty' not found.

## Reproducing this

```bash
find papers -name main.tex | while read tex; do
  (cd "$(dirname "$tex")" && tectonic -X compile main.tex --outdir /tmp/out)
done
```

