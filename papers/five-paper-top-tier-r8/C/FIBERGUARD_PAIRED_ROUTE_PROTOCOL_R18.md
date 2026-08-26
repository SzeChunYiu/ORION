# FiberGuard R18 — prospective paired routing on new MaxSAT and QBF portfolios

Date: 2026-08-26

Status at this commit: protocol only; no R18 outcome has been computed or admitted.

Parent theory: R17 head `f34b61e0051289588eaf144a580dca7bc9b7e707`.

## Question

R16 showed that a marginal certificate for a learned action can be well calibrated while abstention is harmful because the fallback is worse on rejected cases. R17 proved that selective value is controlled by `F-L` on the rejected set and that a learned-action certificate alone cannot bound fallback harm.

R18 asks prospectively:

> Does jointly certifying learned and fallback losses, or directly certifying their difference, produce paid routing value on new solver portfolios?

The subjects were not used in R14--R17:

- development: `MAXSAT12-PMS`;
- validation without retuning: `MAXSAT19-UCMS`;
- untouched cross-domain test: `QBF-2016`.

## Declared measures and acquisition cost

Each scenario must expose exactly one declared performance measure and `maximize=false`. Raw runtime scenarios use median `ok` runtime and PAR10 for every non-`ok` run. A declared PAR10 scenario uses that measure directly and checks non-`ok` values against the PAR10 cutoff convention. Timeout and broader non-`ok` failure are reported separately.

The paid acquisition step is `group_basics`, `ALL`, and `base`, respectively. Every learned and routed policy pays its scenario's recorded feature cost. The no-feature fallback pays none. All losses are excess over the same statewise virtual-best solver under the declared measure.

## Nested custody

For official test fold `f` in repetition 1, fold `1+(f mod 10)` is calibration and the other eight folds are proper training. Proper-training outcomes fit the regret model and robust fallback. Calibration outcomes form the certificate. Test outcomes do neither.

Only MAXSAT12 selects the model, `alpha`, and route mode. MAXSAT19 validates the frozen tuple. QBF-2016 is the untouched final test. Solver models are refit within each scenario because portfolios differ; the model/route/certificate construction transfers unchanged.

## Three paired certificate modes

Let `L,F` be realized learned and fallback regrets and `Lhat,Fhat` their predicted values.

1. **Paired upper:** calibrate `max(L-Lhat,F-Fhat)` and choose the action with the smaller certified upper loss.
2. **Interval no-harm:** calibrate `max(|L-Lhat|,|F-Fhat|)` and switch from learned to fallback only when fallback upper is no larger than learned lower.
3. **Direct difference:** calibrate `|(F-L)-(Fhat-Lhat)|` and switch only when the upper certificate on `F-L` is nonpositive.

All are marginal split-conformal statements under exchangeability. Paired-upper certifies selected absolute loss on the simultaneous-validity event. The latter two certify non-worsening switches on their validity event. None grants worst-case fibre, conditional-deployment, family-shift, or pathwise safety.

## Frozen search and gates

The development menu has eleven model specifications, three `alpha` values, and three route modes: 99 candidates. A development candidate is feasible only if it changes route on at least 5%, strictly improves mean against both full learned and no-feature fallback, does not worsen catastrophic rate or p95 against full learned, and has empirical certificate-failure rate at most `alpha+0.02`.

Validation/test panels additionally require the full model to beat no-feature fallback and the frozen route to improve mean, preserve catastrophic rate and p95, change route on at least 5%, and satisfy the certificate-failure check.

Required references include frozen 16-NN and frozen ExtraTrees full selectors, the global robust fallback, the full selected learned model, one-sided learned-action routing, all three paired modes, and the oracle contextual route.

## Authority boundary

A positive strongest terminal would establish one method/configuration transfer from MaxSAT12 through MaxSAT19 to an untouched QBF portfolio under official-fold exchangeability. It would not establish deterministic worst-case safety, arbitrary domain shift, strongest-baseline completeness, external reproduction, production deployment, novelty, or journal authority.

A development, validation, or QBF failure is a first-class scientific terminal and may not be repaired by inspecting its outcomes.
