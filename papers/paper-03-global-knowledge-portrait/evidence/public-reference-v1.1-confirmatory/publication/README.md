# P3 public-reference confirmatory publication artifacts

These files are deterministic presentation artifacts generated from the immutable confirmatory analysis in `../CONFIRMATORY_ANALYSIS.json`.

## Figures

- `PR3-F1_false_merge_by_system.svg` — pooled false-merge rate for ORION, flat predicate canonicalization and exact-coordinate conservative control.
- `PR3-F2_flat_false_merge_by_case_family.svg` — where the flat control's confirmatory false merges occur across the three covered case families.
- `PR3-F3_ablation_false_merge_deltas.svg` — descriptive paired false-merge deltas and 95% bootstrap intervals for the implemented coordinate ablations.

## Tables

`PUBLIC_REFERENCE_CONFIRMATORY_TABLES_V1.md` contains:

- PR3-T1: confirmatory composition by covered case family;
- PR3-T2: pooled system metrics;
- PR3-T3: the two predeclared confirmatory primary comparisons;
- PR3-T4: covered ablation false-merge deltas.

`SHA256SUMS` binds the generated outputs produced by CI.

## Rebuild

```bash
make paper03-public-reference-publication
```

The generator reads only the archived confirmatory analysis and performs no system execution, model call, web search, or gold mutation.

## Authority boundary

These are **public-reference mapping** figures/tables. They do not replace the original Paper-III figures requiring end-to-end raw-text baselines, recoverability, obstruction-by-incompatibility-type across the full gold set, downstream-answer quality, or the full eight-family study. The main claim ledger remains authoritative if any caption or manuscript prose conflicts with this scope.
