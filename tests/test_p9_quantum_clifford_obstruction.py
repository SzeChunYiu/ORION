import math

import pytest

from orion.study.p9.quantum_obstruction import (
    PureState,
    QuantumLanguageCapability,
    QuantumObstructionVerdict,
    classify_quantum_obstruction,
    is_one_qubit_stabilizer_state,
    one_qubit_bloch_vector,
)


SQRT_HALF = 1.0 / math.sqrt(2.0)


def _state(state_id: str, *amplitudes: complex) -> PureState:
    return PureState(state_id=state_id, amplitudes=tuple(amplitudes))


def test_all_six_one_qubit_pauli_axis_states_are_stabilizer_states():
    states = (
        _state("z+", 1, 0),
        _state("z-", 0, 1),
        _state("x+", SQRT_HALF, SQRT_HALF),
        _state("x-", SQRT_HALF, -SQRT_HALF),
        _state("y+", SQRT_HALF, 1j * SQRT_HALF),
        _state("y-", SQRT_HALF, -1j * SQRT_HALF),
    )

    assert all(is_one_qubit_stabilizer_state(state) for state in states)


def test_bloch_vector_sign_convention_matches_pauli_y_eigenstates():
    y_plus = _state("y+", SQRT_HALF, 1j * SQRT_HALF)
    y_minus = _state("y-", SQRT_HALF, -1j * SQRT_HALF)

    assert one_qubit_bloch_vector(y_plus) == pytest.approx((0.0, 1.0, 0.0))
    assert one_qubit_bloch_vector(y_minus) == pytest.approx((0.0, -1.0, 0.0))


def test_magic_like_state_is_nonstabilizer_and_exact_clifford_obstruction():
    initial = _state("initial", 1, 0)
    phase = complex(math.cos(math.pi / 4.0), math.sin(math.pi / 4.0))
    magic = _state("opaque-target", SQRT_HALF, phase * SQRT_HALF)

    assert not is_one_qubit_stabilizer_state(magic)
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.CLIFFORD_ONLY,
        initial,
        magic,
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION


def test_stabilizer_target_is_only_invariant_compatible():
    initial = _state("initial", 1, 0)
    target = _state("opaque-target", SQRT_HALF, 1j * SQRT_HALF)

    assert classify_quantum_obstruction(
        QuantumLanguageCapability.CLIFFORD_ONLY,
        initial,
        target,
    ) is QuantumObstructionVerdict.INVARIANT_COMPATIBLE


def test_stabilizer_membership_and_clifford_verdict_are_global_phase_invariant():
    initial = _state("initial", 1, 0)
    phase = complex(math.cos(0.43), math.sin(0.43))
    magic_phase = complex(math.cos(math.pi / 8.0), math.sin(math.pi / 8.0))
    magic = _state("opaque-target", SQRT_HALF, magic_phase * SQRT_HALF)

    assert is_one_qubit_stabilizer_state(initial.rephase(phase))
    assert not is_one_qubit_stabilizer_state(magic.rephase(phase))
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.CLIFFORD_ONLY,
        initial.rephase(phase),
        magic.rephase(phase),
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION


def test_nonstabilizer_initial_state_fails_closed_for_clifford_contract():
    phase = complex(math.cos(math.pi / 7.0), math.sin(math.pi / 7.0))
    nonstabilizer = _state("bad-initial", SQRT_HALF, phase * SQRT_HALF)
    target = _state("target", 1, 0)

    with pytest.raises(ValueError, match="stabilizer initial state"):
        classify_quantum_obstruction(
            QuantumLanguageCapability.CLIFFORD_ONLY,
            nonstabilizer,
            target,
        )


def test_bloch_vector_rejects_non_qubit_state():
    two_qubit = _state("two-qubit", 1, 0, 0, 0)

    with pytest.raises(ValueError, match="exactly one qubit"):
        one_qubit_bloch_vector(two_qubit)
