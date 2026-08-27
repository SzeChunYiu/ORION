# ORION-02 C-NBR2 — certified-neighborhood revival disposition

> Revival pass on the V1 `CERTIFICATE_INVALID` verdict (commit `87e7860f`, PR #1486),
> executed under the frozen protocol `CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md`
> (SHA-256 `79309ec0…d82be932`, commit `31ee8705`) by
> `certified_neighborhood_conformal.py` (SHA-256 `f2b0e572…`). Machine-readable source
> of truth: `results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V1.json`.

## Parent failure (one-stage attribution)

V1 failed at the **certification-constant stage**: the pairwise-slope Lipschitz
constant `L` (PAR10 per feature unit) made the certified radius
`eps / L` far smaller than any held-out nearest-anchor distance, so no certificate
ever fired — coverage 0.0000, CNF systems degenerate to SBS.

## Lever applied (this revival)

Replace the distribution-free pairwise-slope `L` with a **split-conformal calibrated
constant** `q_hat` (order statistic over calibration residuals, fail-closed to
infinity), pooled and PCA10 and Mondrian-3 variants. This is the standard tighter
data-driven alternative and needs no new theorem authority.

Outcome: `q_hat` = **3348.0 / 3375.2 PAR10 per unit** (official-fold / family-disjoint)
— **21–25% tighter than V1's pairwise-slope `L`**, self-test GREEN, protocol hash bound.

## Re-test result — still unaffordable (the boundary result)

- Certified radius at the protocol's `eps = 5000`: `≤ 5000/3348 ≈ 1.5` units.
- Held-out nearest-anchor distances: **median 14.1 / 16.8 units** — a ~10× gap.
- Certified coverage **0.0000** on both splits, all three relations, and the
  exact-equality control (5× = 0.0000). CNF_POOLED / CNF_POOLED_PCA10 / CNF_MONDRIAN3
  all degenerate to SBS exactly (`SBS − CNF_POOLED: 0.00 [0.0, 0.0]`).
- Overall verdict: **`VALID_WITHOUT_COVERAGE_OR_VALUE`**,
  disposition `EXECUTED__FROZEN_PROTOCOL_APPLIED`.

## Terminal disposition

The certification-constant stage is **exhausted**: the conformal lever bought 21–25%
and the affordability gap is ~10×, so no realistic calibration refinement closes it.
The blocker is geometric — anchor-set spacing (14–17 units) against the loss scale
(PAR10/unit) — not the certification method. A further revival would have to change
the *representation* (feature geometry that shrinks nearest-anchor distances by an
order of magnitude) or the *loss scale*, which is a different mechanic, not a tighter
bound on this one. **C-NBR lane closed terminal** on this harness
(`VALID_WITHOUT_COVERAGE_OR_VALUE`); no fourth attempt queued.

## Claim boundary

One bounded public scenario (ASlib fold + family-disjoint split); no ASlib-wide,
SAT-wide, cross-domain, or selective-prediction superiority claim. The conformal
bound is a finite-sample **marginal** guarantee under exchangeability — not
conditional-on-covariates validity. Certificate coverage is not action authority.
