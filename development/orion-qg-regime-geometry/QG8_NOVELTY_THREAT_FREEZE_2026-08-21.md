# QG-8 hostile novelty / donor-threat freeze — 2026-08-21

Status: FROZEN BEFORE QG-8 MACHINE OUTCOME.
Issue: #760
Literature cutoff: 2026-08-21.
Authority: novelty threat register only; `NO_CLOSE_PARENT_FOUND` is not novelty authority.

## Candidate residual

Only this object is under candidate novelty review:

> An exact quantum-compiler normal-form phase theorem that maps a region of objective-parameter space to an all-n finite-support optimality bound, using a semantics-preserving local exchange with a machine-checked resource vector; critical objective hyperplanes are proof-certificate boundaries and may seed a larger support/regime phase diagram.

## Mandatory absorbed parents

### Multi-objective / Pareto quantum compilation

Świerkowska, Echavarria, Schulz & Schulz, *Achieving Pareto-Optimality in Quantum Circuit Compilation via a Multi-Objective Heuristic Optimization Approach* (IEEE QCE 2024), Munich Quantum Compiler.

Disposition: **ABSORB** multi-objective compiler optimization and Pareto-optimal compiler-pass selection. QG-8 cannot claim novelty for optimizing more than one cost coordinate or using weighted scalarizations.

### Scalable multi-objective quantum circuit optimization

Ghlib, Bouhadouza & Hnaien, *Scalable multi-objective genetic algorithm for quantum circuit optimization*, Scientific Reports 16, 17977 (2026). Joint fidelity/depth/hardware-cost Pareto optimization with block decomposition.

Disposition: **ABSORB** Pareto fronts over fidelity/depth/gate cost and weighted hardware-aware cost as established quantum-circuit optimization practice.

### General parametric / polyhedral optimization

Parametric linear optimization, critical hyperplanes, normal fans, piecewise-linear value functions, Pareto fronts and polyhedral parameter regions are classical optimization mathematics.

Disposition: **ABSORB** the mathematics of objective-parameter cells/half-spaces. QG-8 can only claim a compiler-specific theorem obtained from its semantic exchange/cost certificate.

### Parametrised quantum circuit compilation

van de Wetering, Yeung, Laakkonen & Kissinger, *Optimal compilation of parametrised quantum circuits* (2024), proves optimal parameter counts for a circuit class using ZX-calculus.

Disposition: **ABSORB** optimal-compilation theorem methodology and parametrised circuit compilation as prior art. This is not the same use of “parameter”: QG-8 parameters are objective coefficients, not circuit angles, but the broader theorem territory must be credited.

## Current hostile-search result

No close parent has been identified that simultaneously:

1. starts from a fixed quantum compilation family and an exact semantics-preserving rewrite;
2. attaches an explicit resource-change vector to every local rewrite instance;
3. derives a polyhedral region of objective coefficients in which the rewrite is globally non-increasing;
4. composes that local certificate with a finite-field zero-sum argument to prove an **all-n optimal support normal form** throughout that region;
5. identifies equality hyperplanes as exact boundaries of the proof certificate;
6. binds outside-region global counterexamples showing the support normal form can genuinely change with objective.

This remains a **candidate residual only**.

## Falsifiers

Novelty narrows or collapses if a donor is found that already provides materially the same objective-indexed all-n support-normal-form theorem for Pauli/block-encoding/quantum compiler families, or a general compiler theorem that directly subsumes the QG-8 construction.

## Allowed current language

`NO_CLOSE_PARENT_FOUND_FOR_OBJECTIVE_INDEXED_ALL_N_COMPILER_SUPPORT_PHASE_THEOREM__NOVELTY_NOT_AUTHORIZED`

Forbidden before independent review:

- `first objective phase diagram in quantum compilation`;
- `novel polyhedral optimization method`;
- `new Pareto compilation method`;
- any physical quantum-advantage claim.
