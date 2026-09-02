# ORION-08 — N4-E power extension V1: findings

**Terminal: `N4E_POWER_DETERMINED_BOTH`** (exit 0, first pass, no amendment
needed). Protocol + derivation committed and pushed before the outcome. n =
4000 (frozen 400 = byte-identical prefix, P1 exact 0.0 on both contrasts).
After the N4-B extension turned that study's two zero-containing rows into
bounded nulls, this extension takes the manuscript's remaining weakest
survivor — `decision_voi_vs_llm_proxy`, the surviving comparison *closest to
zero relative to its width* — and resolves it at 10× mass.

## Result

| contrast | frozen (n=400) | extension (n=4000) | 97.5% CI | verdict |
|---|---|---|---|---|
| decision_voi vs LLM proxy | +0.2770 [+0.119, +0.412] | **+0.3117** | [+0.2538, +0.3677] | **RESOLVED_POSITIVE** |
| decision_voi vs infogain | +2.1455 [+1.976, +2.299] | **+2.1161** | [+2.0543, +2.1778] | **RESOLVED_POSITIVE** |

Bonferroni family m = 2 → per-comparison two-sided 97.5% bootstrap CIs
(5000 draws). Practical-equivalence bound δ = 0.3 registered pre-outcome.

**Reading:** the proxy margin is real and now tight — decision-coupled
acquisition beats the fixed-heuristic proxy by +0.31 utility with the
corrected interval confined to [+0.25, +0.37], i.e. the margin is at least
~8.5× its distance from zero and ~85% of δ. Unlike the N4-B STALE row (whose
frozen +0.774 collapsed to −0.097 under 10× mass), the proxy point estimate
*survived and strengthened* (+0.277 → +0.312). Both registered predictions
(P-PROXY, P-INFO) held.

## Registered predictions — both held

- **P-PROXY (RESOLVED_POSITIVE): held.** CI excludes zero, favors
  ORION_DECISION_VOI.
- **P-INFO (RESOLVED_POSITIVE): held.** Mean within 1.4% of frozen.
- Continuity monitoring: infogain within ±10% of frozen (**yes**); proxy
  **outside ±10%** — +0.312 vs +0.277, a +0.035 shift ≈ 1.5 se(4000) in the
  claim-*strengthening* direction. Reported, non-vetoing, as registered.
- Split-half (monitoring only, not a gate): both halves positive for both
  contrasts (proxy +0.304/+0.319; infogain +2.125/+2.107) — consistent with
  the resolved-positive verdicts and no stream drift.

## Discipline record

Single clean pass; P1 prefix cross-check exact (max |diff| = 0.0 on mean,
CI, and win/tie/loss for both contrasts) on the first run — N4-E's flat
single-block layout makes the N4-B A1 hazard structurally impossible, and
the gate confirmed it rather than assuming it. No amendment. Frozen module,
protocol, and `PUBLICATION_PAIRED_ANALYSIS_V1.json` untouched; this study is
additive under `experiments/n4e-power-extension-v1/`.

## What this changes in the manuscript's limitation

The limitations section's residual concern — the surviving contrast "closest
to zero relative to its width" — is no longer merely surviving: at n = 4000
its corrected interval excludes zero by a factor > 8 and the point estimate
is stable across halves. The manuscript text is frozen; this finding is the
additive successor record a future revision cites (together with
`../n4b-power-extension-v1/`, which bounded the two zero-containing rows).
Every N4-E mean contrast is now either resolved positive (both here) or a
prespecified tie regime (N4-F3 unnecessary, registered outcome).
