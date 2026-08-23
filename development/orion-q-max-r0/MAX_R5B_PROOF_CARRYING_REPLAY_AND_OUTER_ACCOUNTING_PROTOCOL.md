# ORION-Q MAX-R5B proof-carrying replay and outer-composition accounting protocol

Date: 2026-08-20
Parent: #633
MAX: #679
Real-method lane: #698
Branch: `shadow/orion-q-max-r0`
Status: **FROZEN BEFORE THE PROOF-CARRYING REPLAY / CONTROLLED-OUTER ACCOUNTING RESULT IS RUN**

## Why R5 is reopened

The first fresh N2 run (workflow `32377688518`) produced a large prospective internal-resource result, but hostile review found that the v1 harness emitted only exact DP minimum values and hashes. It did not emit and independently verify a canonical per-pair `(R0,R1,S,T0,T1)` witness, while its `joint_realizability` gate was set from construction intent rather than a witness replay.

Accordingly:

- the numerical v1 N2 result is retained as evidence;
- the v1 terminal is **provisional/reopened**;
- no R5 authority is accepted until a proof-carrying replay reconstructs and verifies every selected TARE representation;
- outer controlled composition remains a separate mandatory gate.

This protocol does not change the frozen N2 grouping algorithm or its 1% normalization budget. It tests the already-frozen result more strongly rather than retuning it.

## Part A — proof-carrying exact representation replay

For every TARE pair selected by both the bounded incumbent and the frozen 1% successor, the replay must deterministically reconstruct a canonical exact witness.

### Canonical local alphabet

Per system qubit, enumerate `(r0,r1,s)` in lexicographic base-4 Pauli code order `I,X,Z,Y` after fixing a pair orientation. For each local triple compute the three symplectic contribution bits

1. `<r0,r1>`;
2. `<s,r0>`;
3. `<s,r1>`;

and the local internal cost contribution

`4*w(r0) + 2*w(r1) + 2*w(s) + w(p0*r0) + w(p1*r1)`.

The global target parity is `(1,0,1)`. The orientation-level constants `-4-2` are applied after accumulation.

### Deterministic witness rule

The 8-state min-plus DP must carry backpointers. Ties are broken lexicographically by:

1. total `G_internal_2q`;
2. orientation `(input0,input1)` before the swapped orientation;
3. per-qubit sequence of `(r0,r1,s)` codes.

No post-outcome tie-breaking using controlled cost or any other secondary resource is allowed in this replay.

### Witness obligations

For every reconstructed TARE pair, verify from the emitted Pauli masks rather than from DP state alone:

- `R0` anticommutes with `R1`;
- `S` commutes with `R0`;
- `S` anticommutes with `R1`;
- `T0*R0=P0` and `T1*R1=P1` up to Pauli phase;
- recomputed `G_internal_2q` equals the stored pair cost;
- the pair normalization equals `sqrt(2)*hypot(|a0|,|a1|)`;
- coefficient sign/phase bits are retained in the witness receipt.

For every direct anticommuting block verify:

- the target pair anticommutes;
- normalization equals `hypot(|a0|,|a1|)` with no `sqrt(2)` factor;
- direct ordered `U_anti` cost is recomputed from target Pauli weights;
- coefficient sign/phase bits are retained.

The replay must emit a canonical SHA-256 over every pair witness for the incumbent and successor. A strict wrapper must fail closed on any mismatch.

## Part B — independent replay requirement

A second implementation must independently recompute the pair witnesses and aggregate receipt without importing the v1 pair-cost routines. It may reuse only the already-verified immutable DUCC parsing/Jordan-Wigner semantic layer.

The implementations must agree exactly on:

- sorted nonidentity Pauli list hash;
- incumbent pair list hash;
- 1% successor pair list hash;
- aggregate `Lambda_joint`;
- aggregate `G_internal_2q`;
- direct/TARE block counts;
- canonical witness hashes;
- pass/fail of the original frozen gates.

Floating normalizations are compared to `1e-12` absolute tolerance; all discrete quantities and hashes must match exactly.

## Part C — outer-LCU composition accounting for the already-frozen matchings

No new rematching or representation optimization is permitted in Part C. It wraps the canonical Part-A witnesses exactly as selected by the original internal objective.

TARE v4 explicitly states that operators larger than `2n+1` may be split into TARE groups and recombined via an outer LCU, but leaves that composition unexplored. For m=2 the TARE unitary contains the ancilla Hadamard/tag sequence, three `U_anti` Pauli rotations, Restore, and `W^dagger=H` for binary labels. The outer LCU therefore must control the entire heterogeneous block unitary rather than silently reusing uncontrolled internal counts.

### Canonical one-hot selector model

Use an outer address register of `ceil(log2 B)` qubits and a coherent unary-iteration / one-hot selector flag `f` for `B` blocks. Report selector routing overhead separately because it is common when `B` is matched.

