# Q1 R20 — matched current-compiler resource protocol

Status: `PROTOCOL_FROZEN__CURRENT_BASELINE_AND_EXECUTION_REQUIRED`

## Benchmark subject

Freeze public Hamiltonian/Pauli workloads before compilation. The suite must include the existing QG-21 chemistry control and at least one independently maintained modern Hamiltonian library. Bind every source revision, transform, coefficient threshold, qubit ordering, symmetry reduction, and term-order rule. Duplicate or near-duplicate instances must be declared.

## Compilers and arms

Required arms:

1. the frozen donor construction;
2. the exact support-two/shared-Tag construction;
3. a current global binary-symplectic Pauli compiler;
4. a current Pauli-network or phase-polynomial compiler where semantically applicable;
5. ablations without shared-Tag and without the support theorem;
6. oracle best arm reported only as an unattainable upper comparator.

All arms receive the same input operator and target architecture. Compiler-specific preprocessing must be charged.

## Exact semantics

For every output, verify the represented unitary or registered first-order simulation object under the same coefficient, ordering, Trotter-step, and global-phase conventions. Reject any arm whose semantics or approximation budget differs. The shared-Tag/TARE-M2 theorem applies only to its frozen grammar; unsupported inputs must receive a typed not-applicable terminal.

## Resource models

Report separately:

- arbitrary-angle rotation count and depth;
- logical two-qubit Clifford count and depth;
- routed two-qubit count/depth on at least line, grid, and all-to-all connectivity;
- logical qubits and ancillas;
- T count, T depth, and synthesized rotation cost at fixed precision;
- fault-tolerant factories, spacetime volume, and logical failure budget under one declared model;
- compiler wall time, peak memory, timeout, and preprocessing cost.

No one resource is a proxy for all others.

## Frozen hypotheses

Primary hypothesis:

> Under matched semantics and a declared resource model, the support-two/shared-Tag construction materially improves at least one registered resource without materially worsening every co-primary resource.

The primary QG-21 result remains adverse unless the exact frozen primary arm improves. Sensitivity-only gains are reported as sensitivity results.

## Hostile controls

- an instance where the shared Tag gives no gain;
- an architecture where routing reverses an all-to-all advantage;
- a precision where rotation synthesis dominates Clifford savings;
- a compiler whose global symplectic optimization erases the local support advantage;
- a workload outside the frozen grammar;
- exact donor ties on all 90 primary QG-21 rows.

## Allowed terminals

- `Q1_PRODUCTION_RESOURCE_MAPPING_MATERIAL`;
- `Q1_LOGICAL_RESOURCE_GAIN_ONLY`;
- `Q1_ROUTING_REVERSES_GAIN`;
- `Q1_SYNTHESIS_REVERSES_GAIN`;
- `Q1_PRIMARY_DONOR_TIE`;
- `Q1_SEMANTIC_DISAGREEMENT`;
- `Q1_NOT_APPLICABLE_TO_INPUT_GRAMMAR`;
- `CANNOT_CHECK_CURRENT_BASELINE`;
- `CANNOT_CHECK_RESOURCE_BOUND`.

## Authority

The existing support theorem, nine-qubit core, and `O(n^9)` checker bound remain exact structural results. No physical, fault-tolerant, runtime, or production compiler advantage is established until this protocol executes and passes independent review.
