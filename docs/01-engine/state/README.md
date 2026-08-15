# Mechanic state

ORION distinguishes an execution's state from its observations and from the final knowledge state.

Every mechanic V0 state envelope names:

- run/attempt identity;
- immutable input snapshot identity;
- exact mechanic version;
- exact dependency/evaluator/provider/tool bindings material to execution;
- transition-controlled lifecycle phase;
- mechanic-local working-state digest;
- finalized output-state identity.

State changes are licensed only through declared transitions/events. Hidden mutation outside the transition/receipt lineage is a reproducibility defect.

## Replay and variation

A rerun with different inputs, mechanic version, evaluator, provider/tool binding or other material dependency is not a strict replay unless the difference is explicitly represented as a variation. This matters for failure learning: two similar failures under different hidden states cannot safely be treated as repeated evidence of one failure class.

## Boundary

The envelope makes execution state inspectable and comparable. It does not identify the scientific/algorithmic state variables specific to SEARCH, ABSORB, GLUE, DIAGNOSE, and other mechanics. Each cell therefore retains an empirical-open coordinate for its step-specific state variables, transition graph, latent-state identifiability and replay fidelity.
