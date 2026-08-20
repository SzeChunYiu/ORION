"""Semantic admission gate for proposed ORION-Q quantum language edits.

A generator may propose an opaque unitary operator and an incumbent-valid probe
state. The evaluator executes the operator itself and checks whether the output
violates the invariant preserved by the declared incumbent language.

A positive result means only that the candidate *breaks that invariant on the
supplied witness*. It does not prove that the motivating target is solved, that
the edit is minimal, or that the operator is scientifically novel.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Sequence

from orion.transfer.v2.canonical import content_digest

from .quantum_obstruction import (
    DEFAULT_ATOL,
    PureState,
    QuantumLanguageCapability,
    is_one_qubit_stabilizer_state,
    is_real_up_to_global_phase,
    is_two_qubit_product_state,
)


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


def _encode_matrix(matrix: Sequence[Sequence[complex]]) -> list[list[list[float]]]:
    return [
        [[float(value.real), float(value.imag)] for value in row]
        for row in matrix
    ]


class InvariantBreakVerdict(str, Enum):
    VERIFIED = "INVARIANT_BREAK_VERIFIED"
    NOT_BROKEN = "INVARIANT_NOT_BROKEN"


@dataclass(frozen=True)
class UnitaryOperator:
    """Small opaque finite unitary used only by the exact QC-2 verifier."""

    operator_id: str
    matrix: tuple[tuple[complex, ...], ...]

    def verify(self, *, atol: float = DEFAULT_ATOL) -> None:
        if not self.operator_id:
            raise ValueError("operator id is required")
        if atol <= 0 or not math.isfinite(atol):
            raise ValueError("atol must be finite and positive")
        dimension = len(self.matrix)
        if dimension == 0:
            raise ValueError("operator matrix is required")
        if dimension & (dimension - 1):
            raise ValueError("operator dimension must be a power of two")
        if any(len(row) != dimension for row in self.matrix):
            raise ValueError("operator matrix must be square")
        if any(not _finite_complex(value) for row in self.matrix for value in row):
            raise ValueError("operator entries must be finite")

        for left_column in range(dimension):
            for right_column in range(dimension):
                inner = sum(
                    self.matrix[row][left_column].conjugate()
                    * self.matrix[row][right_column]
                    for row in range(dimension)
                )
                expected = 1.0 if left_column == right_column else 0.0
                if abs(inner - expected) > atol:
                    raise ValueError("operator matrix must be unitary")

    @property
    def dimension(self) -> int:
        return len(self.matrix)

    def model_payload(self, *, atol: float = DEFAULT_ATOL) -> dict[str, object]:
        self.verify(atol=atol)
        return {
            "schema": "ORIONQ.UnitaryOperator.v1",
            "dimension": self.dimension,
            "matrix": _encode_matrix(self.matrix),
        }

    def model_fingerprint(self, *, atol: float = DEFAULT_ATOL) -> str:
        return content_digest(self.model_payload(atol=atol))

    def apply(self, state: PureState, *, atol: float = DEFAULT_ATOL) -> PureState:
        self.verify(atol=atol)
        state.verify(atol=atol)
        if len(state.amplitudes) != self.dimension:
            raise ValueError("operator/state dimension mismatch")
        output = tuple(
            sum(
                self.matrix[row][column] * state.amplitudes[column]
                for column in range(self.dimension)
            )
            for row in range(self.dimension)
        )
        result = PureState(
            state_id=f"{state.state_id}:after:{self.operator_id}",
            amplitudes=output,
        )
        result.verify(atol=atol)
        return result

    def rephase(self, phase: complex, *, atol: float = DEFAULT_ATOL) -> UnitaryOperator:
        self.verify(atol=atol)
        if not _finite_complex(phase):
            raise ValueError("operator global phase must be finite")
        if not math.isclose(abs(phase), 1.0, rel_tol=0.0, abs_tol=atol):
            raise ValueError("operator global phase must have unit magnitude")
        return UnitaryOperator(
            operator_id=f"{self.operator_id}:rephased",
            matrix=tuple(tuple(phase * value for value in row) for row in self.matrix),
        )


@dataclass(frozen=True)
class QuantumInvariantBreakWitness:
    """Candidate operator plus a probe whose post-state is evaluator-derived."""

    witness_id: str
    capability: QuantumLanguageCapability
    operator: UnitaryOperator
    probe: PureState

    def verify_model_input(self, *, atol: float = DEFAULT_ATOL) -> None:
        if not self.witness_id:
            raise ValueError("witness id is required")
        if not isinstance(self.capability, QuantumLanguageCapability):
            raise ValueError("unsupported quantum capability contract")
        self.operator.verify(atol=atol)
        self.probe.verify(atol=atol)
        if self.operator.dimension != len(self.probe.amplitudes):
            raise ValueError("operator/state dimension mismatch")

    def model_payload(self, *, atol: float = DEFAULT_ATOL) -> dict[str, object]:
        self.verify_model_input(atol=atol)
        return {
            "schema": "ORIONQ.InvariantBreakInput.v1",
            "capability": self.capability.value,
            "operator": self.operator.model_payload(atol=atol),
            "probe": self.probe.model_payload(atol=atol),
        }

    def model_fingerprint(self, *, atol: float = DEFAULT_ATOL) -> str:
        return content_digest(self.model_payload(atol=atol))

    def evaluator_output(self, *, atol: float = DEFAULT_ATOL) -> PureState:
        self.verify_model_input(atol=atol)
        return self.operator.apply(self.probe, atol=atol)

    def verdict(self, *, atol: float = DEFAULT_ATOL) -> InvariantBreakVerdict:
        """Validate the probe first, then execute and check whether the invariant breaks."""

        self.verify_model_input(atol=atol)

        if self.capability is QuantumLanguageCapability.LOCAL_PRODUCT_ONLY:
            if len(self.probe.amplitudes) != 4:
                raise ValueError("local-product witness currently requires two qubits")
            if not is_two_qubit_product_state(self.probe, atol=atol):
                raise ValueError("local-product witness requires a product probe")
            output = self.operator.apply(self.probe, atol=atol)
            broken = not is_two_qubit_product_state(output, atol=atol)

        elif self.capability is QuantumLanguageCapability.REAL_UNITARY_ONLY:
            if not is_real_up_to_global_phase(self.probe, atol=atol):
                raise ValueError("real-unitary witness requires a real-up-to-phase probe")
            output = self.operator.apply(self.probe, atol=atol)
            broken = not is_real_up_to_global_phase(output, atol=atol)

        elif self.capability is QuantumLanguageCapability.CLIFFORD_ONLY:
            if len(self.probe.amplitudes) != 2:
                raise ValueError("Clifford witness currently requires exactly one qubit")
            if not is_one_qubit_stabilizer_state(self.probe, atol=atol):
                raise ValueError("Clifford witness requires a stabilizer probe")
            output = self.operator.apply(self.probe, atol=atol)
            broken = not is_one_qubit_stabilizer_state(output, atol=atol)

        else:  # pragma: no cover - enum extension guard
            raise ValueError("unsupported quantum capability contract")

        if broken:
            return InvariantBreakVerdict.VERIFIED
        return InvariantBreakVerdict.NOT_BROKEN


__all__ = [
    "InvariantBreakVerdict",
    "QuantumInvariantBreakWitness",
    "UnitaryOperator",
]
