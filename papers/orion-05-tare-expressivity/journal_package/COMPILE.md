# Exact compile and verification instructions

## Canonical render

The bound PDF was built from manuscript commit `606552180c577a235b0947bf80d225e45424c8ba` with:

- Tectonic 0.15.0;
- XeTeX-compatible processing and `xdvipdfmx` PDF production;
- `SOURCE_DATE_EPOCH=1787918400`.

Two clean builds with this epoch were byte-identical. The resulting 8-page, 98,333-byte PDF SHA-256 is:

```text
75a893f32465a8eabba8161f2368839a880b3c046f1b0edf04cc6375d46a968b
```

## Rebuild

From the manuscript directory:

```text
SOURCE_DATE_EPOCH=1787918400 tectonic main.tex --keep-logs --keep-intermediates
```

The same source also compiles with a standard `latexmk` PDF workflow. A toolchain change may compile correctly without reproducing identical bytes. Such a render must not silently replace the bound PDF.

## Required checks

From the repository root:

```text
PYTHONPATH=. pytest -q \
  tests/unit/publication/test_q1_proof_sanity_binding.py \
  tests/unit/publication/test_orion05_r12_production_benchmark.py \
  tests/unit/publication/test_orion05_wave1_manuscript_surface.py

python scripts/audit_manuscript_clipping.py --root . \
  papers/orion-05-tare-expressivity/manuscript/main.pdf \
  papers/orion-05-tare-expressivity/journal_package/manuscript.pdf

python papers/orion-05-tare-expressivity/submission/build_anonymous_review_artifact.py
```

The anonymous archive must rebuild byte-identically, pass ZIP integrity and recursive reader-surface scans, and pass `proof_sanity.py`, `verify_sharpness.py`, and `aggregate_runtime.py --check runtime_summary.json`. Its isolated manuscript source must compile to an eight-page text-equivalent PDF.

## Filing prohibition

Do not upload this package to *Quantum* or *PRX Quantum*. The scientific object is coherent at its declared boundary, but the requested target-significance gate remains open. Retargeting requires an author-selected exact venue and, where applicable, a new class or template build.
