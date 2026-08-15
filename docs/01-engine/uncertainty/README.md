# Mechanic uncertainty

ORION does not equate uncertainty with one confidence score.

The V0 baseline distinguishes:

- measurement/instrument uncertainty;
- model/formalism plurality;
- partial identification/bounds;
- open search-universe/coverage uncertainty;
- identity/provenance ambiguity;
- stochastic/external execution variability;
- causal/responsibility ambiguity;
- resource-censored `CANNOT_CHECK`.

A probability distribution is used only when a calibrated sampling/model basis justifies one. Otherwise uncertainty remains an interval, identified set, alternative-hypothesis set, bound, `UNKNOWN`, or `CANNOT_CHECK`.

Uncertainty is reduced only by evidence or assumptions whose authority and scope are explicit. Dropping alternatives, exhausting the budget, or failing to retrieve new sources is not uncertainty reduction.

## Propagation

Each mechanic ultimately needs a step-specific propagation rule. Measurement transforms may require covariance/dependence models; representation mappings may carry approximation error; model sets may propagate to downstream identified sets; search coverage may only support bounded statements about the declared route/source universe. The universal plan records these categories while keeping the exact dependence/calibration/propagation law open.
