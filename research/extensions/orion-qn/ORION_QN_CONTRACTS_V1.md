# ORION-QN semantic, access and receipt contracts v1

Status: **FROZEN Q1 CONTRACT BEFORE RESULT-BEARING VS1 OUTCOMES**  
Parent: `ORION_QN_PROVENANCE_BOUNDARY_V1.md`  
Programme: `SzeChunYiu/ORION#734`  
Frozen base lineage: `d7312bc7fda4a84490acbc8b7964904fbedb3a93`

This document freezes the first ORION-QN contract surface. It defines what later implementations and experiments must record. It does not claim that any quantum kernel is faster, novel, hardware-ready or scientifically promoted.

## 1. Design rule

ORION-QN separates five objects that are often conflated:

```text
scientific problem
    -> admitted information/access
    -> executable algorithm/program
    -> observed measurement/output
    -> scientific authority
```

A successful circuit or simulator output can move evidence through this chain only by satisfying the intervening contracts. It cannot skip directly to authority.

## 2. State ontology

Every ORION-QN state coordinate is assigned exactly one state class.

### `CLASSICAL_AUTHORITATIVE`

Ordinary ORION state whose values may control programme governance, claim status, applicability, novelty status, adoption or search stop. P8-style authority coordinates remain here.

### `CLASSICAL_QUANTUM_METADATA`

Classical description of a quantum object: preparation recipe, circuit/IR hash, parameters, observable definition, backend identity, calibration identity, error target or resource estimate.

### `QUANTUM_LIVE`

A live quantum register/state available only inside an admitted execution environment. It is not serializable as an arbitrary amplitude list and is not copied into a receipt.

### `MEASUREMENT_DERIVED`

Classical data produced by a declared measurement/instrument and estimator. Its scientific meaning is bounded by that measurement contract.

### `UNRESOLVED_OR_INACCESSIBLE`

Information not licensed by the current access/measurement contract. A system must preserve this state rather than reading simulator internals or hidden evaluator state to force resolution.

## 3. `QProblemContract.v1`

```text
QProblemContract.v1
  problem_id
  owner_mechanic                # P1 ... P10 semantic owner, not paper id
  scientific_question
  target_output_type
  input_domain
  promise_conditions
  correctness_relation
  approximation_metric
  tolerance
  failure_semantics
  admitted_information
  prohibited_information
  reuse_count_or_workload_horizon
  authority_owner
  frozen_at
  subject_revision
```

Hard rules:

- `correctness_relation` must be independently checkable or explicitly `CANNOT_CHECK`;
- changing the tolerance or promise creates a new problem identity;
- simulator-only information such as the exact hidden statevector is prohibited unless the scientific task itself explicitly grants that information to every comparator.

## 4. `QSemanticStateView.v1`

```text
QSemanticStateView.v1
  problem_id
  classical_authoritative_fields
  classical_quantum_metadata_fields
  quantum_live_handles
  measurement_derived_fields
  unresolved_fields
  provenance_edges
  representation_identity
  transport_obligations
```

A state view may name a `quantum_live_handle`; it may not claim possession of an arbitrary unknown state snapshot.

No-cloning/linearity implication: a live handle may be consumed, borrowed or transformed only under the effect rules of the program IR. Ordinary classical copying applies only to classical metadata/results.

## 5. `QProgramIR.v1`

ORION-QN defines a semantic IR above backend formats. It may later lower to OpenQASM, QIR or other backends, but those formats do not define ORION scientific semantics.

Minimum semantic types/effects:

```text
Classical[T]
Qubit
QReg[n]
PreparedState[prep_contract_id]
Unitary[semantic_contract]
Isometry[semantic_contract]
Channel[semantic_contract]
Instrument[measurement_contract_id]
ClassicalControl
QuantumControl
AccessToken[access_contract_id]
UncomputeObligation
ResourceBudget
AuthorityToken             # CLASSICAL-ONLY; cannot be produced by quantum execution
```

