import pytest

from orion.quantum import (
    QAccessMatch,
    QAdvantageReceipt,
    QResourceSummary,
    QuantumAccessMode,
    QuantumAdvantageTerminal,
    QuantumContractError,
    QuantumEvidenceMode,
    validate_advantage_receipt,
)


MATCHED = QAccessMatch(
    same_problem=True,
    same_information=True,
    same_tolerance=True,
    quantum_access_mode=QuantumAccessMode.NATIVE_COHERENT_ORACLE,
)


def receipt(
    *,
    evidence_mode: QuantumEvidenceMode,
    terminal: QuantumAdvantageTerminal,
    access_match: QAccessMatch = MATCHED,
    unresolved: tuple[str, ...] = (),
    query_claim_bounded: bool = False,
) -> QAdvantageReceipt:
    return QAdvantageReceipt(
        receipt_id="test-receipt",
        evidence_mode=evidence_mode,
        terminal=terminal,
        access_match=access_match,
        resources=QResourceSummary(unresolved_end_to_end_coordinates=unresolved),
        query_claim_bounded=query_claim_bounded,
    )


def test_local_simulation_allows_explicitly_bounded_query_advantage() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        query_claim_bounded=True,
        unresolved=("physical_qubits", "ft_runtime"),
    )

    assert validate_advantage_receipt(candidate) is candidate


@pytest.mark.parametrize(
    "terminal",
    [
        QuantumAdvantageTerminal.QUANTUM_PROJECTED_FT_ADVANTAGE,
        QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
    ],
)
def test_local_simulation_cannot_claim_ft_or_physical_advantage(
    terminal: QuantumAdvantageTerminal,
) -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=terminal,
    )

    with pytest.raises(QuantumContractError, match="local simulation"):
        validate_advantage_receipt(candidate)


def test_resource_estimation_can_support_projected_ft_when_resources_resolved() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.RESOURCE_ESTIMATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_PROJECTED_FT_ADVANTAGE,
    )

    assert validate_advantage_receipt(candidate) is candidate


def test_resource_estimation_cannot_claim_observed_end_to_end_advantage() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.RESOURCE_ESTIMATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
    )

    with pytest.raises(QuantumContractError, match="resource estimation"):
        validate_advantage_receipt(candidate)


def test_real_qpu_end_to_end_receipt_requires_resolved_resources() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.REAL_QPU,
        terminal=QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
        unresolved=("state_prepare_time",),
    )

    with pytest.raises(QuantumContractError, match="state_prepare_time"):
        validate_advantage_receipt(candidate)


def test_real_qpu_end_to_end_receipt_can_pass_local_contract_gate() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.REAL_QPU,
        terminal=QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
    )

    assert validate_advantage_receipt(candidate) is candidate


@pytest.mark.parametrize(
    "access_match",
    [
        QAccessMatch(False, True, True),
        QAccessMatch(True, False, True),
        QAccessMatch(True, True, False),
    ],
)
def test_mismatched_comparison_rejects_positive_terminal(
    access_match: QAccessMatch,
) -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.REAL_QPU,
        terminal=QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
        access_match=access_match,
    )

    with pytest.raises(QuantumContractError, match="INVALID_COMPARISON"):
        validate_advantage_receipt(candidate)


@pytest.mark.parametrize(
    "access_match",
    [
        QAccessMatch(False, True, True),
        QAccessMatch(True, False, True),
        QAccessMatch(True, True, False),
    ],
)
def test_mismatched_comparison_is_retained_when_explicitly_invalid(
    access_match: QAccessMatch,
) -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.INVALID_COMPARISON,
        access_match=access_match,
    )

    assert validate_advantage_receipt(candidate) is candidate


def test_unresolved_stronger_quantum_interface_rejects_query_advantage() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        access_match=QAccessMatch(
            True,
            True,
            True,
            True,
            QuantumAccessMode.NATIVE_COHERENT_ORACLE,
        ),
        query_claim_bounded=True,
    )

    with pytest.raises(QuantumContractError, match="stronger quantum interface"):
        validate_advantage_receipt(candidate)


def test_unresolved_stronger_quantum_interface_can_fail_closed() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL,
        access_match=QAccessMatch(True, True, True, True),
    )

    assert validate_advantage_receipt(candidate) is candidate


def test_query_advantage_requires_explicit_query_bounding() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
    )

    with pytest.raises(QuantumContractError, match="query-model"):
        validate_advantage_receipt(candidate)


def test_query_only_claim_may_retain_unresolved_physical_coordinates() -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        unresolved=("qec_scheme", "physical_qubits", "ft_runtime"),
        query_claim_bounded=True,
    )

    assert validate_advantage_receipt(candidate) is candidate


@pytest.mark.parametrize(
    "terminal",
    [
        QuantumAdvantageTerminal.CLASSICAL_PARENT_SUFFICIENT,
        QuantumAdvantageTerminal.DEQUANTIZED_PARENT_SUFFICIENT,
        QuantumAdvantageTerminal.QUANTUM_FEASIBLE_NO_ADVANTAGE,
        QuantumAdvantageTerminal.CANNOT_CHECK_HARDWARE,
    ],
)
def test_bounded_negative_terminals_are_first_class(
    terminal: QuantumAdvantageTerminal,
) -> None:
    candidate = receipt(
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=terminal,
        unresolved=("physical_qubits", "ft_runtime"),
    )

    assert validate_advantage_receipt(candidate) is candidate
