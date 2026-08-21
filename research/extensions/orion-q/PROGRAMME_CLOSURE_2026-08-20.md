# ORION-Q programme closure — 2026-08-20

**Status:** PROGRAMME COMPLETE  
**Parent:** #633  
**Closure record:** #671  
**Overall terminal:** `ORION_Q_PROGRAMME_COMPLETE__BOUNDED_STRUCTURAL_INTERFACE_VALUE_SUPPORTED__GENERATIVE_QUANTUM_METHOD_NOT_SUPPORTED`

## 1. Closure statement

ORION-Q is scientifically closed at the strongest level supported by the evidence produced in this programme.

The programme **does support bounded structural/interface value in controlled quantum worlds**. It **does not support a generative P10 quantum-method advantage**, a new quantum algorithm, a new complexity bound, or a protected real-domain Pareto improvement.

The strongest final interpretation is:

> Typed, task-sufficient quantum structure, scoped failure state, and explicit access/interface accounting are useful decision substrates. However, once strong classical/donor search and exact interface accounting receive the same information, the programme did not demonstrate that ORION's generative method-space layer creates quantum algorithmic reach beyond those baselines.

This is a completed scientific terminal, not an unfinished programme.

## 2. Evidence authority and chronology

The final deterministic closure experiment uses seed `20260820` and is stored beside this packet.

It was run **for closure after the broader programme had already explored and refined multiple hypotheses**. Therefore it is a **closure diagnostic**, not a prospectively preregistered confirmatory experiment. Its positive results are deliberately bounded to controlled synthetic evidence.

Earlier implementation PRs #640, #644, #647, #657 and #661 were closed without merge. Their own protocols required repository CI before `GREEN`; their workflow runs never reached a concluded success state before administrative closure. They are therefore **not** treated as merged/runtime ORION evidence. The closure diagnostic independently re-executes the key mathematical comparisons needed for programme disposition.

## 3. Donor saturation disposition

Repeated hostile literature/search rounds contracted broad ORION-Q novelty claims.

Mandatory absorbed parents include:

- **QSynth**, POPL 2024, DOI `10.1145/3632901`: recursive/inductive parametric quantum-program synthesis with logical/SMT verification.
- **Automated Quantum Algorithm Synthesis** / Rouillard et al., 2025–2026: DSL/evolutionary scalable quantum algorithm synthesis.
- **AlphaTensor-Quantum**, 2025: representation-specific RL/tensor-decomposition optimization and reusable arithmetic/gadget structure.
- RL/ZX and learned-gadget quantum circuit optimization: supplied rewrite/action-language search and reusable macro discovery.
- **Predict and Conquer**, arXiv:`2507.06758`: algorithm/parameter selection from supplied portfolios under non-functional constraints.
- **AutoQuREO**, arXiv:`2608.12936`: flexible full-stack quantum resource estimation and multi-objective optimization over supplied stack components.
- automated oracle synthesis, including arXiv:`2304.03829`;
- automated block-encoding construction and certified block-encoding/state-preparation tooling;
- standard, block-encoding-free and randomized QSP/QSVT, including arXiv:`2504.02385` and arXiv:`2510.06851`;
- interaction-picture, hybrid and partially randomized Hamiltonian simulation;
- finite quantum-query SDP/adversary/span-program synthesis;
- formal quantum program/circuit verification and 2026 Lean quantum formalization work;
- end-to-end access-cost accounting, including arXiv:`2310.03011`.

### Claims struck as donor-owned

ORION-Q does **not** claim novelty for:

- quantum circuit/program search;
- parametric quantum-program synthesis;
- reusable gate/gadget/library learning;
- algorithm portfolio selection;
- oracle synthesis;
- block-encoding construction;
- QSVT phase synthesis;
- deterministic/randomized Hamiltonian partitioning;
- interaction-picture hybridization;
- full-stack QRE/parameter optimization;
- formal quantum verification.

### Surviving research-space discriminator

The programme froze the larger residual in #659:

`problem semantics -> representation -> admissible access/oracle interface -> algorithm family -> coherent/deterministic/stochastic decomposition -> implementation/resource model -> proof/certificate`

with the load-bearing rule:

`NO_STRONGER_ORACLE`

Every interface used by a candidate must be supplied by the original problem contract or constructible from it under explicit cost/error.

No protected generative advantage for this full object was established before closure.

## 4. Final deterministic closure experiment

Script: `closure_experiment.py`  
Result: `CLOSURE_RESULTS.json`  
Seed: `20260820`

