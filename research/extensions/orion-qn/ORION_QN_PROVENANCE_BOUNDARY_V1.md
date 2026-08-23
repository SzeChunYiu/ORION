# ORION-QN provenance and programme boundary v1

Status: **FROZEN Q0 RESEARCH CONTRACT — NO POSITIVE QUANTUM-ADVANTAGE CLAIM**  
Canonical programme issue: `SzeChunYiu/ORION#734`  
Repository: `SzeChunYiu/ORION` only  
Frozen ORION base: `d7312bc7fda4a84490acbc8b7964904fbedb3a93`  
Base event: merge PR #728, `harden ORION research harness`  
Literature cutoff for this packet: **2026-08-21**

## 1. Repository authority boundary

All ORION-QN research, branches, commits, protocols, experiments, implementations and paper artifacts belong in `SzeChunYiu/ORION`.

The earlier `SzeChunYiu/RAKL#752` planning issue is historical provenance only and was superseded by ORION #734. It is not an active programme location, implementation location or publication-authority surface.

No result may cite the existence, closure or wording of the old RAKL issue as scientific evidence.

## 2. Publication boundary

ORION-QN is a new framework/publication programme. It does **not** rewrite the existing P1–P10 papers and it does not create automatic `P1-Q ... P10-Q` paper successors.

Internal labels such as `P2-Q`, `P4-Q` and `P6-Q` mean only: “the ORION-QN semantic/execution mapping of the corresponding mechanic.”

Default publication path:

1. `QN0` flagship framework paper first;
2. `QN-I` semantics only if a distinct formal/PL result is earned;
3. `QN-II` proof-carrying quantum computation only if `QuantumReceipt`/obligation transport earns a distinct result;
4. `QN-III` end-to-end quantum advantage only if full same-information resource accounting supports a distinct result;
5. `QN-IV` self-optimizing hybrid research only if governed routing/self-improvement earns a distinct result.

A research track remains internal evidence when it does not clear its own publication discriminator.

## 3. Exact object being researched

The target is **full ORION quantum-native semantic coverage**, not all-QPU execution.

For every ORION mechanic `M`, the programme must determine:

```text
C(M) = classical semantics
Q(M) = quantum semantics, or proof/receipt that quantum execution is inapplicable
H(M) = allowed hybrid composition
E(M) = eligibility/access/resource/measurement/verification contract
F(M) = classical fallback preserving scientific semantics
```

A valid final mapping may be:

```text
CLASSICAL_REQUIRED
QUANTUM_SEMANTICS_DEFINED
QUANTUM_FEASIBLE_NO_ADVANTAGE
QUANTUM_QUERY_ADVANTAGE_ONLY
QUANTUM_PROJECTED_FT_ADVANTAGE
QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED
DEQUANTIZED_PARENT_SUFFICIENT
CLASSICAL_PARENT_SUFFICIENT
CANNOT_CHECK_HARDWARE
CANNOT_CHECK_ACCESS_MODEL
INVALID
```

Forcing every mechanic onto a QPU is explicitly outside the success criterion.

## 4. Local-computer-first evidence boundary

ORION-QN must be developable on an ordinary computer.

Three evidence modes are distinct:

### `LOCAL_SIMULATION`

A CPU/GPU simulates the mathematical quantum circuit/state/channel. This can establish implementation semantics, known-answer behavior, compiler equivalence, measurement-distribution behavior and hostile-test failures.

It **cannot** establish physical quantum speedup. The CPU is paying the simulation cost.

Current IBM Quantum guidance explicitly positions local simulators as tools for developing and testing programs before real hardware. Qiskit Aer supports exact/noisy simulation and multiple simulation methods, but noisy simulation remains a model and can underrepresent real-device effects.

Primary sources:
- https://quantum.cloud.ibm.com/docs/en/guides/local-simulators
- https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-aer
- https://quantum.cloud.ibm.com/docs/en/guides/local-testing-mode

### `RESOURCE_ESTIMATION`

A classical computer estimates logical/fault-tolerant physical resources without executing the large quantum workload.

The current Microsoft Quantum resource estimator explicitly models an application, hardware architecture, error correction/factory model and error budget, then reports physical-qubit/runtime trade-offs and Pareto-optimal configurations.

Primary sources:
- https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator
- https://learn.microsoft.com/en-us/azure/quantum/install-run-resource-estimator

This evidence may support `QUANTUM_PROJECTED_FT_ADVANTAGE` only when the compared classical route and all input/output costs are also accounted for. It is not real-QPU evidence.

### `REAL_QPU`

Actual remote or owned quantum hardware execution. This is optional for framework development and not required to complete semantic coverage. Hardware evidence needs its own backend/calibration/compiler/measurement identity and does not retroactively strengthen simulator results.