### Physicality constraints

1. unknown `Qubit/QReg/PreparedState` values cannot be duplicated;
2. discarding a quantum value must be represented by a declared channel/reset/measurement or a valid uncomputation path;
3. temporary garbage that remains entangled with output is part of semantics and resource cost;
4. measurement is an explicit transition to classical result state;
5. classical feed-forward is allowed and expected;
6. `AuthorityToken` has no quantum constructor and cannot be measured out of a circuit;
7. lowering must preserve declared semantics or fail closed.

These choices are donor-informed by OpenQASM/QIR hybrid execution, Silq physicality/uncomputation and QWIRE/SQIR/VOQC formal semantics. ORION-QN’s candidate residual is the binding of these computation semantics to ORION scientific access/resource/authority obligations, not invention of quantum type systems or verified circuits themselves.

## 6. `QAccessContract.v1`

```text
QAccessContract.v1
  access_id
  original_problem_access
  classical_data_access
  quantum_native_access
  query_operations
  sampling_operations
  coherent_access_operations
  controlled_operation_availability
  state_preparation_access
  oracle_derivation
  preprocessing
  construction_cost
  per_use_cost
  amortization_count
  precision
  error_model
  invalid_stronger_interfaces
  comparator_equivalence_rule
```

### Mandatory adjudication

For every quantum kernel ask:

1. Is the quantum interface supplied natively by the problem?
2. If not, can it be constructed from the admitted classical/problem access?
3. What time/memory/data pass/error is required to construct it?
4. Does the classical comparator receive the analogous information or a justified weaker interface?
5. Is controlled access required although only uncontrolled access is supplied?
6. Is the interface reused enough to amortize construction?

If a quantum route depends on an unconstructed stronger interface, terminal = `CANNOT_CHECK_ACCESS_MODEL` or `INVALID`, never advantage.

## 7. `QStatePreparationContract.v1`

```text
QStatePreparationContract.v1
  preparation_id
  target_state_semantics
  source_information
  preparation_algorithm
  preparation_circuit_or_procedure
  logical_gate_cost
  classical_preprocessing_cost
  memory_cost
  precision
  infidelity_bound
  reuse_policy
  reset_or_reprepare_policy
  verification_method
  simulator_shortcuts_prohibited
```

The state preparation cost is zero only when the input problem natively supplies the required quantum state under the same problem definition. “Available as a NumPy array” is not “available as amplitude-encoded quantum state.”

## 8. `QOracleContract.v1`

```text
QOracleContract.v1
  oracle_id
  semantic_predicate_or_operation
  admitted_source_data
  reversible_embedding
  ancilla_requirements
  clean_or_dirty_ancilla_contract
  phase_or_bit_oracle_form
  controlled_form_required
  construction_algorithm
  construction_cost
  per_call_logical_resources
  inverse_cost
  error_bound
  reuse_policy
  classical_equivalent_operation
```

For Grover/amplitude-amplification style experiments, oracle-call complexity and oracle implementation cost must be reported separately.

## 9. `QMeasurementContract.v1`

```text
QMeasurementContract.v1
  measurement_id
  target_observable_or_event
  instrument_or_basis
  adaptive_rounds
  shots
  estimator
  estimator_bias
  confidence_or_error_guarantee
  multiple_testing_policy
  readout_error_model
  mitigation_identity
  reconstruction_algorithm
  classical_postprocess_cost
  stopping_rule
  identifiable_claims
  non_identifiable_claims
```

Rules:

- exact simulator state inspection is not a substitute for the frozen measurement contract;
- a classical shadow supports only the observables/functions covered by its assumptions and finite-sample guarantee;
- amplitude estimation is admissible only if its preparation/oracle/coherence requirements pass the access/resource gates;
- a result not identifiable from the declared measurements remains unresolved.

## 10. `QBackendIdentity.v1`

