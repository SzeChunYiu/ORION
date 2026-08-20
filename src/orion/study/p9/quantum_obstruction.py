"""Exact quantum obstruction witnesses for the ORION-Q QC-2 benchmark.

This module is deliberately small and model-independent. It freezes algebraic
invariants before P9/P10 learning or search is allowed to use the benchmark.
Evaluator gold is derived from the invariant witness and is never part of the
model-visible payload or fingerprint.

The exact substrate currently covers three declared language capabilities:

* arbitrary local one-qubit unitaries on a two-qubit product input;
* arbitrary real-valued unitaries on an input that is real up to global phase;
* arbitrary Clifford operations on a one-qubit stabilizer input.

These are benchmark facts, not ORION novelty claims. No object here grants
scientific, novelty, adoption, or execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Sequence

from orion.transfer.v2.canonical import content_digest


DEFAULT_ATOL = 1e-10


class QuantumLanguageCapability(str, Enum):
    LOCAL_PRODUCT_ONLY = "LOCAL_PRODUCT_ONLY"
    REAL_UNITARY_ONLY = "REAL_UNITARY_ONLY"
    CLIFFORD_ONLY = "CLIFFORD_ONLY"


class QuantumObstructionVerdict(str, Enum):
    EXPRESSIVITY_OBSTRUCTION = "EXPRESSIVITY_OBSTRUCTION"
    INVARIANT_COMPATIBLE = "INVARIANT_COMPATIBLE"


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


def _norm_sq(amplitudes: Sequence[complex]) -> float:
    return math.fsum(abs(value) ** 2 for value in amplitudes)


def _encode_amplitudes(amplitudes: Sequence[complex]) -> list[list[float]]:
    return [[float(value.real), float(value.imag)] for value in amplitudes]


@dataclass(frozen=True)
class PureState:
    """Small normalized pure-state payload used by the exact benchmark only."""

    state_id: str
    amplitudes: tuple[complex, ...]

    def verify(self, *, atol: float = DEFAULT_ATOL) -> None:
        if not self.state_id:
            raise ValueError("state id is required")
        if not self.amplitudes:
            raise ValueError("state requires at least one amplitude")
        if atol <= 0 or not math.isfinite(atol):
            raise ValueError("atol must be finite and positive")
        if any(not _finite_complex(value) for value in self.amplitudes):
            raise ValueError("state amplitudes must be finite")
        norm_sq = _norm_sq(self.amplitudes)
        if not math.isclose(norm_sq, 1.0, rel_tol=0.0, abs_tol=atol):
            raise ValueError("state must be normalized")

    def model_payload(self, *, atol: float = DEFAULT_ATOL) -> dict[str, object]:
        """Return semantic amplitudes only; evaluator/state identity is excluded."""

        self.verify(atol=atol)
        return {
            "schema": "ORIONQ.PureState.v1",
            "amplitudes": _encode_amplitudes(self.amplitudes),
        }

    def rephase(self, phase: complex, *, atol: float = DEFAULT_ATOL) -> PureState:
        self.verify(atol=atol)
        if not _finite_complex(phase):
            raise ValueError("global phase must be finite")
        if not math.isclose(abs(phase), 1.0, rel_tol=0.0, abs_tol=atol):
            raise ValueError("global phase must have unit magnitude")
        return PureState(
            state_id=f"{self.state_id}:rephased",
            amplitudes=tuple(phase * value for value in self.amplitudes),
        )


def two_qubit_schmidt_determinant(
    state: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> complex:
    """Return the 2x2 coefficient determinant for a two-qubit pure state.

    For amplitudes ``(a00, a01, a10, a11)``, a pure two-qubit state is separable
    exactly when ``a00*a11 - a01*a10 == 0``. The determinant is therefore a
    direct Schmidt-rank obstruction witness and does not depend on search.
    """

    state.verify(atol=atol)
    if len(state.amplitudes) != 4:
        raise ValueError("Schmidt determinant requires exactly two qubits")
    a00, a01, a10, a11 = state.amplitudes
    return a00 * a11 - a01 * a10


def is_two_qubit_product_state(
    state: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> bool:
    return abs(two_qubit_schmidt_determinant(state, atol=atol)) <= atol


def is_real_up_to_global_phase(
    state: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Return whether all amplitudes can be made real by one global phase.

    A nonzero vector has this property iff every pairwise product
    ``a_i * conj(a_j)`` is real. This avoids choosing a privileged reference
    amplitude and is invariant under global rephasing.
    """

    state.verify(atol=atol)
    amplitudes = state.amplitudes
    for left_index, left in enumerate(amplitudes):
        for right in amplitudes[left_index + 1 :]:
            if abs((left * right.conjugate()).imag) > atol:
                return False
    return True


