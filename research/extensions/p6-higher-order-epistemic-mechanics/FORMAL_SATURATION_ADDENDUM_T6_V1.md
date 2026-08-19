# #463 saturation addendum — T6 evidence-dependence / adaptivity

**Date:** 2026-08-19  
**Timing:** added before any #522 exact-head CI outcome.  
**Effect on candidate terminal:** none.

## Gap found in closure review

The main parent map contains eight **formal component families** used by the T1–T7 state/mechanic/control product. #463 also listed a candidate proposition T6:

> a claimed adaptive revision policy should change behavior under outcome/evidence interventions or permutations in the dimensions it claims to use.

T6 is not an additional state/mechanic primitive in the implemented calculus. It is an **evaluation/non-vacuity criterion** for whether a policy functionally depends on evidence.

## Parent attribution

- Judea Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed. (2009), supplies mature intervention/counterfactual semantics; an intervention changes a structural mechanism while holding the rest of the model fixed according to the declared intervention.
- Gupta, Hartford & Liu, *LLMs for Bayesian Optimization in Scientific Domains: Are We There Yet?*, arXiv:`2509.21403`, supplies a direct scientific-agent control: replacing experimental outcomes with randomly permuted labels did not change performance in their tested LLM agents, demonstrating why feedback sensitivity must be tested rather than inferred from architecture labels.

## Disposition

`ADOPT_CAUSAL_INTERVENTION_SENSITIVITY_AS_EVALUATION_CRITERION`

Consequences:

1. strike any #463 novelty claim for “adaptivity means behavior changes when evidence is intervened on”;
2. keep outcome permutation/removal/contradiction as T8/#455 hostile controls;
3. do not add a ninth formal component to the T1–T7 mechanics product, because T6 evaluates the policy mapping rather than introducing a new epistemic state coordinate or transition algebra;
4. a future policy that passes T6 still gains no scientific/adoption authority from sensitivity alone.

This completes proposition-level attribution without changing the parent-component count, finite signature family, or recommended #463 terminal.
