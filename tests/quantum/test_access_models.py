import pytest

from orion.quantum.contracts import (
    QAccessMatch,
    QAdvantageReceipt,
    QResourceSummary,
    QuantumAccessMode,
    QuantumAdvantageTerminal,
    QuantumContractError,
    QuantumEvidenceMode,
    validate_advantage_receipt,
)


def query_receipt(access: QAccessMatch) -> QAdvantageReceipt:
    return QAdvantageReceipt(
        receipt_id="q-access-red",
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        access_match=access,
        resources=QResourceSummary(
            unresolved_end_to_end_coordinates=("coherent_oracle_construction",)
        ),
        query_claim_bounded=True,
    )


def test_positive_query_requires_explicit_quantum_access_mode() -> None:
    receipt = query_receipt(
        QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.UNSPECIFIED,
        )
    )

    with pytest.raises(QuantumContractError, match="explicit quantum access mode"):
        validate_advantage_receipt(receipt)


def test_classical_predicate_only_cannot_support_positive_quantum_terminal() -> None:
    receipt = query_receipt(
        QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.CLASSICAL_PREDICATE_ONLY,
        )
    )

    with pytest.raises(QuantumContractError, match="classical-predicate-only"):
        validate_advantage_receipt(receipt)


def test_derived_coherent_oracle_requires_resolved_derivation() -> None:
    receipt = query_receipt(
        QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.DERIVED_COHERENT_ORACLE,
            coherent_oracle_derivation_resolved=False,
        )
    )

    with pytest.raises(QuantumContractError, match="derivation"):
        validate_advantage_receipt(receipt)


def test_native_coherent_oracle_can_support_bounded_query_terminal() -> None:
    receipt = query_receipt(
        QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.NATIVE_COHERENT_ORACLE,
        )
    )

    assert validate_advantage_receipt(receipt) is receipt


def test_classical_predicate_only_can_fail_closed_as_cannot_check() -> None:
    receipt = QAdvantageReceipt(
        receipt_id="q-access-cannot-check",
        evidence_mode=QuantumEvidenceMode.LOCAL_SIMULATION,
        terminal=QuantumAdvantageTerminal.CANNOT_CHECK_ACCESS_MODEL,
        access_match=QAccessMatch(
            same_problem=True,
            same_information=True,
            same_tolerance=True,
            quantum_access_mode=QuantumAccessMode.CLASSICAL_PREDICATE_ONLY,
        ),
    )

    assert validate_advantage_receipt(receipt) is receipt