def one_qubit_bloch_vector(
    state: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> tuple[float, float, float]:
    """Return the Bloch vector of one normalized pure qubit state.

    For ``|psi> = a|0> + b|1>``, the coordinates are expectation values of
    Pauli X/Y/Z. They are invariant under global phase.
    """

    state.verify(atol=atol)
    if len(state.amplitudes) != 2:
        raise ValueError("Bloch vector requires exactly one qubit")
    a, b = state.amplitudes
    overlap = a.conjugate() * b
    return (
        float(2.0 * overlap.real),
        float(2.0 * overlap.imag),
        float(abs(a) ** 2 - abs(b) ** 2),
    )


def is_one_qubit_stabilizer_state(
    state: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Return whether a pure qubit is one of the six Pauli-axis stabilizer states.

    A pure one-qubit stabilizer state has Bloch vector equal to one of
    ``(+/-1,0,0)``, ``(0,+/-1,0)``, or ``(0,0,+/-1)``. The test is independent
    of the state's human-readable identity and global phase.
    """

    x, y, z = one_qubit_bloch_vector(state, atol=atol)
    coordinates = (x, y, z)
    axis_like = [math.isclose(abs(value), 1.0, rel_tol=0.0, abs_tol=atol) for value in coordinates]
    zero_like = [math.isclose(value, 0.0, rel_tol=0.0, abs_tol=atol) for value in coordinates]
    return sum(axis_like) == 1 and sum(zero_like) == 2


def classify_quantum_obstruction(
    capability: QuantumLanguageCapability,
    initial: PureState,
    target: PureState,
    *,
    atol: float = DEFAULT_ATOL,
) -> QuantumObstructionVerdict:
    """Classify an invariant obstruction for one frozen capability contract.

    ``INVARIANT_COMPATIBLE`` means only that this tranche's declared invariant
    does not rule the target out. It is intentionally weaker than a universal
    claim that an arbitrary concrete gate library or bounded search will reach it.
    """

    if not isinstance(capability, QuantumLanguageCapability):
        raise ValueError("unsupported quantum capability contract")
    initial.verify(atol=atol)
    target.verify(atol=atol)
    if len(initial.amplitudes) != len(target.amplitudes):
        raise ValueError("initial and target state dimensions must match")

    if capability is QuantumLanguageCapability.LOCAL_PRODUCT_ONLY:
        if len(initial.amplitudes) != 4:
            raise ValueError("local-product capability currently requires two qubits")
        if not is_two_qubit_product_state(initial, atol=atol):
            raise ValueError("local-product capability requires a product initial state")
        if is_two_qubit_product_state(target, atol=atol):
            return QuantumObstructionVerdict.INVARIANT_COMPATIBLE
        return QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION

    if capability is QuantumLanguageCapability.REAL_UNITARY_ONLY:
        if not is_real_up_to_global_phase(initial, atol=atol):
            raise ValueError("real-unitary capability requires a real-up-to-phase initial state")
        if is_real_up_to_global_phase(target, atol=atol):
            return QuantumObstructionVerdict.INVARIANT_COMPATIBLE
        return QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION

    if capability is QuantumLanguageCapability.CLIFFORD_ONLY:
        if len(initial.amplitudes) != 2:
            raise ValueError("Clifford capability currently requires exactly one qubit")
        if not is_one_qubit_stabilizer_state(initial, atol=atol):
            raise ValueError("Clifford capability requires a stabilizer initial state")
        if is_one_qubit_stabilizer_state(target, atol=atol):
            return QuantumObstructionVerdict.INVARIANT_COMPATIBLE
        return QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION

    raise ValueError("unsupported quantum capability contract")


@dataclass(frozen=True)
class QuantumObstructionCase:
    """One evaluator-bound exact case with a gold-free model projection."""

    case_id: str
    capability: QuantumLanguageCapability
    initial: PureState
    target: PureState
    gold: QuantumObstructionVerdict

    def verify_model_input(self, *, atol: float = DEFAULT_ATOL) -> None:
        if not self.case_id:
            raise ValueError("case id is required")
        if not isinstance(self.capability, QuantumLanguageCapability):
            raise ValueError("unsupported quantum capability contract")
        self.initial.verify(atol=atol)
        self.target.verify(atol=atol)
        if len(self.initial.amplitudes) != len(self.target.amplitudes):
            raise ValueError("initial and target state dimensions must match")

    def verify(self, *, atol: float = DEFAULT_ATOL) -> None:
        self.verify_model_input(atol=atol)
        if not isinstance(self.gold, QuantumObstructionVerdict):
            raise ValueError("invalid quantum obstruction gold")
        derived = classify_quantum_obstruction(
            self.capability,
            self.initial,
            self.target,
            atol=atol,
        )
        if self.gold is not derived:
            raise ValueError("quantum obstruction gold disagrees with exact witness")

    def model_payload(self, *, atol: float = DEFAULT_ATOL) -> dict[str, object]:
        """Model-visible contract; excludes case/state IDs and evaluator gold."""

        self.verify_model_input(atol=atol)
        return {
            "schema": "ORIONQ.QuantumObstructionInput.v1",
            "capability": self.capability.value,
            "initial": self.initial.model_payload(atol=atol),
            "target": self.target.model_payload(atol=atol),
        }

    def model_fingerprint(self, *, atol: float = DEFAULT_ATOL) -> str:
        return content_digest(self.model_payload(atol=atol))


__all__ = [
    "DEFAULT_ATOL",
    "PureState",
    "QuantumLanguageCapability",
    "QuantumObstructionCase",
    "QuantumObstructionVerdict",
    "classify_quantum_obstruction",
    "is_one_qubit_stabilizer_state",
    "is_real_up_to_global_phase",
    "is_two_qubit_product_state",
    "one_qubit_bloch_vector",
    "two_qubit_schmidt_determinant",
]
