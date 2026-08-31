# Render requirements — ORION-16, ORION-17, ORION-18 (V1)

Read-only investigation, 2026-08-30. Scope: the three manuscript trees that
currently have no PDF render path, which is what blocks manuscript repairs to
them (a repair desynchronises the hash-bound `manuscript/main.pdf` in
`SHA256SUMS` with no way to regenerate it).

Paths investigated:

- `papers/orion-16-formal-epistemic-structures-and-mechanics/manuscript/`
- `papers/orion-17-epistemic-navigation-open-worlds/manuscript/`
- `papers/orion-18-epistemic-authority-autonomous-science/manuscript/`

## Correction to the stated premise

The premise "no Makefile" is imprecise and the precise version is the whole fix.

Each of the three papers **does** have a `Makefile` — at the *paper root*, not
in `manuscript/`:

- `papers/orion-16-.../Makefile` — targets `reproduce-v3`, `reproduce-v4`
- `papers/orion-17-.../Makefile` — target `reproduce-v3`
- `papers/orion-18-.../Makefile` — target `reproduce-v3`

All three contain only `uv run python ...` checker invocations. **None has a
PDF/LaTeX target.** What is absent is `manuscript/Makefile`.

That distinction matters because the existing render workflow
`.github/workflows/paper-render-rebind-makefile-set.yml` selects papers by
exactly that file:

```
for d in papers/orion-21-* papers/orion-22-* papers/orion-23-* papers/orion-24-*; do
  [ -f "$d/manuscript/Makefile" ] || continue
```

So these three are excluded twice over: by the directory glob, and by the
`manuscript/Makefile` guard. Verified: no ORION-16/17/18 reference exists in
`paper-render-rebind-makefile-set.yml`, `repository-paper-rebind.yml` (which
covers ORION-11/13/14), or `saturation-final-render-audit.yml`.

## Per-paper requirements

| | ORION-16 | ORION-17 | ORION-18 |
|---|---|---|---|
| `\documentclass` | `[11pt]{article}` | `[11pt]{article}` | `[11pt]{article}` |
| Local `.sty`/`.cls`/`.bst` needed | none | none | none |
| Non-standard packages | none | none | none |
| shell-escape required | **no** | **no** | **no** |
| Figures committed | n/a — no figures referenced at all | n/a — same | n/a — same |
| Bibliography engine | BibTeX (`plain`) | BibTeX (`plain`) | BibTeX (`plain`) |
| `\input` section files | 8, all resolve | 8, all resolve | 10, all resolve |
| `.bib` entries | 14 | 14 | 13 |
| Section numbering | on (default) | off (`\setcounter{secnumdepth}{0}`) | off (`\setcounter{secnumdepth}{0}`) |
| Committed PDF producer | pdfTeX-1.40.25 | pdfTeX-1.40.25 | pdfTeX-1.40.25 |

### Preamble (identical across all three)

```
\usepackage{amsmath,amssymb}
\usepackage[margin=1in]{geometry}
\usepackage{xurl}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{caption}
\usepackage{longtable}
\usepackage{array}
\usepackage{ragged2e}
\usepackage[strings]{underscore}
\usepackage[expansion=false]{microtype}
```

Thirteen `\usepackage` lines, byte-for-byte the same set in all three files.
Every one is TeX Live stock; none needs fetching. `graphicx`, `booktabs`,
`tabularx`, `longtable` and `array` are loaded but unused by the current
section bodies — they must still be installed, and trimming the preamble is out
of scope for a read-only pass.

All three also carry the determinism block, which is why a rebuild can be
byte-stable at all:

```
\ifdefined\pdfinfoomitdate \pdfinfoomitdate=1 \fi
\ifdefined\pdftrailerid \pdftrailerid{} \fi
\ifdefined\pdfsuppressptexinfo \pdfsuppressptexinfo=-1 \fi
```

### Local style files

None. `find <paper-dir> -maxdepth 3 \( -name '*.sty' -o -name '*.cls' -o -name
'*.bst' \)` returns nothing for any of the three. `plain.bst` comes from TeX
Live. Contrast ORION-21, which does ship a local `gobble.sty` — these three do
not, and must not inherit anything from it.

### shell-escape

Not required. `minted`, `markdown`, `svg`, `write18`, `shellesc`, `pygment` and
`epstopdf` do not appear in `main.tex` or in any `sections/*.tex` for any of the
three papers. `sections/` contains `.tex` files only — no `.md` inputs.

Note the trap: `papers/orion-21-*/manuscript/Makefile` and the existing
`paper-render-rebind-makefile-set.yml` both pass `-shell-escape`, because
ORION-21 has `gobble.sty` and `sections/*.md`. **Drop that flag** when copying
that Makefile to 16/17/18; carrying it over would be cargo-cult and would widen
the build's trust surface for no reason.

### Figures

Stronger than "not committed": **no figure is referenced anywhere.**
`figures/` and `tables/` each contain only `.gitkeep` in all three papers, and
`grep includegraphics` over `main.tex` plus all of `sections/` returns nothing.
`\graphicspath{{figures/}}` is declared but unused.

