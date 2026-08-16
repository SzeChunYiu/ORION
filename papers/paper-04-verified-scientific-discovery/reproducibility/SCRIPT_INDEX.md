# ORION-P4 Script Index

## Figure Generation Scripts

| Script | Output | Description |
|--------|--------|-------------|
| `figures/generate_figures.py` | All 6 SVG figures | Regenerates all figures from placeholder data. Run from the paper-04 directory. |

## Campaign Scripts

| Script | Purpose |
|--------|---------|
| `src/orion/benchmarks/campaign_runner.py` | Runs the full baseline and ablation campaign against a manifest |
| `src/orion/benchmarks/baseline_runner.py` | Runs individual baseline strategies |
| `src/orion/benchmarks/ablation_runner.py` | Runs ablation variants of the ORION system |

## Data Processing Scripts

| Script | Purpose |
|--------|---------|
| `research/paper-programme-v1/protocols/publication_stats.py` | Wilson intervals, bootstrap CI, sample size planning |
| `research/paper-programme-v1/protocols/publication_svg.py` | SVG bar charts, scatter plots, and heatmaps from CSV/JSON |

## Validation Scripts

| Script | Purpose |
|--------|---------|
| `tests/test_paper_manuscript_integrity.py` | Validates manuscript structure, citations, and protocol reference |
| `tests/test_journal_protocol_assets.py` | Validates protocol JSONs, schemas, stats, and SVG builders |
| `tests/unit/benchmarks/test_attack_manifest.py` | Validates attack manifest against schema |
| `tests/unit/benchmarks/test_baseline_runner.py` | Validates baseline and ablation implementations |
| `tests/unit/benchmarks/test_protocol_freezing.py` | Validates protocol freeze, metrics registry, and plot spec |

## Regeneration Commands

```bash
# Regenerate all figures
python papers/paper-04-verified-scientific-discovery/figures/generate_figures.py

# Regenerate from raw result data
python -m research.paper-programme-v1.protocols.publication_stats summarize \
  results/campaign_results.jsonl --metric false_authority_promotion_rate

# Re-render figures from frozen summary JSON
python -m research.paper-programme-v1.protocols.publication_svg bar \
  summaries/false_promotion.json figures/p4_2_false_promotion.svg \
  --label system --value rate --title "False Authority-Promotion Rate" --y-label "False Promotion Rate"
```