### QC0 — typed structure across held-out carriers

Three exact quantum classification tasks were represented through different carrier-native serializations.

| Task | Train carriers | Held-out carrier | Raw held-out accuracy | Typed invariant accuracy |
|---|---|---|---:|---:|
| complex relative phase | amplitude, density | Bloch | 0.348 | 1.000 |
| stabilizer / non-stabilizer | amplitude, density | Bloch | 0.494 | 1.000 |
| product / entangled | amplitude, coefficient matrix | reduced density | 0.500 | 1.000 |

Each task used `4000` training and `2000` held-out examples.

Typed coordinates were exact task-sufficient invariants:

- global-phase-safe relative-complex-phase witness;
- Bloch distance to the six one-qubit stabilizer axes;
- absolute two-qubit coefficient determinant / Schmidt-rank witness.

**Terminal:** `QC0_TYPED_STRUCTURE_SUPPORTED__CLOSURE_DIAGNOSTIC_ONLY`.

Interpretation: a controlled data-independence/information result, not a real quantum-algorithm improvement.

### QC1 — semantic known-operator recovery

Across `3000` mixed trials:

- random one-shot candidate success: `0.2933`;
- cheapest identity heuristic: `0.0000`;
- exact semantic invariant-break verifier recovery: `1.0000`.

**Terminal:** `QC1_RECOVERY_SUPPORTED__MECHANISM_VALIDATION_ONLY`.

This validates the evaluator idea only. Exact operator verification is donor-owned and does not establish P10 invention.

### QC2 — frozen-grammar method invention

For all three exact families, exhaustive search over the frozen candidate grammar succeeds whenever the obstruction-guided method succeeds:

- entanglement grammar: `15` candidates;
- complex-phase grammar: `10` candidates;
- Clifford/magic grammar: `10` candidates.

There is no incremental reach over exhaustive frozen-grammar search.

**Terminal:** `QC2_NO_INCREMENTAL_VALUE`.

This is the decisive negative for the strongest closed-world generative-method claim.

### QC2D — scoped negative history

`10000` controlled repair decisions tested an old failure that should remain binding only when the representation is unchanged.

Mean decision costs:

- raw permanent-pruning failure memory: `13.9993`;
- no history / always recheck: `9.4949`;
- scoped failure history with reopen-on-change: `8.9975`;
- clairvoyant ceiling: `8.4927`.

Scoped history saves `5.0019` vs raw failure memory and `0.4975` vs no history.

Reopen prediction:

- raw failure flag only: `0.499`;
- scoped failure + representation-change coordinate: `1.000`.

**Terminal:** `QC2D_FAILURE_STATE_INCREMENTAL_VALUE__CONTROLLED_SYNTHETIC`.

The positive is an explicit-information decision result, not a new quantum-control theorem.

### NML-I0 — access-contract / stronger-oracle laundering

Seven exact interface-stack worlds include free block-encoding assumptions, QRAM laundering, controlled-evolution laundering, representation unlock, amortized interface construction and false representation edits.

Exact-optimum selector accuracy:

- algorithm-only selector: `0.4286`;
- cheapest-interface heuristic: `0.4286`;
- exhaustive end-to-end interface accounting: `1.0000`.

**Joint terminal:**

- `I0_LAUNDERING_DETECTOR_GREEN`;
- `I0_FULLY_KNOWN_ACCESS_GRAPH_CLASSICALLY_CLOSED`.

This is central to the final result: explicit interface accounting matters, but when the derivation graph is completely known, classical search closes the problem. A P9/P10 learner has no justified role there.

### QC4 — standard vs randomized QSVT proxy

The stripped donor asymptotic proxies are:

- standard block-encoded QSVT: `L * lambda * d`;
- randomized QSVT: `(lambda*d)^2`.

Across `140` parameter points, direct comparison and the closed-form crossover disagree `0` times.

`randomized < standard  iff  L > lambda*d`.

**Terminal:** `QC4A_TWO_ROUTE_ANALYTICALLY_CLOSED`.

Caveat: this is only the stripped asymptotic proxy; constants, polylogarithmic factors and access conversion remain unresolved. Therefore the broader real multi-route Pareto claim is `CANNOT_CHECK`, not a positive.

## 5. Final stage terminal matrix

