from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class QuantumContractError(ValueError):
    """Raised when a quantum evidence receipt exceeds its admitted claim boundary."""


class QuantumEvidenceMode(StrEnum):
    """Evidence source classes with different scientific claim ceilings."""

    LOCAL_SIMULATION = "LOCAL_SIMULATION"
    RESOURCE_ESTIMATION = "RESOURCE_ESTIMATION"
    REAL_QPU = "REAL_QPU"


class QuantumAccessMode(StrEnum):
    """How the registered problem exposes the quantum oracle/interface."""

    UNSPECIFIED = "UNSPECIFIED"
    NATIVE_COHERENT_ORACLE = "NATIVE_COHERENT_ORACLE"
    DERIVED_COHERENT_ORACLE = "DERIVED_COHERENT_ORACLE"
    CLASSICAL_PREDICATE_ONLY = "CLASSICAL_PREDICATE_ONLY"


class QuantumAdvantageTerminal(StrEnum):
    """Bounded scientific terminals for an ORION-QN comparison."""

    CLASSICAL_PARENT_SUFFICIENT = "CLASSICAL_PARENT_SUFFICIENT"
    DEQUANTIZED_PARENT_SUFFICIENT = "DEQUANTIZED_PARENT_SUFFICIENT"
    QUANTUM_FEASIBLE_NO_ADVANTAGE = "QUANTUM_FEASIBLE_NO_ADVANTAGE"
    QUANTUM_QUERY_ADVANTAGE_ONLY = "QUANTUM_QUERY_ADVANTAGE_ONLY"
    QUANTUM_PROJECTED_FT_ADVANTAGE = "QUANTUM_PROJECTED_FT_ADVANTAGE"
    QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED = "QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED"
    CANNOT_CHECK_ACCESS_MODEL = "CANNOT_CHECK_ACCESS_MODEL"
    CANNOT_CHECK_HARDWARE = "CANNOT_CHECK_HARDWARE"
    INVALID_COMPARISON = "INVALID_COMPARISON"


_POSITIVE_TERMINALS = frozenset(
    {
        QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY,
        QuantumAdvantageTerminal.QUANTUM_PROJECTED_FT_ADVANTAGE,
        QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
    }
)

_END_TO_END_RESOURCE_TERMINALS = frozenset(
    {
        QuantumAdvantageTerminal.QUANTUM_PROJECTED_FT_ADVANTAGE,
        QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
    }
)


@dataclass(frozen=True)
class QAccessMatch:
    """Whether quantum and classical routes compare the same admitted problem.

    `same_information` does not imply that coherent oracle access is free. Positive
    quantum terminals additionally require an explicit quantum access mode. A native
    coherent query oracle is an admitted model assumption; a derived coherent oracle
    needs a separately resolved derivation obligation.
    """

    same_problem: bool
    same_information: bool
    same_tolerance: bool
    stronger_quantum_interface_unresolved: bool = False
    quantum_access_mode: QuantumAccessMode = QuantumAccessMode.UNSPECIFIED
    coherent_oracle_derivation_resolved: bool = False

    @property
    def comparison_matched(self) -> bool:
        return self.same_problem and self.same_information and self.same_tolerance


@dataclass(frozen=True)
class QResourceSummary:
    """Minimal resource completeness state for advantage adjudication.

    Full resource vectors belong in QResourceReceipt.v1. This subset records only
    whether a stronger-than-query claim still has load-bearing unknown coordinates.
    """

    unresolved_end_to_end_coordinates: tuple[str, ...] = ()

    @property
    def end_to_end_resolved(self) -> bool:
        return not self.unresolved_end_to_end_coordinates


@dataclass(frozen=True)
class QAdvantageReceipt:
    """Minimal executable subset of the ORION-QN QAdvantageReceipt.v1 contract."""

    receipt_id: str
    evidence_mode: QuantumEvidenceMode
    terminal: QuantumAdvantageTerminal
    access_match: QAccessMatch
    resources: QResourceSummary = QResourceSummary()
    query_claim_bounded: bool = False


def validate_advantage_receipt(receipt: QAdvantageReceipt) -> QAdvantageReceipt:
    """Fail closed when the receipt claims more authority than its evidence permits.

    This validator intentionally does not prove a quantum advantage. It only rejects
    comparisons that violate the frozen Q1 evidence/access/resource claim boundaries.
    """

    _validate_comparison_identity(receipt)
    _validate_access_model(receipt)
    _validate_evidence_ceiling(receipt)
    _validate_resource_completeness(receipt)
    _validate_query_claim_scope(receipt)
    return receipt


def _validate_comparison_identity(receipt: QAdvantageReceipt) -> None:
    access = receipt.access_match
    if access.comparison_matched:
        return
    if receipt.terminal is QuantumAdvantageTerminal.INVALID_COMPARISON:
        return
    raise QuantumContractError(
        "mismatched problem, information, or tolerance requires INVALID_COMPARISON"
    )


def _validate_access_model(receipt: QAdvantageReceipt) -> None:
    access = receipt.access_match
    if receipt.terminal not in _POSITIVE_TERMINALS:
        return
    if access.stronger_quantum_interface_unresolved:
        raise QuantumContractError(
            "positive quantum advantage cannot use an unresolved stronger quantum interface"
        )
    if access.quantum_access_mode is QuantumAccessMode.UNSPECIFIED:
        raise QuantumContractError(
            "positive quantum advantage requires an explicit quantum access mode"
        )
    if access.quantum_access_mode is QuantumAccessMode.CLASSICAL_PREDICATE_ONLY:
        raise QuantumContractError(
            "classical-predicate-only access cannot support a positive quantum terminal"
        )
    if (
        access.quantum_access_mode is QuantumAccessMode.DERIVED_COHERENT_ORACLE
        and not access.coherent_oracle_derivation_resolved
    ):
        raise QuantumContractError(
            "derived coherent oracle requires a resolved derivation before positive quantum claims"
        )


def _validate_evidence_ceiling(receipt: QAdvantageReceipt) -> None:
    if receipt.evidence_mode is QuantumEvidenceMode.LOCAL_SIMULATION:
        forbidden = {
            QuantumAdvantageTerminal.QUANTUM_PROJECTED_FT_ADVANTAGE,
            QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED,
        }
        if receipt.terminal in forbidden:
            raise QuantumContractError(
                "local simulation cannot support projected-FT or physical end-to-end advantage"
            )

    if (
        receipt.evidence_mode is QuantumEvidenceMode.RESOURCE_ESTIMATION
        and receipt.terminal
        is QuantumAdvantageTerminal.QUANTUM_END_TO_END_ADVANTAGE_SUPPORTED
    ):
        raise QuantumContractError(
            "resource estimation cannot support observed physical end-to-end advantage"
        )


def _validate_resource_completeness(receipt: QAdvantageReceipt) -> None:
    if receipt.terminal not in _END_TO_END_RESOURCE_TERMINALS:
        return
    if receipt.resources.end_to_end_resolved:
        return
    unresolved = ", ".join(receipt.resources.unresolved_end_to_end_coordinates)
    raise QuantumContractError(
        f"stronger advantage terminal has unresolved end-to-end resources: {unresolved}"
    )


def _validate_query_claim_scope(receipt: QAdvantageReceipt) -> None:
    if receipt.terminal is not QuantumAdvantageTerminal.QUANTUM_QUERY_ADVANTAGE_ONLY:
        return
    if receipt.query_claim_bounded:
        return
    raise QuantumContractError(
        "query advantage must be explicitly bounded as a query-model claim"
    )