Outer Prepare uses the exact per-block normalization vector and fixed synthesis precision. Incumbent and successor have the same `B`, so the dense reference rotation count is matched; the coefficient angles differ and their hashes must be reported.

### Controlled DIRECT block primitive vector

For a direct anticommuting pair, control the frozen ordered three-Pauli-rotation `U_anti` on selector flag `f`.

Report, without scalar laundering:

- system parity-ladder CNOT count;
- controlled coefficient-rotation count (`3`);
- controlled-Pauli support count outside the rotations (`0`);
- controlled-H count (`0`);
- coherent two-control AND compute/uncompute pairs (`0`).

### Controlled TARE m=2 primitive vector

For a TARE pair use its **canonical internal-G witness**, with no controlled-cost retuning.

Report:

1. `U_anti`: the original system parity-ladder CNOTs plus exactly three selector-controlled coefficient rotations;
2. three selector-controlled ancilla Hadamards for the m=2 circuit (`H` at tag preparation, the second tag Hadamard, and `W^dagger=H`);
3. Tag/Tag-dagger: use one coherent conjunction scratch `q=f AND l`, keep it through both Tag passes, then uncompute it. The controlled-Pauli support is `2*w(S)`;
4. Restore: use the exact identity
   `C_f[ |0><0| T0 + |1><1| T1 ]`
   as one selector-controlled base branch plus one conjunction-controlled correction. Choose the base branch solely by the frozen deterministic rule `min(w(T0),w(T1))`, tie to branch 0. Its controlled-Pauli support is
   `min(w(T0),w(T1)) + w(T0*T1)`.
   A second coherent conjunction compute/uncompute pair is required for the correction;
5. real coefficient signs are implemented as phases on the selector/conjunction controls and reported; they do not change Pauli support.

Thus the canonical non-scalar controlled-TARE vector is

- `parity_CNOT = 4(w(R0)-1)+2(w(R1)-1)`;
- `controlled_Rz = 3`;
- `controlled_H = 3`;
- `controlled_Pauli_support = 2w(S)+min(w(T0),w(T1))+w(T0*T1)`;
- `AND2_compute_uncompute_pairs = 2`;
- extra coherent scratch beyond the original local TARE ancilla = 1.

This vector is an exact circuit-structure receipt for the frozen factorization; no universal hardware equivalence between these primitive types is assumed.

### Fault-tolerant projections

In addition to the primitive vector, report at least two transparent projections, neither of which may replace the vector:

- **standard exact Clifford+T projection** using an explicitly cited controlled-H decomposition and an explicitly declared coherent Toffoli/AND decomposition;
- **native arbitrary-two-qubit projection** where each controlled-H / controlled Pauli is one two-qubit primitive and controlled arbitrary rotations remain a separate synthesized-rotation count.

All decomposition constants must be declared in the receipt. If a claimed advantage changes sign across reasonable projections, full outer superiority is **not** supported.

### QSVT/qubitization normalization weighting

Report per-query outer resource and the same resource multiplied by the normalization ratio. The 0.9839% N2 normalization increase must never be hidden by a scalar product. Primary comparison remains a vector:

- normalization `Lambda`;
- outer block count/address width;
- Prepare rotations;
- selector-routing overhead;
- controlled coefficient rotations;
- controlled-H / AND / controlled-Pauli support;
- projected T / CNOT counts;
- total logical ancillas/workspace.

## Part D — donor audit before R5 closure

The N2 v1 bounded incumbent is not the final donor-composed comparison. Before R5 closure, absorb and report at least:

1. Pauli LCU (`lambda=l1`) under the same Pauli list;
2. pure TARE adjacent theorem split;
3. direct anticommuting grouping / unitary partitioning, including groups larger than two using a published sorted-insertion-style heuristic and a deterministic coefficient-aware variant;
4. a stronger pair-only global normalization baseline if computationally practical (minimum-weight perfect matching with jointly realizable direct/TARE edge normalizations);
5. commuting-group/parallel-SELECT donor as a resource comparison, not as a false normalization improvement;
6. current fermionic/tensor block-encoding donors (DF/SCDF/MTD-like) with representation/access differences explicitly stated rather than compared under a secretly stronger oracle.

The donor audit is descriptive/Pareto unless a fresh protocol has been frozen for a new superiority threshold. Existing N2 data may be used for this post-confirmation audit but may not be used to invent a new protected gate and retroactively call it prospective.

## Closure gates

`MAX_R5_*` full closure requires all of:

- Part A canonical witness replay GREEN;
- Part B independent replay GREEN;
- original frozen N2 prospective gates still GREEN;
- outer controlled composition fully reported under the fixed wrapper;
- no hidden stronger oracle/access/precision assumption;
- donor audit completed with any stronger donor absorbed;
- applicability/failure boundary recorded.

If the fixed N2 successor loses its advantage after outer control, preserve the negative and open a fresh controlled-cost-aware successor protocol on a new protected public subject. Do not retune N2.

Even if R5 closes, R6 remains blocked pending hostile novelty authority and a claim stronger than self-certification.
