# Reproduction order

Requirements: Python 3.10 or later; the included checks use only the standard library.

1. Run `python3 code/verify_review_results.py`.
2. Run `python3 code/generate_review_tables.py`.
3. Compare `generated_tables.md` with the corresponding manuscript tables.
4. Inspect `exact_results/state_preparation_panel.json` for the complete per-state panel and null distribution.

The Supplementary Information gives the formal models, proof compositions and exact null algorithm.