```text
QBackendIdentity.v1
  evidence_mode              # LOCAL_SIMULATION | RESOURCE_ESTIMATION | REAL_QPU
  provider_or_tool
  package_version
  backend_name
  simulator_method
  device_or_architecture_model
  compiler_transpiler_identity
  optimization_configuration
  noise_model_or_calibration_identity
  qec_model
  factory_model
  hardware_parameters
  timestamp
  environment_hash_or_manifest
```

Changing a load-bearing backend/compiler/noise/QEC coordinate reopens affected resource/correctness receipts rather than rewriting history.

## 11. `QResourceReceipt.v1`

No single scalar resource score is primary.

```text
QResourceReceipt.v1
  problem_id
  kernel_id
  backend_identity
  preprocess_time
  preprocess_memory
  state_prepare_time
  state_prepare_memory
  oracle_build_time
  oracle_build_memory
  oracle_calls
  inverse_oracle_calls
  logical_qubits
  logical_depth
  one_qubit_gates
  two_qubit_gates
  t_count
  t_depth
  ancilla_qubits
  logical_error_target
  qec_scheme
  factory_assumptions
  projected_physical_qubits
  projected_ft_runtime
  shots_or_repetitions
  measurement_time
  classical_reconstruction_time
  verifier_time
  total_wall_time_if_measured
  total_memory_if_measured
  total_failure_probability_bound
  unknown_coordinates
  source_of_each_coordinate
```

A derived scalar may be used for one explicit decision only after the full vector is retained.

## 12. `QVerificationReceipt.v1`

```text
QVerificationReceipt.v1
  problem_id
  kernel_id
  semantic_verifier
  compiler_or_lowering_verifier
  known_answer_tests
  hostile_tests
  measurement_statistical_check
  access_contract_check
  preparation_contract_check
  resource_accounting_check
  backend_identity_check
  independent_reconstruction_status
  unresolved_obligations
  final_verification_state     # VERIFIED | BOUNDED_VERIFIED | INVALIDATED | CANNOT_CHECK
```

The executor’s own success flag is never sufficient verification.

Formal verification, cryptographic verification and statistical verification are distinct evidence routes. Mahadev-style classical verification is optional and threat-model specific; it is not silently assumed for ordinary simulator work.

## 13. `QKernel.v1`

```text
QKernel.v1
  kernel_id
  owner_mechanic
  problem_contract_id
  classical_semantics
  quantum_semantics
  eligibility_predicate
  access_contract_id
  preparation_contract_id
  oracle_contract_id
  program_ir_id
  measurement_contract_id
  backend_eligibility
  error_contract
  resource_model
  verification_contract
  strongest_classical_baseline
  strongest_dequantized_baseline
  fallback_contract_id
  claim_ceiling
```

A kernel is executable only when every referenced contract exists and no non-compensatory gate is unresolved.

## 14. `QFallbackContract.v1`

```text
QFallbackContract.v1
  fallback_id
  trigger
  classical_or_hybrid_route
  semantic_equivalence_relation
  expected_resource_change
  evidence_status_preservation
  prohibited_failure_reinterpretations
```

A missing QPU or oversized simulation must not create a scientific negative. Correct outcomes include fallback execution or `CANNOT_CHECK_HARDWARE`.

## 15. `QuantumReceipt.v1`

This is the composite proof-carrying execution record.

```text
QuantumReceipt.v1
  receipt_id
  problem_contract
  semantic_state_view_before
  kernel
  access_contract
  preparation_contract
  oracle_contract
  program_ir_identity
  lowering_and_compiler_identity
  backend_identity
  measurement_contract
  raw_result_digests
  estimator_result
  uncertainty
  resource_receipt
  verification_receipt
  semantic_state_view_after
  claim_ceiling
  provenance_chain
  artifact_hash
```

A receipt records preparation/circuit/measurement identity and evidence. It does **not** serialize arbitrary unknown quantum amplitudes.

## 16. `QAdvantageReceipt.v1`

An advantage claim needs a separate adjudication object.

