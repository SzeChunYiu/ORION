# P1 prospective power and precision — computed before any outcome access

**Bound to:** protocol `P1.hidden-formulation.v1.1`, suite PILOT `7a50a2d5…` /
TEST `21b461d8…`. Derived from the frozen margins and the frozen N only. No
outcome, pilot or live, was read to produce any number here.

## The headline, stated first because it changes what may be claimed

**The frozen suite cannot test H1 at the frozen margin.** H1 asks for a +0.05
absolute root-success improvement over the strongest matched baseline. At 80%
power and two-sided α=0.05, a paired binary comparison needs roughly **3,140
discordant pairs** to resolve a 0.05 difference — between **7,800 and 12,600
cases** depending on discordance rate. The frozen TEST split has **48**.

This is a shortfall of two orders of magnitude, and it is not fixable by running
more seeds. The protocol binds the analysis unit to the case with stochastic
repeats reduced before any interval is computed, so `n` is the number of cases
and never cases × seeds. That reduction rule is correct — it prevents
manufacturing significance from repeated draws on the same item — and it is
exactly why repetition cannot buy power here.

## What 48 cases can actually resolve

Wilson 95% half-width at the frozen N:

| split | n | p=0.5 | p=0.7 | p=0.9 |
|---|---|---|---|---|
| TEST, all | 48 | ±0.136 | ±0.126 | ±0.087 |
| hidden-shift | 32 | ±0.164 | ±0.152 | ±0.107 |
| negative controls | 16 | ±0.220 | ±0.205 | ±0.153 |

A ±0.136 interval cannot adjudicate a ±0.05 margin. For the H2
non-inferiority guard at +0.02 the mismatch is worse: the controls subgroup
carries a ±0.220 half-width, eleven times the margin it is meant to police.

Required N for the precision the margins presuppose:

| target half-width | at p=0.5 | at p=0.8 |
|---|---|---|
| < 0.05 | n ≈ 382 | n ≈ 246 |
| < 0.02 | n ≈ 2,398 | n ≈ 1,536 |

## Sensitivity, not a single opaque N

Paired detectable difference at 80% power, by discordance rate — the fraction of
cases where the two systems disagree, which is what a paired test actually
consumes:

| true difference | discordant pairs needed | N at discordance 0.25 | N at discordance 0.40 |
|---|---|---|---|
| 0.05 | 3,140 | 12,558 | 7,849 |
| 0.10 | 785 | 3,140 | 1,962 |
| 0.15 | 349 | 1,395 | 872 |
| 0.20 | 196 | 785 | 491 |
| 0.30 | 87 | 349 | 218 |

At n=48 and a generous 0.40 discordance, roughly 19 discordant pairs are
available, which resolves a difference of about **0.64** — a difference so large
that any system showing it would not need a statistical test.

## The three honest options, and the one this study should take

1. **Enlarge the suite to ~8,000 cases.** Correct, and infeasible: these are
   hand-constructed cases with protected gold, and 8,000 of them cannot be
   authored without generating them from templates, which would reintroduce
   exactly the template leak that took three rounds to remove.
2. **Widen the margin prospectively** to something 48 cases can resolve. Legitimate
   *only* because it is being done before outcome access, and it must be recorded
   as an amendment rather than edited in place. But a margin of 0.30+ is not a
   scientifically interesting threshold for this claim.
3. **Reclassify H1 as estimation rather than a powered test.** Report the
   difference with its interval and state plainly that the design cannot reject a
   0.05 effect. This is what the evidence supports.

**Recommendation: option 3, with option 1 named as the path to a powered test.**
The study still yields a real result — H2's selectivity contrast, H3's reopen
comparison against a computed mechanism-free floor, H4's stability by depth, and
the mechanistic metrics are all informative at this N because their effects are
large and structural rather than marginal. What must not happen is reporting
"H1 NOT_SUPPORTED" from 48 cases as though it were a null result. It would be an
underpowered non-finding wearing the clothes of evidence.

## Why this had to be computed before the run

Had the live trial run first, the arithmetic above would have arrived after a
verdict existed, and every choice among the three options would have been
contaminated by knowing which one flattered the result. The protocol records
`outcome_accessed: false`; this document is what that field is for.

## Consequence for the frozen statistics

`UNDERPOWERED` was previously unreachable, because the protocol named a
prospective power analysis and bound no N, so the minimum-units floor defaulted
to zero and no verdict could fall through to it. With N now derived, the floor is
bindable and the verdict is reachable. A comparison whose N cannot resolve its
own margin should return `UNDERPOWERED`, not `NOT_SUPPORTED` — those say
different things, and only one of them is true here.
