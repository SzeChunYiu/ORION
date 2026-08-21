# ORION-QN donor threat — routing, end-to-end advantage, verification and authority

Status: **HOSTILE NOVELTY/OWNERSHIP REVIEW — RESIDUAL OPEN, NO NOVELTY CLAIM**  
Programme: `SzeChunYiu/ORION#734`  
Date / cutoff: **2026-08-21**

This packet attacks the residual left after `S2_S3_DONOR_ABSORPTION_2026-08-21.md`.

## 1. Candidate residual under attack

Previous bounded candidate:

> proof-carrying quantum eligibility under heterogeneous incumbents — bind theorem-valid quantum execution, access/oracle derivability, resource evidence, a strong classical incumbent and a bounded authority terminal without laundering theorem validity into practical superiority.

This sounds broad. The current literature owns most of its obvious components. This packet subtracts them before any novelty language is permitted.

## 2. D5 — Predict and Conquer owns automated quantum/classical algorithm selection

Primary:

- Simon Thelen and Wolfgang Mauerer, **Predict and Conquer: Navigating Algorithm Trade-offs with Quantum Design Automation**, arXiv:`2507.06758` (2025).

Mechanisms:

- source-level characterization of quantum-classical algorithms;
- empirical/statistical models of non-functional properties such as runtime and solution quality;
- automatic algorithm + parameter selection against user requirements/preferences;
- intended generalization beyond the demonstrated combinatorial-optimization case.

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty merely because it predicts whether one quantum/classical algorithm should be selected for a task or optimizes an algorithm/parameter choice from performance models.

## 3. D6 — AutoQuREO owns broad full-stack resource estimation + optimization

Primary:

- Harshkumar Oza et al., **AutoQuREO: A Framework for Automated Quantum Resource Estimation and Optimization**, arXiv:`2608.12936` (2026).

Mechanisms:

- user-defined heterogeneous stack abstraction;
- reusable stack components;
- layer-wise resource surrogate models;
- integrated multi-objective optimization over full-stack design choices;
- application to early-FT algorithms, QEC, decomposition and parametric circuits.

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty for automated full-stack QRE, multi-objective quantum-stack co-design, or choosing a resource-efficient stack configuration.

## 4. D7 — qstack owns compositional end-to-end fault-tolerant compilation

Primary:

- Andres Paz and Dan Grossman, **qstack: Compositional End-to-End Compilation for Fault-Tolerant Quantum Programs**, arXiv:`2605.16595` (2026).

Mechanisms:

- compositional passes across logical, QEC and ISA layers;
- quantum IR with opaque classical callbacks;
- automatic adaptation/wrapping of classical feedback through compilation;
- recursively generated kernels recompiled through the full stack;
- composition of QEC passes.

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty for an IR merely because it preserves hybrid quantum/classical execution across multiple compilation layers.

## 5. D8 — QBlue owns mechanized semantic/correctness preservation for a major quantum domain

Primary:

- Liyi Li et al., **A Verified Compiler for Quantum Simulation**, arXiv:`2509.18583` (2025/2026 artifact).

Mechanisms:

- high-level typed Hamiltonian language;
- multiple semantic layers;
- mechanized compiler correctness in Rocq;
- digital/analog backends;
- certified approximation/error reasoning.

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty for typed quantum semantics or formally verified compilation alone.

## 6. D9 — end-to-end runtime accounting + strong classical comparison is already an active methodology

Primary current paper:

- **Limits of quantum run-time advantage**, *Physical Review Applied* (2026), DOI shown by the publisher as `10.1103/gpsf-pn1x`.

Mechanisms/findings:

- conventional quantum runtime analysis can be biased if system overhead is excluded;
- readout, transpilation, thermalization and related overheads can be load-bearing;
- experimentally grounded end-to-end runtime definitions;
- methodology for selecting strong classical baselines;
- re-analysis of quantum-advantage claims under these definitions.

Additional current end-to-end benchmark:

- Pranav Chandarana et al., **The Quest for Quantum Advantage in Combinatorial Optimization: End-to-end Benchmarking of Quantum Solvers vs. Multi-core Classical Solvers**, arXiv:`2603.13607` (2026).

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty for including preprocessing, QPU execution and postprocessing in runtime, nor for requiring a strong classical comparator.

## 7. D10 — DARPA QB/QBI owns broad utility-over-cost + independent V&V framing

Official programme sources:

- DARPA **Quantum Benchmarking (QB)**;
- DARPA **Quantum Benchmarking Initiative (QBI)**.

Current QBI framing explicitly seeks rigorous verification/validation of whether a quantum computing approach can achieve utility-scale operation, with utility qualitatively defined as computational value exceeding costs. It also emphasizes third-party/government verification and validation rather than performer self-certification.

