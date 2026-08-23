# P9 unified I/A/C/M resource-ledger protocol V1

**Programme:** #977  
**Role:** post-outcome accounting completion for already-frozen P9 intervention studies; this protocol may not change any scientific outcome, quality target, intervention choice or protected disposition.

## Purpose

P9's higher claim separates semantic information (`I`), representation accessibility (`A`), downstream computation (`C`) and access/model mechanism (`M`). The scientific comparisons are not publication-ready if one intervention appears cheaper only because transformation, fit, model-state or inference work is omitted.

This accounting pass therefore binds a common **vector schema** to the frozen P9 causal-diagnostic cells. It explicitly forbids a post-hoc scalar cost across heterogeneous domains.

## Frozen source authority

The accounting script must reproduce the exact train/probe/protected splits and interventions from `P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md`. It may recompute model shapes and deterministic work proxies but may not alter:

- quality targets;
- intervention semantics;
- registered selection costs;
- protected causal gold;
- predicted intervention;
- the `D-A` protected `CANNOT_CHECK` cell;
- the Qwen negative or earlier P9 results.

## Unified vector

Every intervention cell emits:

`R9 = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)`

where:

- `I_sem`: semantic information coordinates/bits exposed to the arm;
- `A_dim`: representation dimension delivered to the access mechanism;
- `A_transform`: deterministic representation-transform coordinate touches per evaluation example;
- `M_state`: fitted model-state coordinates (linear coefficients/intercepts, support-vector coordinates, or zero for exact registered computation);
- `C_fit`: deterministic fit-feature touches (`n_train * A_dim`) where a learned access mechanism is fit; zero for exact non-learned tasks;
- `C_infer`: access-mechanism feature touches per evaluation example; for RBF this is support-vector coordinate count; for linear access it is `A_dim`;
- `C_explicit`: explicit deterministic operations per example for registered exact computation/repair not already represented as `A_transform`;
- `R_registered`: the prospectively frozen abstract intervention cost used by the causal selector.

No coordinate is silently free. `R_registered` is not presented as a physical conversion of the other coordinates.

## Same-information and information-change checks

The ledger must explicitly mark whether an intervention changes semantic information:

- `ACCESSIBILITY`: `I_sem` must equal base `I_sem`;
- `COMPUTATION`: `I_sem` and `A_dim` must equal base values unless the frozen protocol explicitly says otherwise;
- `INFORMATION`: any increase in `I_sem` must be recorded and cannot be relabeled as representation repair.

## Matchability rule

Comparisons are reported as vectors or constrained slices. P9 may say one intervention uses less of a named coordinate only when every other materially relevant changed coordinate is shown. It may not derive a universal scalar ranking from these proxies.

## Positive accounting terminal

`P9_UNIFIED_RESOURCE_LEDGER_V1_GREEN` requires:

- all five causal-diagnostic task families represented;
- all three intervention classes represented for each task;
- all eight vector fields present;
- information-preserving interventions explicitly pass the `I_sem` equality check;
- learned-model fit and model-state costs are nonzero where applicable;
- exact computation operations are nonzero where applicable;
- the ledger reproduces the original protected predictions/gold from the bound result receipt without changing them;
- deterministic replay;
- a second checker verifies vector completeness and the information-preservation constraints from the emitted ledger.

A GREEN terminal closes accounting completeness for the bounded P9 causal-diagnostic headline only. It does not establish that heterogeneous resource coordinates admit one universal exchange rate.
