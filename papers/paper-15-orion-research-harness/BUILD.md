# P15 build

Canonical source: `manuscript/main.tex` and the tracked files under
`manuscript/chapters/`.

From `manuscript/`:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

The build must complete without shell escape, runtime network access, unresolved
citations/references or untracked generated chapter text. Record the TeX engine,
`latexmk` version and final PDF digest with any submission candidate.

Verified candidate on 2026-08-22:

- pdfTeX `3.141592653-2.6-1.40.25` (TeX Live 2023/Debian);
- `latexmk` `4.83`;
- 10 US-letter pages;
- no unresolved citation/reference, overfull or underfull warnings in the final log;
- `main.pdf` SHA-256
  `ee2c034a556b73034d9f2dda0ecb8668f49710a26d83d0a245addf09e4195691`.
