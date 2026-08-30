# ORION24.STRATUM_TRANSPORT_PARTIAL_IDENTIFICATION.v1

## Question

When a governance system has a strong measured advantage on a controlled source distribution, what can be inferred about its average advantage in a target population whose semantic-stratum composition and/or unmeasured stratum effects differ?

This matters for ORION-24 because the internally authored P14C benchmark is deliberately balanced and its strongest baseline failures are concentrated in particular semantic cases. The existing result is valid on that specification. A broader scientific-validity claim requires transport, not just more source-distribution replay.

## Model

Partition the target population into semantic strata `s in S`. Let

- `pi_s >= 0`, `sum_s pi_s = 1`, be target-population stratum weights;
- `delta_s = E[Y_ORION - Y_BASELINE | s]` be the stratum-specific advantage on a bounded score `Y in [0,1]`.

Thus `delta_s in [-1,1]`.

Suppose stratum-specific effects are established only for an observed subset `O`. Let `U=S\O` be the unobserved strata and

`A = sum_{s in O} pi_s delta_s`,

`W = sum_{s in U} pi_s`.

The target average advantage is

`Delta = A + sum_{s in U} pi_s delta_s`.

## Theorem 1 — sharp partial-identification interval

Without additional assumptions on the unobserved stratum effects beyond `delta_s in [-1,1]`,

`Delta in [A-W, A+W]`.

The interval is sharp.

### Proof

For every unobserved stratum, `-pi_s <= pi_s delta_s <= pi_s`. Summing gives `-W <= sum_U pi_s delta_s <= W`, hence the interval. The lower endpoint is attained by setting every unobserved `delta_s=-1`; the upper endpoint by setting every unobserved `delta_s=+1`. Both assignments satisfy the model, so no narrower universal interval follows. QED.

## Corollary 1.1 — when is the sign identified?

A strictly positive target advantage is guaranteed **iff**

`A - W > 0`.

A strictly negative target advantage is guaranteed **iff**

`A + W < 0`.

Otherwise the sign is not identified from the observed strata alone.

This is a worst-case transport statement. It does not say unobserved strata are adversarial; it says their behaviour has not been measured or otherwise constrained.

## Corollary 1.2 — one observed stratum

If only one stratum has measured advantage `d` and its known target weight is `p`, then

`Delta in [p d - (1-p), p d + (1-p)]`.

For `d>0`, positivity is guaranteed only when

`p d > 1-p`, i.e. `p > 1/(1+d)`.

Even a perfect `d=1` on one stratum cannot by itself guarantee a positive population average unless that stratum has target weight greater than one half or additional constraints are supplied for the rest.

## Theorem 2 — source-average performance does not identify target-average performance without transport information

Suppose two worlds have the same complete source benchmark—including every source-case output and source average—but differ in target stratum weights or unmeasured target stratum effects. If those target quantities are absent from the observable source transcript, the target average can differ between the worlds while the source evidence is identical.

Therefore target-population performance is not identifiable from source-average performance alone.

This is an information boundary, not a criticism of the source benchmark.

## Corollary 2.1 — balanced source designs answer balanced-source questions

A benchmark that assigns equal mass to semantic strata estimates performance on that balanced benchmark. It does not automatically estimate a naturally occurring population with different prevalence. Balance is valuable for refutation capacity and construct coverage; prevalence-weighted transport is a separate estimand.

## What closes the interval

The partial-identification interval narrows when the study prospectively supplies one or more of:

1. direct measurements of `delta_s` in previously unobserved target strata;
2. externally justified bounds `[L_s,U_s]` tighter than `[-1,1]`;
3. independently estimated target weights `pi_s`;
4. a structural invariance theorem whose assumptions are themselves externally checked.

With stratum-specific bounds, the exact extension is

`Delta in [sum_s pi_s L_s, sum_s pi_s U_s]`,

using point bounds `L_s=U_s=delta_s` for measured strata.

## ORION-24 successor consequence

The next blinded external validation should report **stratum-specific** outcomes and target-weight provenance, not only one pooled score. At minimum it should preserve the already planned negative-retention stratum and an ordinary-positive/mixed stratum, keep family as the inference unit, and retain adverse strata.

For a claim of target-population superiority, the paper should publish the resulting transport interval. If zero lies inside it, the correct population-level terminal is `TARGET_SIGN_NOT_IDENTIFIED`, even if the balanced-source benchmark remains strongly favourable.

## Relation to current P14C authority

Nothing here weakens `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`. P14C establishes strong conformance on its separately frozen internally authored specification and is robust to the registered internal checks. This theorem states exactly why that result and a mixed external target-population claim are different estimands.

## Claim boundary

Earned deductive claim:

> With bounded stratum effects and unmeasured target mass `W`, the sharp target-average advantage interval is `[A-W,A+W]`; a positive target effect is identified only when its lower endpoint exceeds zero.

Not earned:

- target-population weights;
- unmeasured external stratum effects;
- blinded external scientific validity;
- frontier-agent superiority.

`scientific_authority_delta: NONE`
