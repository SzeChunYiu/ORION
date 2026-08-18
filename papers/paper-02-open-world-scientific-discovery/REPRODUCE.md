# Reproduce ORION-P2

Run from the repository root with Python 3.12.

## Claim and protocol gates

```bash
python papers/paper-02-open-world-scientific-discovery/scripts/check_claim_ledger.py --check
python papers/paper-02-open-world-scientific-discovery/scripts/check_p2_assimilation.py
python papers/paper-02-open-world-scientific-discovery/scripts/check_p2_v2.py
python papers/paper-02-open-world-scientific-discovery/scripts/mirror_ci_evidence.py --check
```

These checks fail closed on unledgered result prose, donor/source drift,
unauthorized V2 promotion, and mutated or missing CI evidence archives.

## Controlled headline evidence

```bash
python papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check
python papers/paper-02-open-world-scientific-discovery/scripts/render_suite_facts.py --check
python papers/paper-02-open-world-scientific-discovery/scripts/render_offline_mechanisms.py --check
python papers/paper-02-open-world-scientific-discovery/scripts/render_route_stop_oracle.py --check
```

The offline companion rebuilds the 390-task × 14-system × 3-repeat projection
and refuses any digest drift. Repeats test deterministic harness stability; they
do not enlarge the statistical unit. The headline remains descriptive and
underpowered for the frozen 0.03 superiority margin.

## External evidence

MetaSyn and AutoResearchBench rerun instructions and pinned revisions are in
`protocol/` and `evidence/access/`. The OpenAIRE/Crossref matched campaign is
not rerun into a different result: its immutable failed capture, first evaluator
handoff, and evaluator-only repair are mirrored as the three
`evidence/ci_mirror/p2-wide-openaire-matched-*.zip` files. Verify them with the
mirror command above and audit the terminal in:

- `evidence/external_results/P2_WIDE_OPENAIRE_MATCHED_RESULT_V1.json`;
- `evidence/external_results/P2_WIDE_OPENAIRE_MATCHED_RUN_RECEIPT_V1.json`.

Its `P2_WIDE_EXTERNAL_CANNOT_CHECK` terminal is mandatory because only 800 of
1,200 provider calls succeeded. A new campaign requires a new prospective
protocol; do not overwrite this capture or interpret its zero paired difference
as a valid null.

## Manuscript and package

```bash
cd papers/paper-02-open-world-scientific-discovery/manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
python ../scripts/check_manuscript_typography.py --log main.log
cd ..
sha256sum -c journal_package/SHA256SUMS
```

Expected review artifact: 21-page `journal_package/manuscript.pdf`, with no
unresolved citation/reference warning and zero overfull boxes. The package
attests only the bounded methods / critical system-design claim; external
ORION-vs-baseline superiority remains `CANNOT_CHECK`.