```text
QAdvantageReceipt.v1
  problem_id
  quantum_kernel_id
  classical_baseline_id
  dequantized_baseline_id
  same_information_check
  same_problem_check
  same_tolerance_check
  access_model_comparison
  preprocessing_comparison
  preparation_comparison
  oracle_construction_comparison
  query_complexity_comparison
  logical_resource_comparison
  projected_physical_resource_comparison
  measurement_readout_comparison
  verification_cost_comparison
  amortization_horizon
  evidence_mode
  observed_or_projected_regime
  unresolved_costs
  terminal
```

Allowed terminals include:

```text
CLASSICAL_PARENT_SUFFICIENT
DEQUANTIZED_PARENT_SUFFICIENT
QUANTUM_FEASIBLE_NO_ADVANTAGE
QUANTUM_QUERY_ADVANTAGE_ONLY
QUANTUM_PROJECTED_FT_ADVANTAGE
QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED
CANNOT_CHECK_ACCESS_MODEL
CANNOT_CHECK_HARDWARE
INVALID_COMPARISON
```

Only `REAL_QPU` evidence with matched end-to-end accounting can directly support a physical observed speedup claim. `RESOURCE_ESTIMATION` can support a projected FT regime. `LOCAL_SIMULATION` can support correctness/query-structure claims but not physical speedup.

## 17. End-to-end cost identity

Every result-bearing comparison retains:

```text
C_Q = C_preprocess
    + C_state_prepare
    + C_oracle_build
    + C_compile
    + C_logical_execute
    + C_QEC_physical
    + C_measure
    + C_reconstruct
    + C_verify

C_C = C_classical_preprocess
    + C_classical_index_or_model_build
    + C_classical_execute
    + C_classical_postprocess
    + C_classical_verify
```

The exact terms may be vectors rather than scalars. Amortized and one-shot costs must be reported separately.

## 18. First lowering policy

The semantic IR is backend-neutral.

Initial backend donor targets:

- OpenQASM 3.x for circuit/control interchange where expressible;
- QIR for LLVM-based hybrid representation/interoperability;
- Qiskit objects/Aer as a **local simulation adapter**, not the semantic definition;
- Microsoft QRE as a **resource-estimation adapter**, not physical execution evidence.

A backend adapter can fail `UNSUPPORTED` without invalidating the semantic kernel if another valid lowering/fallback exists.

## 19. Hostile conformance cases frozen before implementation

Every Q1 implementation must reject or correctly classify at least these cases:

1. amplitude-encoded input treated as free although only a classical array is supplied;
2. controlled oracle assumed when only ordinary oracle access is supplied;
3. simulator statevector inspection used to answer a measurement-limited task;
4. exact simulator runtime reported as quantum speedup;
5. logical gate count reported as physical runtime;
6. noisy simulator result reported as real-QPU evidence;
7. quantum route changes tolerance/error norm to win;
8. classical comparator denied preprocessing/reuse available to the quantum route;
9. oracle build cost omitted while per-call query count is highlighted;
10. measurement shots/readout cost omitted;
11. failed quantum backend availability recorded as scientific task failure;
12. quantum executor attempts to grant novelty/adoption/authority;
13. backend/compiler version changes but stale resource receipt remains silently authoritative;
14. uncomputed garbage remains entangled and changes output distribution;
15. unknown quantum state is copied into two independent live handles without a valid preparation/recomputation path.

Known-answer/no-alarm controls must also demonstrate that a fully specified, admissible small kernel can execute and verify without blanket refusal.

## 20. Q1 completion boundary

This contract freeze permits implementation of the first local simulator adapter and VS1 only after the VS1 problem families, splits, baselines, budgets and claim ceilings are frozen.

It does not authorize:

- new algorithm claims;
- P1–P10 paper edits;
- physical speedup claims;
- QPU-required architecture;
- novelty claims for hybrid IRs, quantum type systems, formal circuit verification, circuit synthesis, Grover/amplitude amplification or quantum backtracking.
