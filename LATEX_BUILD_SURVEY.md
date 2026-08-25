# LaTeX build survey

Produced by compiling every `main.tex` under `papers/` with Tectonic 0.15.0
on LUNARC. Recorded rather than summarised, because "the papers build" is a
claim that should carry its own denominator.

**17 of 26 targets produced a PDF.** The 9 that did not
split into three classes, and only one of them is a defect.

## Built

| Target | PDF bytes |
|---|---|
| `Q-paper-01-tare-expressivity` | 74,186 |
| `Q-paper-02-recursive-recovery` | 56,244 |
| `Q-paper-03-dual-instrument` | 53,907 |
| `Q-paper-04-typed-state` | 57,754 |
| `QG-paper-01-compilation-regime-geometry` | 66,312 |
| `QG-paper-02-certified-static-forecasting` | 72,002 |
| `paper-01-recursive-epistemic-reconstruction` | 326,930 |
| `paper-02-open-world-scientific-discovery` | 322,155 |
| `paper-03-global-knowledge-portrait` | 289,341 |
| `paper-04-verified-scientific-discovery` | 553,370 |
| `paper-05-self-orion` | 278,879 |
| `paper-06-formal-epistemic-structures-and-mechanics` | 69,042 |
| `paper-07-epistemic-navigation-open-worlds` | 61,786 |
| `paper-08-epistemic-authority-autonomous-science` | 68,194 |
| `paper-09-structured-epistemic-learning` | 98,411 |
| `paper-10-structured-problem-solving` | 65,842 |
| `paper-15-orion-research-harness` | 116,922 |

## Not build targets (preserved fragments)

These are not manuscripts and their failure is not a defect. Commit `1f545b8d` preserved 575 files from 447 un-PR'd branches; these `paper/` trees are part of that sweep and are listed individually in `papers/candidates/BRANCH_FOREST_PRESERVATION_2026-08-23.md`.

The fragments are `.md` files while the accompanying `main.tex` inputs `.tex` files, so these trees were never coherent. `paper-11`'s tree inputs ten chapters and contains one. A sweep that compiles every `main.tex` will always fail here; that is the sweep's error, not the repository's.

- `paper-11-state-as-computation_paper`
- `paper-12-adaptive-state-reasoning_paper`
- `paper-13-responsibility-carrying-state_paper`
- `paper-14-orion-rse_paper`

## Engine-dependent (real, toolchain)

These are genuine manuscripts that Tectonic cannot build. Two causes, both in the toolchain rather than the prose:

1. `\DeclareUnicodeCharacter` is a pdflatex + `inputenc` command and is undefined under XeTeX, which is what Tectonic runs. XeTeX needs no such declarations because it handles the code points natively.
2. The LaTeX `markdown` package shells out to `texlua`. Even with `-Z shell-escape`, Tectonic could not execute it.

So these require a full TeX Live with `pdflatex` and `texlua`, not a self-contained engine. That matters at submission time: a journal building with a different engine than the author will not reproduce the author's PDF.

- `paper-11-state-as-computation`
- `paper-12-adaptive-state-reasoning`
- `paper-13-responsibility-carrying-state`
- `paper-14-orion-rse`

## Other

- `candidates_paper-09-structured-epistemic-learning` — :: error: main.tex:3: ! LaTeX Error: File `tmlr.sty' not found.

## Reproducing this

```bash
find papers -name main.tex | while read tex; do
  (cd "$(dirname "$tex")" && tectonic -X compile main.tex --outdir /tmp/out)
done
```

