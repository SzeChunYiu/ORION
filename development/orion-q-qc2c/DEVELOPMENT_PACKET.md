# ORION-Q QC-2C — semantic operator-edit witness development packet

Tracking issue: #645
Parent: #633
Stack base: `shadow/orion-q-qc2b` / PR #644

## Development question

Can ORION independently verify that a proposed unitary operator genuinely introduces the missing quantum capability diagnosed by QC-2, without relying on gate names, candidate-supplied output states, or a claim that the target problem is thereby solved?

## Atomic fibres

1. Define an opaque small `UnitaryOperator` with exact finite matrix payload and fail-closed unitarity checks.
2. Execute the operator on an evaluator-checked probe state.
3. Require the probe to satisfy the incumbent invariant.
4. Verify that the executed output violates that invariant.
5. Cover separability, real-up-to-phase, and one-qubit stabilizer invariants.
6. Preserve operator/case identity isolation in model-visible payloads.
7. Make the verdict invariant to global phase on the operator.

## Donor ownership / non-claim

Verifying unitary matrices and checking entanglement, realness, or stabilizer membership are standard quantum-information operations. This packet claims no novelty in those tests. The research purpose is to create a common semantic admission gate for future P10-generated method edits.

## Saturation assessment for this implementation atom

The implementation atom is narrow: arbitrary finite 2x2/4x4 unitary candidates plus a witness state. A more general symbolic/circuit operator representation is deferred until this interface survives hostile tests.

## Challenge to saturation basis

The design fails if:

- the generator can provide its own post-operator output as evidence;
- a non-unitary matrix is accepted;
- operator identity/name affects the semantic verdict;
- a probe outside the incumbent invariant is accepted;
- an operator receives credit only because it directly encodes the final benchmark target;
- global operator phase changes the invariant-break verdict;
- `INVARIANT_BREAK_VERIFIED` is later laundered into target solve, bounded reachability, minimality, or novelty.

## Miss hypotheses

1. Matrix application or conjugation may be implemented incorrectly.
2. Unitarity tolerance may accept materially invalid matrices or reject valid phase-scaled matrices.
3. CNOT on `|00>` is a false negative for entangling capability unless the witness probe is chosen correctly; therefore the witness state is part of the candidate certificate.
4. A non-Clifford operator can fail to create magic on a particular stabilizer probe; the certificate is existential and must prove the supplied probe works, not classify the operator globally.

## Frozen implementation hypothesis

> If a candidate unitary and incumbent-valid probe are executed by the evaluator, then a transition from invariant-satisfying probe to invariant-violating output is a machine-checkable witness that the candidate operator breaks that specific incumbent invariant. The witness is strictly weaker than solving the motivating target or proving a globally minimal language edit.

## Frozen positive controls

- two-qubit controlled-NOT with `|+0>` probe breaks product-state preservation;
- one-qubit phase-S with `|+>` probe breaks real-up-to-global-phase preservation;
- one-qubit T-like phase with `|+>` probe breaks stabilizer preservation.

## Frozen negative controls

- local `X tensor I` does not break product-state preservation on a product probe;
- Hadamard does not break real-up-to-phase preservation on a real probe;
- Hadamard does not break stabilizer preservation on a stabilizer probe;
- non-unitary candidate is rejected;
- wrong-dimension candidate is rejected;
- invalid probe precondition is rejected;
- operator remint/global rephase leaves verdict unchanged.

## Reopen triggers

Reopen if the witness interface needs candidate-supplied target labels, if tolerance dominates the verdict on clean exact controls, or if one invariant requires fundamentally different authority semantics.

## Authority

Engineering/evaluator substrate only. A GREEN witness means only `INVARIANT_BREAK_VERIFIED` for the declared probe and incumbent invariant.