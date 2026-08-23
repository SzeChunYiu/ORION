import math

import pytest

from orion.study.p9.quantum_language_edit import (
    InvariantBreakVerdict,
    QuantumInvariantBreakWitness,
    UnitaryOperator,
)
from orion.study.p9.quantum_obstruction import PureState, QuantumLanguageCapability


SQRT_HALF = 1.0 / math.sqrt(2.0)


def _state(state_id: str, *amplitudes: complex) -> PureState:
    return PureState(state_id=state_id, amplitudes=tuple(amplitudes))


def _operator(operator_id: str, *rows: tuple[complex, ...]) -> UnitaryOperator:
    return UnitaryOperator(operator_id=operator_id, matrix=tuple(rows))


def test_cnot_class_operator_breaks_product_invariant_on_plus_zero_probe():
    cnot = _operator(
        "opaque-entangler",
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 1, 0),
    )
    plus_zero = _state("probe", SQRT_HALF, 0, SQRT_HALF, 0)
    witness = QuantumInvariantBreakWitness(
        "w-entangle",
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        cnot,
        plus_zero,
    )

    assert witness.verdict() is InvariantBreakVerdict.VERIFIED


def test_local_product_operator_does_not_receive_entanglement_break_credit():
    x_tensor_i = _operator(
        "opaque-local",
        (0, 0, 1, 0),
        (0, 0, 0, 1),
        (1, 0, 0, 0),
        (0, 1, 0, 0),
    )
    plus_zero = _state("probe", SQRT_HALF, 0, SQRT_HALF, 0)
    witness = QuantumInvariantBreakWitness(
        "w-local-decoy",
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        x_tensor_i,
        plus_zero,
    )

    assert witness.verdict() is InvariantBreakVerdict.NOT_BROKEN


def test_phase_operator_breaks_real_up_to_global_phase_invariant():
    phase_s = _operator("opaque-phase", (1, 0), (0, 1j))
    plus = _state("probe", SQRT_HALF, SQRT_HALF)
    witness = QuantumInvariantBreakWitness(
        "w-phase",
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        phase_s,
        plus,
    )

    assert witness.verdict() is InvariantBreakVerdict.VERIFIED


def test_real_hadamard_does_not_receive_complex_phase_break_credit():
    hadamard = _operator(
        "opaque-real",
        (SQRT_HALF, SQRT_HALF),
        (SQRT_HALF, -SQRT_HALF),
    )
    zero = _state("probe", 1, 0)
    witness = QuantumInvariantBreakWitness(
        "w-real-decoy",
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        hadamard,
        zero,
    )

    assert witness.verdict() is InvariantBreakVerdict.NOT_BROKEN


def test_nonclifford_phase_breaks_stabilizer_invariant():
    phase = complex(math.cos(math.pi / 4.0), math.sin(math.pi / 4.0))
    nonclifford = _operator("opaque-nonclifford", (1, 0), (0, phase))
    plus = _state("probe", SQRT_HALF, SQRT_HALF)
    witness = QuantumInvariantBreakWitness(
        "w-magic",
        QuantumLanguageCapability.CLIFFORD_ONLY,
        nonclifford,
        plus,
    )

    assert witness.verdict() is InvariantBreakVerdict.VERIFIED


def test_clifford_hadamard_does_not_receive_stabilizer_break_credit():
    hadamard = _operator(
        "opaque-clifford",
        (SQRT_HALF, SQRT_HALF),
        (SQRT_HALF, -SQRT_HALF),
    )
    zero = _state("probe", 1, 0)
    witness = QuantumInvariantBreakWitness(
        "w-clifford-decoy",
        QuantumLanguageCapability.CLIFFORD_ONLY,
        hadamard,
        zero,
    )

    assert witness.verdict() is InvariantBreakVerdict.NOT_BROKEN


def test_nonunitary_operator_is_rejected_before_witness_execution():
    bad = _operator("bad", (1, 0), (0, 2))

    with pytest.raises(ValueError, match="unitary"):
        bad.verify()


def test_operator_state_dimension_mismatch_fails_closed():
    identity = _operator("two", (1, 0), (0, 1))
    two_qubit = _state("four", 1, 0, 0, 0)
    witness = QuantumInvariantBreakWitness(
        "w-dimension",
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        identity,
        two_qubit,
    )

    with pytest.raises(ValueError, match="dimension mismatch"):
        witness.verdict()


def test_invalid_probe_precondition_is_rejected_not_scored_as_a_break():
    cnot = _operator(
        "opaque-entangler",
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 1, 0),
    )
    bell = _state("bad-probe", SQRT_HALF, 0, 0, SQRT_HALF)
    witness = QuantumInvariantBreakWitness(
        "w-invalid-probe",
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        cnot,
        bell,
    )

    with pytest.raises(ValueError, match="product probe"):
        witness.verdict()


def test_global_operator_phase_and_identity_remint_preserve_semantic_verdict():
    phase_s = _operator("operator-a", (1, 0), (0, 1j))
    plus = _state("probe-a", SQRT_HALF, SQRT_HALF)
    witness = QuantumInvariantBreakWitness(
        "w-a",
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        phase_s,
        plus,
    )
    global_phase = complex(math.cos(0.61), math.sin(0.61))
    reminted_operator = phase_s.rephase(global_phase)
    reminted_operator = UnitaryOperator("operator-b", reminted_operator.matrix)
    reminted_probe = PureState("probe-b", plus.amplitudes)
    reminted = QuantumInvariantBreakWitness(
        "w-b",
        witness.capability,
        reminted_operator,
        reminted_probe,
    )

    assert witness.verdict() is InvariantBreakVerdict.VERIFIED
    assert reminted.verdict() is InvariantBreakVerdict.VERIFIED
    assert witness.model_fingerprint() != reminted.model_fingerprint()
    assert phase_s.model_fingerprint() != reminted_operator.model_fingerprint()


def test_operator_identity_remint_alone_does_not_change_model_fingerprint():
    phase_s = _operator("operator-a", (1, 0), (0, 1j))
    reminted = UnitaryOperator("operator-b", phase_s.matrix)

    assert phase_s.model_fingerprint() == reminted.model_fingerprint()
