# ORION-14 exact compile and verification instructions

## Canonical render

The bound submission PDF was produced from source revision `b1c0d26096a822e8294b8b60dbbbec3c4e73bc5d` by GitHub Actions run `33167703059` using:

- Ubuntu runner;
- latexmk 4.83;
- pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian);
- `SOURCE_DATE_EPOCH=1787916820`;
- vendored official TMLR style files pinned to upstream commit `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992`.

Pinned style hashes:

```text
816214ff5919aa457b6b443bee52b15d9561421417b7f8a50cc84651519f0002  manuscript/tmlr.sty
306fd454cf40771bee01293eeb98d2c1cd5f4e11ed0cd7296b335f354fc45206  manuscript/tmlr.bst
```

The resulting PDF is 19 pages with SHA-256:

```text
d9b8fbf3b9f16a7c35b478a810121d8803ae2d848a7817d0cff33e6d47126110
```

## Build from the repository root

Install latexmk, TeX Live with recommended fonts/LaTeX packages, librsvg and Poppler. Regenerate the safe figures and tables before compiling:

```bash
python papers/orion-14-verified-scientific-discovery/figures/generate_figures.py
F=papers/orion-14-verified-scientific-discovery/figures
for stem in p4_2_false_promotion p4_3_coverage_frontier \
            p4_4_detection_by_attack p4_5_attribution_vs_support \
            p4_6_cost_false_promotion; do
  rsvg-convert -w 1440 -o "$F/$stem.png" "$F/$stem.svg"
done
```

Compile with the pinned epoch:

```bash
cd papers/orion-14-verified-scientific-discovery/manuscript
export SOURCE_DATE_EPOCH=1787916820
latexmk -C main.tex
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error main.tex
```

The exact byte hash requires the pinned Ubuntu/TeX toolchain above. A successful build on another platform is a useful compile check but is not authority to replace the bound PDF.

## Required verification

From the repository root:

```bash
python papers/orion-14-verified-scientific-discovery/submission/build_anonymous_review_artifact.py --out-dir /tmp/orion14-anonymous
pytest -q tests/unit/p4/test_p4_publication_v2.py \
          tests/unit/p4/test_p4_v2_execution_freeze.py \
          tests/unit/p4/test_p4_h3_v3_promotion.py
python research/paper-programme-v1/journal_package/check_journal_package.py --paper P4
python scripts/audit_manuscript_clipping.py --root . \
  papers/orion-14-verified-scientific-discovery/manuscript/main.pdf \
  papers/orion-14-verified-scientific-discovery/journal_package/manuscript.pdf
```

Also run the package-currency and manuscript-integrity/surface tests named in the final editor record. `SHA256SUMS` must remain unchanged and all required files must verify.

## Filing objects

Upload only the exact bound `journal_package/manuscript.pdf` and `journal_package/orion14_anonymous_review_2026-08-28.zip`, after completing the human-only OpenReview metadata. Do not upload `submission/TMLR_EDITOR_NOTE_2026-08-28.md` as anonymous supplementary material; it contains the corresponding-author identity for the editor-facing form.