| Stage | Final terminal | Disposition |
|---|---|---|
| S0 | `S0_DONOR_MAP_FROZEN` | major donor territory absorbed; full-conjunction interface-synthesis residual not found as an obvious single parent |
| S1 | `S1_INTERFACE_SYNTHESIS_DISCRIMINATOR_FROZEN` | #659 object + `NO_STRONGER_ORACLE` |
| QC0 | `QC0_TYPED_STRUCTURE_SUPPORTED__CLOSURE_DIAGNOSTIC_ONLY` | bounded positive |
| QC0A | `QC0A_RULES_SPECIALISTS_SUFFICIENT_IN_EXACT_REGIME` | exact specialist outputs/rules leave no learned-controller claim in current exact regime |
| QC1 | `QC1_RECOVERY_SUPPORTED__MECHANISM_VALIDATION_ONLY` | bounded positive |
| QC2 | `QC2_NO_INCREMENTAL_VALUE` | exhaustive grammar search closes |
| QC2D | `QC2D_FAILURE_STATE_INCREMENTAL_VALUE__CONTROLLED_SYNTHETIC` | bounded positive |
| QC3 | `QC3_DONOR_COLLAPSED_NO_DISTINCT_ORION_RESIDUAL` | QSynth + scalable DSL/evolutionary synthesis already own the broad parametric-synthesis claim |
| QC4 | `QC4A_TWO_ROUTE_ANALYTICALLY_CLOSED__REAL_MULTI_ROUTE_CANNOT_CHECK` | simple selector unnecessary; no real Pareto claim |
| QC5 | `QC5_NOT_AUTHORIZED_BY_PRIOR_GATES` | no prospective frontier campaign claim |
| NML-I0 | `I0_LAUNDERING_DETECTOR_GREEN__FULLY_KNOWN_ACCESS_GRAPH_CLASSICALLY_CLOSED` | evaluation discipline positive; learning claim negative |
| NML-I1 | `NML_DONOR_COMPOSITION_SUFFICIENT_FOR_FULLY_KNOWN_STACKS` | supplied components + exact search sufficient |
| NML-I2 | `NML_I2_CANNOT_CHECK_GENERATIVE_INTERFACE_ADVANTAGE` | no protected fair generative test establishes an advantage |
| NML-I3 | `NML_I3_KNOWN_ROUTE_ONLY_NO_NEW_ROUTE` | known QSVT/access routes only |
| NML-I4 | `NML_I4_NOT_AUTHORIZED_BY_PRIOR_GATES` | no prospective new-method campaign |

## 6. Strongest allowed claim

The programme may state:

> In controlled quantum worlds, task-sufficient typed invariant state and scoped failure provenance can provide representation-robust decision information, while explicit end-to-end access-contract accounting prevents stronger-oracle/resource laundering. In the same programme, exhaustive/classical donor-complete methods close the tested frozen method grammars and fully known interface graphs, so no generative ORION quantum-method advantage is supported.

## 7. Claims explicitly not earned

The programme may **not** state:

- ORION discovered a new quantum algorithm;
- ORION discovered a new reusable quantum primitive;
- ORION improved a real QSVT/Hamiltonian algorithm Pareto frontier;
- ORION established a new query/complexity bound;
- P10 generative quantum method-space expansion beat exhaustive/program/evolutionary search;
- closed draft PRs are merged or CI-green;
- the closure diagnostic is a prospectively preregistered confirmation.

## 8. Negative history retained

The following negative results are load-bearing:

1. reusable quantum gate/library growth is already donor territory;
2. recursive/parametric quantum program synthesis is already donor territory;
3. generic invariant/controllability repair is heavily covered by Lie/control theory;
4. two-route QSVT selection is analytically closed in the stripped proxy;
5. frozen candidate-grammar invention shows no incremental value over exhaustive search;
6. fully known interface-stack selection is classically closed;
7. real generative interface invention remains `CANNOT_CHECK`;
8. no new real quantum algorithm/method was independently established.

These negatives are the reason the final claim is smaller and more defensible than the opening aspiration.

## 9. Programme closure

There is no remaining result-bearing ORION-Q stage in this programme.

Any future attempt at a real new quantum method must open a **new prospective programme** with a newly frozen target, donor set, model/code identity, resource/access contract, strong baselines and external novelty/correctness review. It cannot reuse this closure diagnostic as prospective evidence.

**Final terminal:**

`ORION_Q_PROGRAMME_COMPLETE__BOUNDED_STRUCTURAL_INTERFACE_VALUE_SUPPORTED__GENERATIVE_QUANTUM_METHOD_NOT_SUPPORTED`
