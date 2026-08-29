# Build instructions

This package is generated **without editing the frozen canonical manuscript**. `SOURCE.md` and `CLAIM_LEDGER.md` are byte-identical package copies of the canonical files named in `SUBMISSION_MANIFEST.json`.

## Dependencies

- Pandoc
- pdfTeX / `pdflatex`

## One-command build

```bash
./build.sh
```

The command produces:

- `main.pdf`
- `BUILD_SHA256SUMS`

The PDF is a reproducible review/package render of the frozen Markdown source. It is **not** a claim that the source has been converted to a journal's final LaTeX template. Journal-template conversion remains a production step after venue instructions and human author metadata are fixed.

## Verification

Run:

```bash
python verify_package.py
```

The verifier checks package/source byte identity against the canonical repository files and the registered SHA-256 values, and fails closed if the package source drifts.

## Authority

Building a PDF changes no scientific authority. The manuscript's claim ledger and all external-review gates remain binding.
