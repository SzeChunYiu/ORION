# Compile and verification

Required tools: Python 3, Pandoc, a working `pdflatex`, `qpdf`, GNU `sha256sum`, and Poppler `pdftotext`.

From this directory:

```bash
python verify_package.py
./build.sh
python verify_package.py --require-render
```

`build.sh` renders `SOURCE.md`, validates the PDF container and extracted text, writes SHA-256 receipts for the exact source, claim ledger, and PDF, and then reruns the fail-closed package verifier. The renderer is a review/submission-neutral build; apply a journal-specific template only at filing time without changing scientific content or claim authority.
