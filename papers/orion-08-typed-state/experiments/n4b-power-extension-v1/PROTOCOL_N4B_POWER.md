# PROTOCOL — N4-B power extension V1 (ORION-08 successor)

Committed BEFORE any outcome. One script
(`run_n4b_power_v1.py`), one pass, stdout + JSON receipt (schema
`ORION08.N4B_POWER.v1`) + SHA256SUMS. Reuses the frozen analysis machinery
verbatim by importing `papers/orion-08-typed-state/publication_analysis.py`
(`paired_summary`, `quantile`, `load`) — no statistical code is re-implemented.

## Registered design

- **Episodes:** continue the frozen stream — `random.Random(20260821)`,
  `REGIMES` order (STALE_MATTERS, REOPEN_WASTEFUL), `N_EXT = 2000` per
  regime. Episodes 1..200 per regime are byte-identical to the frozen
  analysis (determinism of the stream); 201..2000 are the new mass.
- **Targets (gated, Bonferroni family m = 2):** `scoped_vs_never`
  (`ORION_SCOPED_REOPEN` − `NEVER_REOPEN`, `mean_round_utility`) in both
  regimes. Per-comparison two-sided **97.5%** bootstrap CIs (family-wise
  95%), 5000 draws, seed `20260902:n4b-power:<label>`.
- **Monitoring (non-gated):** `scoped_vs_unscoped` in both regimes
  (continuity); split-half stability of both targets (first 1000 vs
  second 1000).
- **Practical-equivalence bound:** δ = 1.0 mean-round-utility (rationale in
  `DERIVATION_N4B_POWER.md`).

## Cross-check (gated, runs first)

**P1 prefix reproduction:** recompute the frozen statistics on episodes
1..200 per regime with the frozen bootstrap machinery (frozen seed labels
`B-<regime>-never`, frozen 95% quantiles) and require mean, CI, and
win/tie/loss fractions to match `PUBLICATION_PAIRED_ANALYSIS_V1.json`
within 1e-9. P1 failing aborts with `N4B_POWER_PREFIX_FAIL` (exit 3) and no
target verdict.

## Gates (per target, in order)

1. 97.5% CI excludes 0 → `RESOLVED_POSITIVE` (lower bound > 0) or
   `RESOLVED_NEGATIVE` (upper bound < 0).
2. else CI ⊂ (−δ, +δ) → `BOUNDED_NULL`.
3. else → `UNRESOLVED`.

Study terminal: both targets in {RESOLVED_*, BOUNDED_NULL} →
`N4B_POWER_DETERMINED_BOTH` (exit 0); otherwise
`N4B_POWER_PARTIAL_<targets>` (exit 1).

## Discipline

No fitted parameter; every constant (N_EXT, δ, seeds, draw count, family)
is registered here before the first run. The frozen protocol, module, and
published analysis are untouched; the extension is additive. An aborted or
crashed pass is retained as a receipt (suffix `_aborted`) and never
silently retried without an amendment naming the defect.
