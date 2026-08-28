# ORION-02 — one mechanism behind four consecutive negatives

**Protocol identity:** `ORION02.VALIDITY_UTILITY_FRONTIER.v1`
**Status:** `DIAGNOSTIC_SYNTHESIS` · `scientific_authority_delta = NONE`

This does not run new science. It reads four committed negatives and reports that they
are one failure, not four.

## The four negatives

| round | committed terminal | what failed |
|---|---|---|
| R18 | `FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE` | `coverage` and `route_beats_full_model` |
| R22 | `C_R22_PMLB_PROPOSAL_ORDERING_CERTIFICATE_INVALID` | held-out certificate validity |
| R23 | `C_R23_PMLB_BACKOFF_CERTIFICATE_INVALID` | coverage, then validity |
| R24 | `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` | held-out validity at full coverage |

## They fail in opposite directions

**R18 — the certificate is too loose to ever act.** From
`FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json`, at cutoff `1800.0` s:

| paired mode | quantile range | as multiple of cutoff | `route_change_coverage` |
|---|---|---|---|
| `direct_difference` | 12035.3 – 17304.2 | **6.7× – 9.6×** | **0.0** |
| `interval_no_harm` | 12314.4 – 17455.0 | **6.8× – 9.7×** | **0.0** |
| `paired_upper` | 11133.3 – 17392.3 | **6.2× – 9.7×** | **0.0** |

Every conformal quantile sits six to ten times the solver cutoff, so the certificate's
interval contains every candidate and **never licenses a single route change** — in all
three modes, in every fold. The panel gate records exactly this: `coverage: false` and
`route_beats_full_model: false`, while `catastrophic_no_worse`, `p95_no_worse`,
`certificate_failure` and `full_model_beats_no_feature_fallback` all pass.

This is a **vacuity** failure, not a performance failure. The underlying learning works:
the one-sided learned arm cuts the catastrophic rate from `0.2691` (no-feature fallback)
to `0.1624`, and mean total cost from `4860.7` to `2967.5`, against an oracle at
`0.0982` / `1811.3`. The paired *certificate* then declines to use any of it.

**R22–R24 — the certificate is tight enough to act but not valid.** R24 reaches full
coverage `44/44` and then fails held-out validity at `20/44 = 45.5 %` strict violations
against a registered `0.10` cap. Its floor is structural: every pool branch gates
eligibility on `excess <= tau + TOL`, so `bound = max(pool) <= tau` identically —
verified across all 704 rows, 0 exceptions — giving
`violations_strict >= violations_tau = 11/44 = 25 %`. The `0.10` gate was unreachable
for that committed-classifier assignment.

## The synthesis

> Across four rounds, no certificate construction has occupied an operating point that is
> **simultaneously valid and non-vacuous**. Loosen it enough to be valid and it licenses
> nothing (R18: coverage 0 at 6–10× cutoff). Tighten it enough to license action and it
> violates its own risk gate (R22/R23/R24: 25–45 % against a 10 % cap).

The rounds are not four independent misses. They are four probes of the same
**validity–utility frontier**, approached from opposite sides, and the paper has never
exhibited an interior point.

## Why this matters for the manuscript

The current framing reads as a sequence of repairs that each nearly worked. The evidence
supports a stronger and more defensible claim: the paper has **empirically traced a
frontier**, and the interesting result is the frontier itself rather than any single
round's shortfall.

Note the direction this points. R18 shows the learned signal is real and substantial
(0.2691 → 0.1624 catastrophic). What fails is the wrapper that turns a signal into a
guarantee. So the residual contribution is about *certification*, not about whether
fibre geometry predicts — and the R24 result independently says geometry supplies no
value over the lexical control.

## Relation to the preregistered successor

This is the empirical counterpart of #1615 Priority 2
(`ORION02.FIBRE_AMBIGUITY_RISK.v1`), whose accepted-fibre diameter lower bound predicts
exactly such a frontier: if a fibre has target diameter `D(z)`, any accepted point
certificate carries worst-case error at least `D(z)/2`, so validity below that radius is
unattainable and validity above it is uninformative.

Four rounds are consistent with that prediction. They do **not** prove it: none of them
measured `D(z)` directly, so the frontier is observed, not explained.

`ORION02.SELECTIVE_FIBRE_RISK.v1`, preregistered in
`experiments/selective-fibre-risk-v1/`, should therefore add one thing this synthesis
cannot supply — **a direct measurement of `D(z)` on the accepted fibres**, so the
observed frontier can be compared against the predicted `D(z)/2` floor. If they agree,
the negatives become a theorem with evidence. If the observed frontier sits well above
`D(z)/2`, something other than fibre ambiguity is binding, and that is a new lead.

## Limits

- This is a reading of committed results, not a new run. No number here is new.
- R18 and R22–R24 use different corpora (ASlib MaxSAT/QBF portfolios vs PMLB) and
  different measures (PAR10 vs excess). The frontier claim is about the shape of the
  failures, not a pooled quantitative comparison, and must not be reported as one.
- "No interior point has been exhibited" is not "no interior point exists". Four probes
  are four probes.
