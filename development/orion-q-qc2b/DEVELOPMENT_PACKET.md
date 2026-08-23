# ORION-Q QC-2B — development packet

Tracking issue: #642
Parent: #633
Stack base: `shadow/orion-q-qc2a` / PR #640

## Development question

Can the QC-2 exact obstruction substrate host a third, materially different quantum invariant — Clifford preservation of stabilizer states — without weakening fail-closed contracts, leaking target/operator names, or conflating invariant compatibility with bounded reachability?

## Atomic fibres

1. Extend the frozen capability vocabulary with `CLIFFORD_ONLY`.
2. Implement a one-qubit pure-state stabilizer witness from the Bloch vector.
3. Require a stabilizer initial state for the Clifford-only contract.
4. Classify a non-stabilizer target as `EXPRESSIVITY_OBSTRUCTION` and a stabilizer target as `INVARIANT_COMPATIBLE` only.
5. Add a deterministic `CLIFFORD_MAGIC` hostile-pair family with weaker-view collisions and semantic separation.
6. Recompute the exact information lattice over all three hostile families.
7. Preserve evaluator identity/gold isolation and global-phase invariance.

## Incumbent knowledge / donor ownership

- Stabilizer formalism, Clifford preservation, and magic/non-stabilizer resources are established quantum-information theory. ORION owns none of those facts.
- Quantum synthesis already studies gate-set expressivity/reachability; this tranche cannot claim that distinction.
- The residual being tested is narrower: whether ORION can represent multiple independent exact obstruction witnesses through one fail-closed typed benchmark substrate before any learned edit policy is introduced.

## Saturation assessment for this implementation atom

Knowledge saturation is intentionally bounded to the exact one-qubit stabilizer fact required for the test; no research novelty is asserted. The benchmark-design saturation basis is QC-2A's exact invariant contract plus hostile leakage rules.

## Challenge to saturation basis

The design is invalid if:

- a non-stabilizer initial state is silently accepted;
- global phase changes stabilizer classification;
- the benchmark leaks `T`, `MAGIC`, `CLIFFORD_MAGIC`, family identity, case identity, or gold through model-visible views;
- the accepted compatible class is described as guaranteed bounded reachability;
- numerical tolerance makes ordinary axis stabilizer states unstable.

## Miss hypotheses

1. Bloch-coordinate computation may be written with the wrong sign convention for Y, yet membership could still appear superficially plausible.
2. Using only one named T state could create a target-template shortcut.
3. `CLIFFORD_ONLY` may be passed as a malformed runtime string unless the capability contract explicitly rejects it.
4. Extending the hostile-family enum may accidentally alter existing deterministic pair identities or information ceilings.

## Frozen implementation hypothesis

> If one-qubit stabilizer membership is implemented as Pauli-axis Bloch-vector membership, then a Clifford-only capability with a stabilizer initial state yields an exact invariant obstruction for non-stabilizer targets; adding deterministic reminted stabilizer/non-stabilizer hostile pairs should preserve the `SURFACE=1/2`, `CONTRACT=1/2`, `SEMANTIC=1` information-lattice pattern without changing QC-2A's semantics.

## Frozen hostile tests

- `|0>`, `|1>`, `|+>`, `|->`, `|+i>`, `|-i>` classify stabilizer;
- a T/magic-like state classifies non-stabilizer;
- global rephasing preserves the label;
- non-stabilizer initial state fails closed under `CLIFFORD_ONLY`;
- malformed capability fails closed;
- reminted case/state IDs do not change the model fingerprint;
- generated weaker views collide across opposite gold;
- generated semantic views separate;
- balanced three-family corpus has deterministic ceilings 1/2, 1/2, 1.

## Reopen triggers

Reopen rather than patch post hoc if the one-qubit witness is numerically unstable at the frozen tolerance, if semantic views need target labels to separate, or if the third family breaks the exact information-lattice construction.

## Authority

Engineering/evaluator substrate only. No new quantum algorithm, quantum-method invention, P9/P10 learning advantage, or novelty claim is authorized by this packet.