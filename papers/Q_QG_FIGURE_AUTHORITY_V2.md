# Q/QG publication figure authority V2

Date: 2026-08-21

## Authoritative publication builder

- source manifest: `papers/Q_QG_FIGURE_SOURCE_V1.json`
- builder: `papers/build_q_qg_figures_v2.py`
- workflow: `.github/workflows/q-qg-figures-v2.yml`
- expected artifact: `q-qg-publication-figures-v2`
- expected quantitative plots: **12 standalone SVG + 12 standalone PNG**
- exact source data: `source_data.json`
- receipt verification report: `verification.json`
- generated file registry: `generated_stems.json`

## Superseded exploratory layout

`papers/archive/2026-08-pre-unification/build_q_qg_figures.py` and `.github/workflows/q-qg-figures.yml` are retained as development history only. Their grouped subplot layouts have **no publication authority** and must not be included in target packages.

## V2 plot set

### ORION-01
- `Q1_counterexamples_and_support_ceiling_v2`

### ORION-02
- `Q2_declared_denominator_v2`

### ORION-04
- `Q4_N4A_typed_prior`
- `Q4_N4B_scoped_reopening`
- `Q4_N4C_targeted_verification`
- `Q4_N4D_chain_transport`
- `Q4_N4E_decision_coupled`
- `Q4_N4F3_remint_transport`

### ORION-09
- `QG1_R6I_support_bound_hierarchy_v2`
- `QG1_QG16_certificate_cone_slice_v2`

### ORION-10
- `QG2_registered_comparison_counts_v2`
- `QG2_exact_counterexample_repair_v2`

## Scientific safeguards

Before drawing, V2 requires every configured numeric scalar to occur in the union of the paper's bound source artifacts at the correct scientific cut. It then exports the exact plotted source data.

The plot builder does not grant theorem, novelty, replication, generalization, physical-advantage, or submission authority.

## Visual QA still required

A green build is not a visual audit. Before inclusion in any final target package, inspect each PNG/SVG at the intended physical width for:
- readable labels;
- no clipping/overlap;
- no misleading axis scale;
- legend/annotation agreement with the figure legend;
- exact caption denominator/evidence class;
- no color-only distinction;
- no accidental replacement of an exact counterexample with an aggregate percentage.

Any data/claim change must be made upstream in the scientific artifact/manuscript and re-run through the publication gates; do not hand-edit plotted values.