The earlier QB programme developed application benchmarks and hardware-specific resource estimates for end-to-end application instantiations.

Disposition: `ADOPT / NOVELTY STRIKE`.

ORION-QN may not claim novelty for the generic doctrine:

```text
quantum value must exceed total cost
+ independent validation is required
```

## 8. D11 — explicit access models/dequantization remain strong ownership threats

Relevant parent:

- Miguel Murça, Paul K. Faehrmann, Yasser Omar, **An access model for quantum encoded data**, arXiv:`2412.01889`.

The paper develops a compositional approximate sample/query access model and connects it to block-encoded states, classical simulation/Pauli sampling and dequantization-style reasoning.

Disposition: `ADOPT / ACCESS-MODEL THREAT`.

For future P3/P9-style data problems, ORION-QN cannot treat access-contract analysis or a classical sample/query comparator as new by itself.

## 9. Ownership matrix after subtraction

| Candidate ORION-QN idea | Strong owner / threat | Disposition |
|---|---|---|
| choose quantum vs classical algorithm from performance/resource predictions | Predict and Conquer; algorithm-selection literature | donor-owned |
| optimize full quantum hardware/software resource stack | AutoQuREO; QRE ecosystem | donor-owned |
| hybrid quantum/classical compilation across QEC/ISA | qstack | donor-owned |
| typed/formally verified quantum compilation | QBlue, SQIR/VOQC/QWIRE family | donor-owned |
| end-to-end runtime rather than gate/query proxy | current runtime-advantage methodology | donor-owned |
| strong classical first refusal | benchmarking literature, Brehm/Weggemans, runtime-advantage work | donor-owned |
| utility must exceed cost | DARPA QB/QBI and wider systems methodology | donor-owned |
| independent V&V | DARPA QBI and scientific assurance practice | donor-owned |
| explicit data/access/dequantization model | dequantization/access-model literature | donor-owned |
| quantum circuit generation / synthesis | prior ORION-Q donor set | donor-owned |

## 10. Residual that still appears distinct enough to test

After subtraction, the residual is no longer a generic scheduler, resource estimator, compiler, benchmark or verifier.

The remaining candidate object is a **scientific-admissibility dependency/receipt graph** spanning coordinates that existing quantum software systems usually own separately:

```text
original scientific object / claim
    -> admitted information + access derivation
    -> theorem applicability witness
    -> quantum representation / compilation correspondence
    -> backend + resource receipt
    -> measurement / uncertainty evidence
    -> strongest-classical counterfactual
    -> scoped negative-history applicability / reopen conditions
    -> independent verification state
    -> CLASSICAL scientific authority coordinates
```

The candidate contribution, if any, would be the **non-laundering composition law** across these coordinates for an autonomous scientific-research system:

- compiler correctness cannot imply quantum usefulness;
- query advantage cannot imply system advantage;
- system advantage cannot imply scientific validity/novelty/adoption;
- old negative evidence cannot be applied after a material access/backend/representation change without a scope witness;
- a quantum route can be mathematically eligible yet scientifically rejected in favor of a stronger classical route;
- `CANNOT_CHECK` remains a first-class route when any load-bearing dependency is unresolved.

This is only a candidate residual. It is very close to internal ORION #694 (`QuantumObligationBundle` / transport), existing assurance-case/provenance methods, and general proof-carrying systems. It therefore needs another changed-vocabulary search before any paper-level novelty statement.

## 11. Strongest immediate falsifier

Construct a mixed workload where independent dimensions disagree:

1. quantum theorem applicable + compiler verified + strong classical dominates;
2. quantum theorem applicable + query advantage + oracle derivation unresolved;
3. compiler/resource stack valid + scientific output measurement insufficient;
4. projected resource advantage + stale backend identity;
5. positive execution + prior scoped negative invalidated by a genuine representation change;
6. technically valid quantum result attempts to self-authorize P8 validity/novelty/adoption.

Compare:

- performance-model algorithm selector;
- full-stack resource optimizer;
- verified compiler;
- end-to-end benchmark rule;
- flat conjunction of all checks;
- ORION-QN typed dependency/authority graph.

ORION-QN has an incremental mechanism only if its typed dependency/history/authority composition rejects or reopens cases that the strongest faithful donor composition cannot express or adjudicate under the same information.

## 12. Current research terminal

`ROUTING_QRE_VERIFIED_COMPILATION_AND_UTILITY_VV_DONOR_OWNED__SCIENTIFIC_ADMISSIBILITY_COMPOSITION_RESIDUAL_OPEN`

No novelty authority is issued. Next search must target assurance cases, proof-carrying systems, scientific workflow provenance, dependency-aware invalidation and safety-case composition outside quantum computing as well as inside it.
