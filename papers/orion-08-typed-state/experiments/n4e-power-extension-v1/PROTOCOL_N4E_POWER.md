# PROTOCOL — N4-E power extension V1 (ORION-08 successor)

Committed BEFORE any outcome. One script (`run_n4e_power_v1.py`), one pass,
stdout + JSON receipt (schema `ORION08.N4E_POWER.v1`) + SHA256SUMS. Reuses the
frozen analysis machinery verbatim by importing
`papers/orion-08-typed-state/publication_analysis.py` (`quantile`, `load`) —
no statistical code is re-implemented. Design mirrors the certified N4-B
extension (`../n4b-power-extension-v1/`), adjusted for N4-E's flat
single-block episode list.

## Registered design

- **Episodes:** continue the frozen stream — `random.Random(20260821)`,
  `N_EXT = 4000`. Episodes 1..400 are byte-identical to the frozen analysis
  (determinism of the stream); 401..4000 are the new mass. Single block; the
  frozen list is extended in place on the same stream.
- **Targets (gated, Bonferroni family m = 2):**
  `decision_voi_vs_llm_proxy` (`ORION_DECISION_VOI` − `LLM_PROXY_HEURISTIC`,
  `utility`) and `decision_voi_vs_infogain` (`ORION_DECISION_VOI` −
  `INFOGAIN`, `utility`). Per-comparison two-sided **97.5%** bootstrap CIs
  (family-wise 95%), 5000 draws, seed `20260902:n4e-power:<label>`.
- **Monitoring (non-gated):** both contrasts' point estimates vs frozen
  (±10% continuity); split-half stability (first 2000 vs second 2000).
- **Practical-equivalence bound:** δ = 0.3 utility (rationale in
  `DERIVATION_N4E_POWER.md`).

## Cross-check (gated, runs first)

**P1 prefix reproduction:** recompute the frozen statistics on episodes
1..400 with the frozen bootstrap machinery (frozen seed labels
`E-voi-vs-proxy` / `E-voi-vs-infogain`, frozen 95% quantiles) and require
mean, CI, and win/tie/loss fractions to match
`PUBLICATION_PAIRED_ANALYSIS_V1.json` within 1e-9. P1 failing aborts with
`N4E_POWER_PREFIX_FAIL` (exit 3) and no target verdict.

## Gates (per target, in order)

1. 97.5% CI excludes 0 → `RESOLVED_POSITIVE` (lower bound > 0) or
   `RESOLVED_NEGATIVE` (upper bound < 0).
2. else CI ⊂ (−δ, +δ) → `BOUNDED_NULL`.
3. else → `UNRESOLVED`.

Study terminal: both targets in {RESOLVED_*, BOUNDED_NULL} →
`N4E_POWER_DETERMINED_BOTH` (exit 0); otherwise
`N4E_POWER_PARTIAL_<targets>` (exit 1).

## Discipline

No fitted parameter; every constant (N_EXT, δ, seeds, draw count, family) is
registered here before the first run. The frozen protocol, module, and
published analysis are untouched; the extension is additive. An aborted or
crashed pass is retained as a receipt (suffix `_aborted`) and never silently
retried without an amendment naming the defect.
