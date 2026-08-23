# ORION-QN Q0/Q1 development packet

Status: **FROZEN BEFORE FIRST ORION-QN CODE CHANGE**  
Programme: #734  
Research contracts:
- `research/extensions/orion-qn/ORION_QN_PROVENANCE_BOUNDARY_V1.md`
- `research/extensions/orion-qn/ORION_QN_CONTRACTS_V1.md`
- `research/extensions/orion-qn/VS1_P6_P2_P4_LOCAL_SIMULATION_PROTOCOL_V1.md`

## Development question

What is the smallest ORION code addition that makes the Q1 evidence/claim boundary mechanically testable without importing a quantum SDK into ORION core, changing P1–P10 authority semantics, or prematurely implementing a result-bearing Grover experiment?

## Atomic development questions

### D1 — evidence-mode representation
Can ORION represent `LOCAL_SIMULATION`, `RESOURCE_ESTIMATION`, and `REAL_QPU` as mutually explicit evidence modes rather than comments/prose?

### D2 — access-match representation
Can a result mechanically retain whether the quantum and classical comparators received the same admitted information/problem/tolerance and whether a stronger quantum interface remains unresolved?

### D3 — claim ceiling
Can the code reject authority laundering such as:
- local simulation -> projected FT advantage;
- local simulation -> end-to-end physical advantage;
- resource estimation -> observed end-to-end physical advantage?

### D4 — fail-closed unresolved costs
Can stronger advantage terminals fail closed when load-bearing access/resource coordinates are unresolved?

### D5 — negative/bounded terminals
Can the model preserve `CLASSICAL_PARENT_SUFFICIENT`, `DEQUANTIZED_PARENT_SUFFICIENT`, `QUANTUM_FEASIBLE_NO_ADVANTAGE`, `CANNOT_CHECK_*`, and `INVALID_COMPARISON` as first-class results rather than forcing a positive quantum label?

### D6 — package isolation
Can this be added under a new `orion.quantum` package with no import from ORION core into a vendor SDK and no new mandatory runtime dependency?

## Bounded saturation assessment

### Knowledge
Two Q0 literature rounds covered hybrid quantum IR/control, physicality/uncomputation, formal circuit verification, local simulation, FT resource estimation, search/backtracking donors, dequantization/access-model threats and automated quantum synthesis. No literature result requires a different first implementation atom: the immediate need is a local evidence/claim guard, not a new quantum language or circuit engine.

### Search universe
Searched across:
- quantum programming languages/IR;
- simulators;
- formal verification;
- quantum algorithms/complexity;
- resource estimation/QEC;
- dequantization/input access;
- automated synthesis.

Potential missing domains that could matter later but do not block this atom: measurement-based computation, analog/annealing semantics, continuous-variable systems, distributed/network quantum computing, specialized QEC compilers. Reopen when a kernel targets one of these execution models.

### Formulation
Competing formulations considered:

1. add Qiskit directly to core and let backend objects imply evidence class — rejected because backend availability is not scientific authority and this couples core to a vendor SDK;
2. represent evidence mode with plain strings in experiment scripts — rejected because fail-closed claim ceilings become non-local convention;
3. build the entire `QProgramIR` now — rejected as too large before the first receipt/claim boundary is mechanically exercised;
4. first add a small typed evidence/access/advantage contract layer — retained.

## Challenge to the saturation basis

The current literature could look falsely flat if we searched only for “quantum programming language” rather than scientific-workflow provenance. The nearest ORION-specific residual is therefore deliberately narrowed: **not** a new PL, but a machine-checkable mapping from execution evidence class + access parity + unresolved cost state to allowed scientific claim terminal.

This is provisional. If a current framework already provides the same end-to-end scientific-authority contract, ORION-QN should absorb it and shrink the contribution claim without removing the engineering need.

## Why searches might have missed relevant knowledge

1. the same idea may live under reproducibility/provenance terminology rather than quantum terminology;
2. resource-estimation systems may encode stronger authority boundaries outside their main papers;
3. quantum cloud workflow systems may already distinguish simulator/projected/hardware evidence in machine-readable schemas;
4. formal-method systems may bind access assumptions more strongly than abstract summaries reveal.

