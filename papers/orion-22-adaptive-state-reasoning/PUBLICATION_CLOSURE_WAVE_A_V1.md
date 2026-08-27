# ORION-22 Publication Closure Wave A V1

## Maximum current claim

ORION-22 has bounded verifier-backed allocation/path evidence and an unchanged allocator transfer across SAT, procedural path, and knapsack tasks. The named open gate is robustness under resource-price changes, task-distribution shift, and hidden parameterization. Wave A should execute the existing frozen suite if its identities are complete; it must not silently replace it with a new easier benchmark.

## Good specialist finish

- [ ] Reconcile the current three-domain 9/9 result, exact rule identity, verifier evidence, resource vectors, negative regimes, and independent checker into one claim authority/manuscript.
- [ ] State the small-denominator and controlled-domain limits prominently.
- [ ] Complete target selection, clean replay, final figures/tables, current PDF audit, and package binding.

## Step 1 — locate and validate the frozen robustness authority

An AI session must first inspect all ORION-22 protocol, promotion, receipt, claim-ledger, and execution files and answer mechanically:

- [ ] Is the price-shift/task-shift/hidden-parameter suite frozen before outcomes?
- [ ] Are exact subject, task denominator, seeds/splits, allocator, comparator, resource-price vectors, hidden parameters, endpoints, margins, and terminals content-bound?
- [ ] Is the executor outcome-blind and independently testable?
- [ ] Has any outcome already been observed on another branch/PR?

If any identity is missing, commit a prospective protocol repair before execution. Do not infer or backfill outcome-dependent values.

## Robustness dimensions

### A. Resource-price shift

- Freeze at least three qualitatively different public price vectors, including one where the current allocator should not be optimal.
- Charge preprocessing, state/memory, model/solver compute, search, tool/verifier calls, latency, cache/reuse, and recovery/reconstruction.
- Compare policy decisions, regret, safety/correctness, and resource use.

### B. Task-distribution shift

- Use public held-out instances/families not used to construct or tune the allocation rule.
- Preserve domain-native correctness via SAT/optimization/path verifier.
- Report per-family outcomes; pooled success may not hide a failed family.

### C. Hidden-parameter audit

- Hide parameters from every arm unless the deployed contract supplies them.
- Include misspecified and partially observed parameters.
- Audit whether ORION obtains hidden information through preprocessing, cached state, or evaluator coupling.
- Register `CANNOT_CHECK` when the optimal decision cannot be identified from public/verifier-backed information.

## Required comparators

- fixed/flat allocation;
- simple myopic value-per-cost allocation;
- strongest native/domain allocator;
- oracle upper bound, labelled unattainable;
- donor-composed allocator with the same observable state and resource vector;
- unchanged ORION-22 allocator.

No arm may receive different verifier access, hidden parameters, preprocessing, or cached outcomes.

## Primary endpoints

- task correctness/verified success;
- regret against the frozen attainable oracle;
- catastrophic invalid decision rate;
- allocation stability/change under price shift;
- resource vector and Pareto dominance;
- robustness coverage and CANNOT_CHECK rate;
- per-domain/family effects.

Freeze uncertainty/multiplicity and a non-compensatory correctness/safety gate before execution.

## Hostile controls

- [ ] scale all prices uniformly—decision should obey the registered invariance, if claimed;
- [ ] swap relative prices to create a known policy change;
- [ ] hide a load-bearing parameter;
- [ ] add irrelevant observable features;
- [ ] permute task order and identifiers;
- [ ] create a regime where fixed allocation is optimal;
- [ ] verify oracle and regret independently on small exact instances;
- [ ] mutation-test resource accounting and missing-run handling.

## Registered terminals

Use the existing frozen terminal names when present. At minimum distinguish:

- `ROBUST_UNDER_REGISTERED_SHIFTS`
- `PRICE_SHIFT_POLICY_FAILURE`
- `TASK_SHIFT_GENERALIZATION_FAILURE`
- `HIDDEN_PARAMETER_LEAK_OR_UNIDENTIFIABLE`
- `NO_ADVANTAGE_OVER_DONOR_ALLOCATOR`
- `ROBUSTNESS_SUITE_CANNOT_CHECK`

## Required artifacts

- [ ] frozen/validated protocol receipt;
- [ ] public dataset/instance/version/licence manifest;
- [ ] exact price/parameter vectors;
- [ ] baseline fidelity tests;
- [ ] raw allocation and verifier records;
- [ ] complete resource and failure ledger;
- [ ] independent oracle/regret implementation;
- [ ] deterministic replay where claimed;
- [ ] generated robustness figures/tables;
- [ ] result-bound claim and package update.

A null/adverse robustness result does not invalidate the current bounded three-domain paper. It sets the correct specialist scope and must remain visible.
