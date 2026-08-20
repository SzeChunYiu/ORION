from dataclasses import replace
import math

import pytest

from orion.study.p9.quantum_obstruction import (
    PureState,
    QuantumLanguageCapability,
    QuantumObstructionCase,
    QuantumObstructionVerdict,
    classify_quantum_obstruction,
    is_real_up_to_global_phase,
    is_two_qubit_product_state,
    two_qubit_schmidt_determinant,
)


SQRT_HALF = 1.0 / math.sqrt(2.0)


def _state(state_id: str, *amplitudes: complex) -> PureState:
    return PureState(state_id=state_id, amplitudes=tuple(amplitudes))


def test_bell_target_is_certified_obstruction_for_local_product_language():
    initial = _state("initial", 1, 0, 0, 0)
    bell = _state("target", SQRT_HALF, 0, 0, SQRT_HALF)

    assert is_two_qubit_product_state(initial)
    assert not is_two_qubit_product_state(bell)
    assert two_qubit_schmidt_determinant(bell) == pytest.approx(0.5)
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        initial,
        bell,
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION


def test_product_target_is_not_falsely_called_entanglement_obstruction():
    initial = _state("initial", 1, 0, 0, 0)
    product = _state("target", SQRT_HALF, SQRT_HALF, 0, 0)

    assert is_two_qubit_product_state(product)
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        initial,
        product,
    ) is QuantumObstructionVerdict.INVARIANT_COMPATIBLE


def test_intrinsically_complex_relative_phase_is_certified_obstruction():
    initial = _state("initial", 1, 0)
    phase_target = _state("target", SQRT_HALF, 1j * SQRT_HALF)

    assert is_real_up_to_global_phase(initial)
    assert not is_real_up_to_global_phase(phase_target)
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        initial,
        phase_target,
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION


def test_global_phase_does_not_create_false_complex_phase_obstruction():
    initial = _state("initial", 1, 0)
    real_target = _state("target", SQRT_HALF, -SQRT_HALF)
    phase = complex(math.cos(0.37), math.sin(0.37))
    rephased = real_target.rephase(phase)

    assert is_real_up_to_global_phase(real_target)
    assert is_real_up_to_global_phase(rephased)
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        initial,
        rephased,
    ) is QuantumObstructionVerdict.INVARIANT_COMPATIBLE


def test_obstruction_label_is_invariant_under_global_rephasing():
    product_initial = _state("initial", 1, 0, 0, 0)
    bell = _state("bell", SQRT_HALF, 0, 0, SQRT_HALF)
    real_initial = _state("real-initial", 1, 0)
    phase_target = _state("phase-target", SQRT_HALF, 1j * SQRT_HALF)
    phase = complex(math.cos(1.13), math.sin(1.13))

    assert classify_quantum_obstruction(
        QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        product_initial.rephase(phase),
        bell.rephase(phase),
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION
    assert classify_quantum_obstruction(
        QuantumLanguageCapability.REAL_UNITARY_ONLY,
        real_initial.rephase(phase),
        phase_target.rephase(phase),
    ) is QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION


def test_nonproduct_initial_state_fails_closed_for_local_product_contract():
    bell = _state("bell", SQRT_HALF, 0, 0, SQRT_HALF)
    product_target = _state("target", 1, 0, 0, 0)

    with pytest.raises(ValueError, match="product initial state"):
        classify_quantum_obstruction(
            QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
            bell,
            product_target,
        )


def test_nonreal_initial_state_fails_closed_for_real_unitary_contract():
    phase_initial = _state("initial", SQRT_HALF, 1j * SQRT_HALF)
    target = _state("target", 1, 0)

    with pytest.raises(ValueError, match="real-up-to-phase initial state"):
        classify_quantum_obstruction(
            QuantumLanguageCapability.REAL_UNITARY_ONLY,
            phase_initial,
            target,
        )


def test_invalid_states_are_rejected_instead_of_classified():
    zero = _state("zero", 0, 0)
    unnormalized = _state("bad", 1, 1)

    with pytest.raises(ValueError, match="normalized"):
        zero.verify()
    with pytest.raises(ValueError, match="normalized"):
        unnormalized.verify()


def test_model_fingerprint_excludes_case_and_state_identity_and_gold():
    initial = _state("initial-a", 1, 0)
    target = _state("target-a", SQRT_HALF, 1j * SQRT_HALF)
    case = QuantumObstructionCase(
        case_id="case-a",
        capability=QuantumLanguageCapability.REAL_UNITARY_ONLY,
        initial=initial,
        target=target,
        gold=QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION,
    )
    reminted = QuantumObstructionCase(
        case_id="case-b",
        capability=case.capability,
        initial=replace(initial, state_id="opaque-initial-b"),
        target=replace(target, state_id="opaque-target-b"),
        gold=QuantumObstructionVerdict.INVARIANT_COMPATIBLE,
    )

    assert case.model_fingerprint() == reminted.model_fingerprint()
    assert "case-a" not in str(case.model_payload())
    assert "initial-a" not in str(case.model_payload())
    assert "target-a" not in str(case.model_payload())
    assert "EXPRESSIVITY_OBSTRUCTION" not in str(case.model_payload())

    case.verify()
    with pytest.raises(ValueError, match="gold disagrees"):
        reminted.verify()


def test_quantum_case_verifies_gold_only_against_exact_witness():
    initial = _state("initial", 1, 0, 0, 0)
    target = _state("target", SQRT_HALF, 0, 0, SQRT_HALF)
    correct = QuantumObstructionCase(
        case_id="correct",
        capability=QuantumLanguageCapability.LOCAL_PRODUCT_ONLY,
        initial=initial,
        target=target,
        gold=QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION,
    )
    wrong = replace(correct, case_id="wrong", gold=QuantumObstructionVerdict.INVARIANT_COMPATIBLE)

    correct.verify()
    with pytest.raises(ValueError, match="gold disagrees"):
        wrong.verify()


def test_malformed_capability_contract_fails_closed_before_model_projection():
    initial = _state("initial", 1, 0)
    target = _state("target", 1, 0)
    malformed = QuantumObstructionCase(
        case_id="malformed",
        capability="REAL_UNITARY_ONLY",  # type: ignore[arg-type]
        initial=initial,
        target=target,
        gold=QuantumObstructionVerdict.INVARIANT_COMPATIBLE,
    )

    with pytest.raises(ValueError, match="unsupported quantum capability contract"):
        malformed.model_payload()
    with pytest.raises(ValueError, match="unsupported quantum capability contract"):
        classify_quantum_obstruction(
            "REAL_UNITARY_ONLY",  # type: ignore[arg-type]
            initial,
            target,
        )