Consequence for a workflow: **no** figure-generation step and **no**
`librsvg2-bin` / `rsvg-convert` are needed — unlike the P4 lane in
`repository-paper-rebind.yml`, which runs `generate_figures.py` and converts SVG
to PNG. Copying that lane wholesale would import work these papers do not need.

### Bibliography

BibTeX, not biblatex, not natbib. All three end with:

```
\nocite{*}
\bibliographystyle{plain}
\bibliography{bibliography}
```

`manuscript/bibliography.bib` exists in all three (14 / 14 / 13 entries, braces
balanced in each). Because of `\nocite{*}`, *every* entry in the file is
load-bearing — a malformed entry anywhere can trip an undefined-citation gate,
not only a cited one.

`main.bbl` is listed in `manuscript/.gitignore` in all three, so there is no
committed `.bbl` shortcut: **BibTeX must actually run in the build**, which
`latexmk -pdf` handles.

### Section inputs

Every `\input{sections/...}` target was checked file-by-file and resolves:
ORION-16 8/8, ORION-17 8/8, ORION-18 10/10. No orphan section files. ORION-17
deliberately inputs `08-real-regime-transport` *before* `07-limits`; that is
intentional ordering, not an error.

Section bodies use only `quote`, `itemize` and `enumerate` environments. No
`\usepackage`, `\RequirePackage` or `\documentclass` occurs inside any section
file.

## What a render workflow would need

### apt packages

Reuse the line already proven on sibling papers with the same preamble lineage,
verbatim from `paper-render-rebind-makefile-set.yml` (runner `ubuntu-24.04`):

```
sudo apt-get install -y -qq --no-install-recommends \
  latexmk texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-pictures texlive-fonts-recommended texlive-luatex lmodern poppler-utils
```

Notes, lower confidence than the verbatim line above: `texlive-latex-extra` is
the package carrying `xurl`, `ragged2e` and `underscore` — dropping it is the
likely failure mode. `texlive-luatex` is unnecessary for these three (pdflatex
only) but harmless. `librsvg2-bin` is **not** needed (no SVG). Ubuntu 24.04
ships TeX Live 2023 = pdfTeX 1.40.25, matching the producer string in all three
committed PDFs.

### Build command (identical for all three)

```
cd papers/<paper>/manuscript && \
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

No `-shell-escape`. No pre-step.

### Minimal-change route

Add `manuscript/Makefile` to each of the three, modelled on ORION-21's but with
`-shell-escape` and the `sections/*.md` prerequisite removed:

```
LATEXMK ?= latexmk

all: main.pdf

main.pdf: main.tex bibliography.bib sections/*.tex
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C
```

Then extend the glob in `paper-render-rebind-makefile-set.yml` from
`papers/orion-21-* papers/orion-22-* papers/orion-23-* papers/orion-24-*` to
also include `papers/orion-16-* papers/orion-17-* papers/orion-18-*`. Its
`[ -f "$d/manuscript/Makefile" ]` guard then admits them, and its existing
SHA256SUMS-refresh and commit steps already do the right thing.

### The rebind step is mandatory, not optional

Each paper's root `SHA256SUMS` binds the built PDF:

- ORION-16 line 56 — `fbdd6a8f...5ba7  .../manuscript/main.pdf`
- ORION-17 line 20 — `3ed66d99...b4e2  .../manuscript/main.pdf`
- ORION-18 line 24 — `333ba81e...3cf6  .../manuscript/main.pdf`

Whether a fresh render reproduces those exact bytes is **CANNOT_CHECK** here (no
TeX toolchain on this machine, no installs permitted). The determinism block
removes wall-clock nondeterminism and the producer version matches, so it is
plausible — but not verified. The workflow must therefore recompute and commit
the checksum alongside the PDF, as the existing rebind workflows already do. The
PDF and the checksums that describe it have to move in one commit.

## Blockers and open risks

1. **Overfull-box gate — CANNOT_CHECK, top risk.** Both existing render
   workflows hard-fail on `Overfull \hbox|Overfull \vbox` in `main.log`. These
   three preambles are precisely the ones whose comments discuss unbreakable
   typewriter runs, `\setlength{\emergencystretch}{3em}` and protrusion-only
   microtype — the authors were already fighting overfull boxes. Whether a fresh
   render passes that gate cannot be determined without rendering. Mitigation:
   first run should render **without** the gate to capture `main.log`, then
   decide between fixing the boxes and relaxing the gate for these three. Do not
   assume it passes.
2. **Undefined-citation gate — CANNOT_CHECK.** `\nocite{*}` pulls in all 14/14/13
   entries; a malformed entry would surface only at BibTeX time.
3. **Byte-identical rebuild — CANNOT_CHECK.** See the rebind section above.
4. **Not a blocker:** local styles, non-standard packages, figure generation,
   shell-escape, missing section files — all checked and clean.

## Method

`/bin/ls`, `/usr/bin/find`, `/usr/bin/grep`, `/usr/bin/sed`, `/bin/cat` used
directly (not via the rtk proxy, which corrupts output and exit codes). Absence
claims are backed by scoped searches whose scope is stated: `find` to depth 3
under each paper directory for style files; recursive `grep` over `main.tex`
plus the whole `sections/` directory for shell-escape and graphics markers. Each
`grep` batch included a control pattern that must match, to prove the search
itself worked.