## 5. Prior ORION-Q lineage is immutable evidence

The following ORION issues are mandatory prior evidence/control inputs rather than authorizing parents:

- #633 — reopened negative-result recovery programme;
- #671 — prior closure snapshot;
- #674 — QC2/exhaustive-search negative recovery;
- #675 — QSVT route-selection negative recovery;
- #676 — parametric synthesis donor-collapse recovery;
- #677 — partially known interface-graph recovery;
- #679 — MAX quantum scientist programme;
- #694 — proof-carrying quantum obligation transport;
- #695 — protected self-evolving quantum skills;
- #698 — real quantum method/resource lane.

The prior closure packet must remain historically intact. Its terminal was:

`ORION_Q_PROGRAMME_COMPLETE__BOUNDED_STRUCTURAL_INTERFACE_VALUE_SUPPORTED__GENERATIVE_QUANTUM_METHOD_NOT_SUPPORTED`

Load-bearing inherited controls include:

1. a tiny frozen method grammar can make exhaustive search dominate obstruction-guided editing;
2. a fully known interface/derivation graph can be classically closed;
3. stripped low-dimensional route-selection proxies can be analytically closed;
4. generic quantum circuit/program/parametric synthesis has strong donor ownership;
5. a proxy resource gain can disappear when actual circuit implementation cost is charged;
6. no stronger oracle may be silently introduced;
7. state preparation, preprocessing and readout are not free;
8. a real quantum-method contribution requires a fresh prospective target, donor set, access/resource contract, strong baselines and independent review.

ORION-QN may absorb these lessons. It may not erase or relabel their negative outcomes.

## 6. Q0/Q1 expert cell and vetoes

These are role-separated same-context reviews, not independent peer review.

| Role | Scope | Veto |
|---|---|---|
| Q1 quantum algorithms/complexity | query/model assumptions, search/backtracking algorithms, strongest quantum/classical parent | speedup uses mismatched access or wrong asymptotic object |
| Q2 quantum PL/reversible systems | linearity, no-cloning, physical semantics, uncomputation, control/lowering | proposed semantic operator cannot correspond to an admissible quantum operation/instrument |
| Q3 verification/statistics | measurement, uncertainty, replay, independent reconstruction | scientific conclusion not identifiable from declared measurements or verifier is self-authorizing |
| Q4 FTQC/resources | logical/physical resources, QEC, factories, backend assumptions | advantage omits material QEC/prep/measurement/runtime cost |
| Q5 ORION architecture | P1–P10 responsibility and authority boundary | capability silently changes P4/P8/P5 authority semantics |
| Q6 hostile dequantization reviewer | stronger classical algorithms, access symmetry, hidden preprocessing/readout | fair classical/dequantized route closes the claimed residual |

Any unresolved veto lowers the claim ceiling or yields a typed `CANNOT_CHECK`/parent-sufficient terminal.

## 7. Literature saturation round 1 — architecture and execution

Round 1 searched current official/primary work across hybrid IRs, simulation, resource estimation and first quantum search kernels.

### Retained donor facts

**OpenQASM 3/3.1.** OpenQASM explicitly includes classical data/control, measurement and feed-forward around quantum operations. It is an execution-level language/IR, not evidence that a whole scientific controller should be coherent quantum state.

- https://openqasm.com/
- https://openqasm.com/versions/3.1/index.html

**QIR.** The QIR Alliance specifies an LLVM-based representation intended to connect multiple quantum languages to heterogeneous quantum processors. LLVM/QIR can represent rich classical control integrated with quantum calls.

- https://github.com/qir-alliance/qir-spec
- https://github.com/qir-alliance/qir-spec/blob/main/specification/README.md
- https://www.qir-alliance.org/alliance/

**Local simulation.** Qiskit Aer/local testing provides exact/noisy/general-purpose simulation for development; simulator results are not device results.

**Fault-tolerant resource estimation.** Microsoft QRE explicitly separates application traces, architecture, QEC/factory design and error budget and explores physical-qubit/runtime Pareto trade-offs.

**Amplitude amplification.** Brassard–Høyer–Mosca–Tapp generalize Grover-like search, reducing repeated-success probability dependence from `1/a` to order `1/sqrt(a)` applications under the algorithm’s access assumptions.

- https://arxiv.org/abs/quant-ph/0005055

**Quantum backtracking.** Montanaro gives a bounded-error quantum walk speedup for a classical backtracking tree of size `T`, with theorem-specific dependence on problem size and test access. This is a candidate S2 donor, not a generic “all structured search” theorem.

- https://arxiv.org/abs/1509.02374

### Round-1 effect on programme

No material architecture change. It strengthens the choice of:

