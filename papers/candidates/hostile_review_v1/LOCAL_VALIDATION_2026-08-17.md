# Local validation — ORION-16–ORION-18 hostile formal review V1

**Date:** 2026-08-17  
**Reviewed programme snapshot:** `999abd4899f3fed906ba024ae8ecd775a69b6560`  
**Environment:** CPython 3.13.5, Linux x86_64  
**Authority:** authored local replay only; not independent verification or repository CI.

## Results

- Python AST parsing: **8/8 source files parsed**.
- Unit tests: **12/12 passed**.
- Review report: **11 records, 80 encoded cases, 0 unexpected `FAIL`**.
- Expected constructive terminals: **4 `COUNTEREXAMPLE_CONFIRMED`**.
- Two-run report determinism: **byte-identical**.
- Fresh-copy replay: **byte-identical** to the checked-in report.
- Checked-in report file SHA-256:  
  `db70fea4918918841bade760d3b12e87ec20a90547d4c919567114918092688a`
- Ruff: **NOT_RUN** because neither a `ruff` executable nor Python module was present in the authored environment.

## Commands

From the repository root:

```bash
python - <<'PY'
import ast
from pathlib import Path
for path in sorted(Path('papers/candidates/hostile_review_v1').rglob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
PY

PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s papers/candidates/hostile_review_v1/tests -v

PYTHONDONTWRITEBYTECODE=1 python \
  papers/candidates/hostile_review_v1/run_all.py

sha256sum -c \
  papers/candidates/hostile_review_v1/MANIFEST.sha256
```

## Boundary

These results validate the authored finite implementation and reproduce the
listed counterexamples. They do not establish the general theorems, novelty,
faithful donor embedding, empirical transfer, independent review, or promotion
of ORION-16–ORION-18.
