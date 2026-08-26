# Reproduce the scoped P3 headline

This route reproduces the bounded P3.C5/P3.C9 public-reference mapping result and the manuscript/package checks. It does not execute the retired eight-family raw-text study.

From repository root:

```bash
python -m pip install -e '.[dev,candidates]'
python papers/paper-03-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/publication/generate_publication_artifacts.py --check
pytest -q tests/test_p3_public_reference_confirmatory.py tests/test_p3_confirmatory_receipt.py
```

For the additive method-structure non-vacuity pilot:

```bash
pytest -q tests/test_p1_p3_method_structure.py
```

For the scoped manuscript/package gate, use the same commands as `.github/workflows/p3-manuscript-audit.yml`: install the declared TeX toolchain, run the static claim/citation/input audit, verify `journal_package/SHA256SUMS`, and compile `manuscript/main.tex` with `latexmk -pdf -interaction=nonstopmode -halt-on-error` until references converge.

The authoritative headline numbers are in:

- `evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json`;
- `research/verification/records/P3.C5.confirmatory-mapping.json`;
- `CLAIM_LEDGER_V1.md`.

A wider raw-text, downstream-utility, or expert-atlas claim requires a new prospective protocol and is not reproduced by this route.
