# DERIVATION — N4-E power extension V1 (ORION-08 successor)

Companion: `PROTOCOL_N4E_POWER.md` (committed before any outcome). Parent:
`papers/orion-08-typed-state/PUBLICATION_PAIRED_ANALYSIS_V1.json` (frozen
secondary analysis) and the manuscript limitation it names: after the N4-B
power extension (`../n4b-power-extension-v1/`) determined the two
zero-containing N4-B rows as bounded nulls, the *surviving* comparison whose
interval lies **closest to zero relative to its width** is N4-E's
`decision_voi_vs_llm_proxy` contrast. This extension determines it (and its
sibling) at 10× the frozen mass.

## What is being determined

| contrast | frozen mean | frozen 95% CI | mean/width status |
|---|---|---|---|
| decision_voi_vs_llm_proxy | +0.2770 | [+0.1187, +0.4119] | surviving, closest to zero relative to width (mean/half-width ≈ 1.9) |
| decision_voi_vs_infogain | +2.1455 | [+1.9760, +2.2988] | surviving, wide margin (monitoring + secondary target) |

Nothing about the frozen protocol changes: same module
(`research/extensions/orion-q/nlanes/n4_e_active_experiments.py`), same seed
(20260821), same arms (`ORION_DECISION_VOI` treatment vs `LLM_PROXY_HEURISTIC`
and `INFOGAIN` comparators), same metric (`utility`), same paired estimand
(per-episode difference, mean over episodes). The extension only **continues
the frozen RNG stream**: the frozen 400-episode list is generated first
(`random.Random(20260821)`, draws 1..400, byte-identical to the frozen
analysis by determinism of the stream), then the same list is extended in
place on the same stream to `N_EXT = 4000` (episodes 401..4000 = new,
pre-outcome-registered mass). N4-E is a single flat episode list (no regime
blocks), so the N4-B A1 layout hazard does not arise; the P1 prefix gate is
registered anyway.

## Power arithmetic (from the frozen intervals only)

Per-pair sd estimated from the frozen CI half-widths (÷1.96, ×√400):

- `voi_vs_llm_proxy`: half-width 0.1466 → se(400) ≈ 0.0748 → sd ≈ 1.50.
- `voi_vs_infogain`: half-width 0.1614 → se(400) ≈ 0.0824 → sd ≈ 1.65.

At `N_EXT = 4000` (10×): se ≈ sd/√4000 → proxy ≈ 0.0237, infogain ≈ 0.0260.
Bonferroni-97.5% half-widths (z ≈ 2.24) ≈ 0.053 and 0.059.

- **P-PROXY:** if the frozen point estimate holds, predicted interval ≈
  [+0.224, +0.330] → excludes zero (z ≈ 11.7). Prediction:
  `RESOLVED_POSITIVE`.
- **P-INFO:** predicted interval ≈ [2.087, 2.204] → excludes zero by a wide
  margin. Prediction: `RESOLVED_POSITIVE`.

The refutation risk that motivated the N4-B extension is materially smaller
here (frozen z ≈ 3.7 for the proxy row vs ≈ 1.0 for the N4-B STALE row), but
the extension is what makes that statement data-backed rather than asserted:
either the proxy margin tightens to a certified positive, or it collapses to
a bounded null and the manuscript's "surviving" claim for that contrast is
corrected — both are outcomes the protocol ranks equally.

## Registered practical-equivalence bound

δ = 0.3 utility, chosen from the frozen data alone: it is ≈ 1/7 of the
study's other resolved contrast (`voi_vs_infogain`, +2.1455) — the same
1/7-of-smallest-resolved-anchor rule the N4-B extension used — and ≈ 1.5% of
the episode reward scale (`REWARD = 20.0`). A proxy advantage confined to
|effect| < 0.3 could not carry the manuscript's qualitative claim that
decision-coupled acquisition beats the fixed-heuristic proxy by a margin
comparable to its other separators. `BOUNDED_NULL` requires the corrected CI
⊂ (−δ, +δ); sign-exclusion is evaluated first, so a genuine +0.28 effect with
CI [+0.22, +0.33] resolves positive, never "bounded null".

## Registered predictions (non-vetoing, always reported)

- P-PROXY resolves `RESOLVED_POSITIVE` (97.5% CI excludes 0, favors
  ORION_DECISION_VOI).
- P-INFO resolves `RESOLVED_POSITIVE`.
- Continuity (monitoring, not a target): both full-sample point estimates
  within ±10% of the frozen values.
- Split-half (first 2000 vs second 2000, monitoring only, **not registered as
  a gate** — under a true ≈0 effect halves straddle zero routinely; N4-B
  empirics confirmed this).

## Terminals

Per target: `RESOLVED_POSITIVE` / `RESOLVED_NEGATIVE` (Bonferroni-97.5% CI
excludes 0) / `BOUNDED_NULL` (CI ⊂ (−δ, +δ)) / `UNRESOLVED` (neither).
Study: `N4E_POWER_DETERMINED_BOTH` (both targets resolved or bounded) /
`N4E_POWER_PARTIAL_<which>` / `N4E_POWER_PREFIX_FAIL` (cross-check P1 fails →
no verdict, exit 3). Frozen artifacts untouched; this experiment is additive
under `experiments/n4e-power-extension-v1/`.