These are literature reopen triggers, not blockers for implementing the local fail-closed contract.

## Frozen implementation hypothesis H-Q1-LOCAL-GATE

> A small dependency-free `orion.quantum` contract module can make the simulator/resource-estimator/QPU evidence hierarchy, same-information gates and advantage claim ceilings mechanically enforceable before any quantum SDK adapter is added.

### Intended files

```text
src/orion/quantum/__init__.py
src/orion/quantum/contracts.py
tests/quantum/test_contracts.py
```

No existing P1–P10 file, core authority object or shared registry is modified in this tranche.

## Minimum types

Implement only the mechanically load-bearing subset:

```text
QuantumEvidenceMode
QuantumAdvantageTerminal
QAccessMatch
QResourceSummary
QAdvantageReceipt
QuantumContractError
validate_advantage_receipt(...)
```

The full Q1 research schemas remain the specification; this tranche is not allowed to pretend the subset is complete `QuantumReceipt.v1` support.

## Frozen validation laws

### L1 simulator ceiling
`LOCAL_SIMULATION` rejects:
- `QUANTUM_PROJECTED_FT_ADVANTAGE`
- `QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED`

It may retain `QUANTUM_QUERY_ADVANTAGE_ONLY` only when same problem/information/tolerance/access checks pass and the claim text is explicitly query-bounded.

### L2 resource-estimation ceiling
`RESOURCE_ESTIMATION` rejects observed `QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED`; it may support `QUANTUM_PROJECTED_FT_ADVANTAGE` when required coordinates are resolved and comparator/access gates pass.

### L3 real-QPU is necessary but not sufficient
`REAL_QPU` does not automatically grant end-to-end advantage. Same-problem, same-information, same-tolerance, access parity and required resource coordinates must also pass.

### L4 access fail-closed
An unresolved stronger quantum interface rejects every positive advantage terminal and permits `CANNOT_CHECK_ACCESS_MODEL`.

### L5 problem/tolerance mismatch
If same-problem or same-tolerance is false, the comparison is `INVALID_COMPARISON`; no positive terminal is admitted.

### L6 unresolved load-bearing resources
A terminal stronger than query-only cannot be admitted while required end-to-end resource coordinates are unresolved.

### L7 negatives are valid
Classical/dequantized/no-advantage/CANNOT_CHECK terminals remain representable and do not raise simply for being non-positive.

## Known-answer tests

1. admissible local-simulation query-only receipt passes;
2. admissible resource-estimation projected-FT receipt passes;
3. admissible real-QPU end-to-end receipt passes only with all comparison gates and resources resolved;
4. classical-parent-sufficient receipt passes without requiring quantum-positive evidence.

## Hostile tests

1. local simulator labeled physical end-to-end advantage -> reject;
2. local simulator labeled projected FT advantage -> reject;
3. QRE projection labeled observed physical end-to-end advantage -> reject;
4. stronger quantum access unresolved + query advantage -> reject;
5. same information false + positive advantage -> reject;
6. same tolerance false + positive advantage -> reject;
7. unresolved end-to-end cost + projected/physical advantage -> reject;
8. real QPU evidence with mismatched access -> reject;
9. `CANNOT_CHECK_ACCESS_MODEL` with unresolved access -> retain;
10. negative/classical terminal -> retain.

## Reopen triggers

Reopen this implementation hypothesis if:

- the subset cannot express a hostile case without adding hidden booleans;
- enforcing it requires modifying existing P8 authority semantics;
- current main changes the relevant authority/receipt API before integration;
- a stronger donor contract discovered during implementation subsumes the exact object;
- VS1 needs an execution fact that cannot be represented without implementing more of Q1.

## Non-claims

A green implementation proves only that ORION can enforce these local contract laws. It is not evidence of:

- quantum algorithm correctness;
- Grover speedup;
- real QPU value;
- novelty;
- ORION-QN publication readiness;
- P1–P10 quantum superiority.