`ORION semantic IR -> backend lowering (OpenQASM/QIR/etc.)`

rather than making OpenQASM or QIR itself the ORION semantic layer.

## 8. Literature saturation round 2 — hostile prior-art / physicality / dequantization

Round 2 deliberately searched for mechanisms that could absorb ORION-QN’s intended residual or invalidate apparent quantum value.

### Retained donor facts

**Silq.** Safe uncomputation and a physicality-aware type system demonstrate that temporary-value disposal and uncomputation are first-class language problems.

- https://doi.org/10.1145/3385412.3386007

**QWIRE.** QWIRE gives a circuit language embedded in a classical host language with sound physical semantics and formal reasoning in Coq. Therefore “hybrid host + typed quantum circuit” is donor-owned.

- https://doi.org/10.1145/3009837.3009894
- https://github.com/inQWIRE/QWIRE

**SQIR/VOQC.** Verified circuit IR and verified optimizer construction in Coq are donor-owned; ORION-QN must not claim novelty for circuit equivalence/verified optimization by itself.

- https://github.com/inQWIRE/SQIR
- https://doi.org/10.1145/3434318

**Classical verification of quantum computation.** Mahadev establishes an important cryptographic verification route under computational assumptions. It is a specialized option, not a mandatory verifier for every ORION-QN kernel.

- https://arxiv.org/abs/1804.01082

**Classical shadows.** Classical shadows support predicting many selected properties from measurement data under their theorem assumptions; they do not supply free full-state readout.

- https://arxiv.org/abs/2002.08953

**Dequantization.** Tang showed that a strong apparent recommendation-system speedup can collapse when a classical algorithm receives suitable sample/query access. Cotler–Huang–McClean further stress that access models themselves must be compared carefully: sample/query access can be stronger than quantum-state input in some learning tasks.

- https://arxiv.org/abs/1807.04271
- https://arxiv.org/abs/2112.00811

**Automated quantum algorithm synthesis.** Rouillard–Lourens–Petruccione show scalable DSL/evolutionary synthesis that rediscovers general quantum algorithms. Generic “generate a quantum algorithm/program family” therefore remains donor-owned.

- https://link.springer.com/article/10.1140/epjqt/s40507-026-00472-4

**2026 input-problem preprint.** `The Input Problem: A Permanent Bottleneck for Quantum Machine Learning` is recent preprint evidence arguing that classical-data state preparation can dominate apparent speedups. It is useful as a hostile checklist, not settled authority or a universal impossibility theorem.

- https://arxiv.org/abs/2608.08433

### Round-2 effect on programme

`NO_MATERIAL_CHANGE` to the architecture. The pass strengthens four mandatory gates:

1. linear/physical semantics and uncomputation in `QProgramIR`;
2. formal/statistical verification separated from scientific authority;
3. explicit access/state-preparation/readout accounting;
4. donor-complete circuit/program synthesis baseline before any P10 quantum-method claim.

Two consecutive literature rounds therefore leave the Q0/Q1 residual stable enough to freeze the first semantic-contract tranche. This is **not** a novelty certificate. New literature or a materially stronger donor reopens the affected atom.

## 9. Constitutional invariants frozen at Q0

The following are non-compensatory:

1. `NO_STRONGER_ORACLE`
2. `NO_FREE_STATE_PREPARATION`
3. `NO_FREE_READOUT`
4. `NO_AUTHORITY_LAUNDERING`
5. `NO_NEGATIVE_HISTORY_REWRITE`
6. `SAME_ADMITTED_INFORMATION`
7. `STRONGEST_FAIR_CLASSICAL_OR_DEQUANTIZED_BASELINE`
8. `NO_SIMULATOR_EQUALS_HARDWARE_CLAIM`
9. `NO_LOGICAL_EQUALS_PHYSICAL_CLAIM`
10. `RESOURCE_VECTOR_NOT_ONE_SCORE`
11. `BACKEND_OR_REVISION_DRIFT_REOPENS_RECEIPTS`
12. `CLASSICAL_FALLBACK_PRESERVES_SCIENCE`

A scientific win cannot compensate for violating one of these gates.

## 10. Q0 completion state

Q0 establishes only:

- repository and publication identity;
- frozen code/literature chronology;
- immutable prior negative/donor lineage;
- local-simulation/resource-estimation/hardware evidence classes;
- two literature rounds with no material architecture change;
- expert veto roles and constitutional invariants.

Q0 does **not** establish:

- novelty of ORION-QN;
- quantum speedup;
- end-to-end advantage;
- real hardware value;
- correctness of any future quantum kernel;
- publication readiness.

Next gate: Q1 semantic/access/measurement/resource/verification contracts, followed by a prospectively frozen VS1 before protected outcomes.
