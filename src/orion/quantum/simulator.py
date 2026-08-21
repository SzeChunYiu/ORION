from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any


PINNED_QISKIT_VERSION = "2.5.1"
PINNED_QISKIT_AER_VERSION = "0.17.2"
PINNED_BACKEND_NAME = "AerSimulator"
PINNED_BACKEND_METHOD = "statevector"


@dataclass(frozen=True)
class GroverCaseExecution:
    case_id: str
    n_qubits: int
    search_size: int
    case_index: int
    marked_index: int
    iterations: int
    analytic_marked_probability: float
    simulated_marked_probability: float
    normalization_error: float
    measured_candidates: tuple[int, ...]
    returned_candidate: int | None
    attempts: int
    oracle_calls: int
    verification_predicate_calls: int
    measurement_shots: int
    classical_ordered_calls: int
    classical_random_calls: int
    classical_random_seed: int
    backend_identity: tuple[tuple[str, str], ...]
    circuit_qubits: int
    logical_depth: int
    transpiled_depth: int
    logical_ops: tuple[tuple[str, int], ...]
    transpiled_ops: tuple[tuple[str, int], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "ORION.QN.GroverCaseExecution.v1",
            "case_id": self.case_id,
            "n_qubits": self.n_qubits,
            "search_size": self.search_size,
            "case_index": self.case_index,
            "marked_index": self.marked_index,
            "iterations": self.iterations,
            "analytic_marked_probability": self.analytic_marked_probability,
            "simulated_marked_probability": self.simulated_marked_probability,
            "normalization_error": self.normalization_error,
            "measured_candidates": list(self.measured_candidates),
            "returned_candidate": self.returned_candidate,
            "attempts": self.attempts,
            "oracle_calls": self.oracle_calls,
            "verification_predicate_calls": self.verification_predicate_calls,
            "measurement_shots": self.measurement_shots,
            "classical_ordered_calls": self.classical_ordered_calls,
            "classical_random_calls": self.classical_random_calls,
            "classical_random_seed": self.classical_random_seed,
            "backend_identity": dict(self.backend_identity),
            "circuit_qubits": self.circuit_qubits,
            "logical_depth": self.logical_depth,
            "transpiled_depth": self.transpiled_depth,
            "logical_ops": dict(self.logical_ops),
            "transpiled_ops": dict(self.transpiled_ops),
        }


def frozen_s1a_marked_positions(n_qubits: int) -> tuple[int, ...]:
    if n_qubits < 3 or n_qubits > 10:
        raise ValueError("S1A v1 size ladder requires 3 <= n_qubits <= 10")
    search_size = 1 << n_qubits
    generator = random.Random(734000 + n_qubits)
    interior = sorted(generator.sample(range(1, search_size - 1), 6))
    return (0, search_size - 1, *interior)


def analytic_grover_probability(search_size: int, iterations: int) -> float:
    if search_size < 2 or search_size & (search_size - 1):
        raise ValueError("search_size must be a power of two >= 2")
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    theta = math.asin(1.0 / math.sqrt(search_size))
    return math.sin((2 * iterations + 1) * theta) ** 2


def optimal_single_marked_iterations(search_size: int) -> int:
    if search_size < 2 or search_size & (search_size - 1):
        raise ValueError("search_size must be a power of two >= 2")
    theta = math.asin(1.0 / math.sqrt(search_size))
    target = math.pi / (4 * theta) - 0.5
    lower = max(0, math.floor(target))
    upper = max(0, math.ceil(target))
    candidates = sorted({lower, upper})
    return max(candidates, key=lambda value: (analytic_grover_probability(search_size, value), -value))


def _require_pinned_qiskit():
    import qiskit
    import qiskit_aer

    if qiskit.__version__ != PINNED_QISKIT_VERSION:
        raise RuntimeError(
            f"Qiskit version drift: expected {PINNED_QISKIT_VERSION}, got {qiskit.__version__}"
        )
    if qiskit_aer.__version__ != PINNED_QISKIT_AER_VERSION:
        raise RuntimeError(
            "Qiskit Aer version drift: expected "
            f"{PINNED_QISKIT_AER_VERSION}, got {qiskit_aer.__version__}"
        )
    return qiskit, qiskit_aer


def _append_multi_controlled_z(circuit, qubits: tuple[int, ...]) -> None:
    if not qubits:
        raise ValueError("at least one qubit is required")
    if len(qubits) == 1:
        circuit.z(qubits[0])
        return
    from qiskit.circuit.library import MCXGate

    target = qubits[-1]
    controls = qubits[:-1]
    circuit.h(target)
    circuit.append(MCXGate(len(controls)), [*controls, target])
    circuit.h(target)


def build_single_marked_grover_circuit(
    n_qubits: int,
    marked_index: int,
    *,
    iterations: int | None = None,
):
    qiskit, _ = _require_pinned_qiskit()
    from qiskit import QuantumCircuit

    if n_qubits < 1:
        raise ValueError("n_qubits must be positive")
    search_size = 1 << n_qubits
    if marked_index < 0 or marked_index >= search_size:
        raise ValueError("marked_index outside search space")
    if iterations is None:
        iterations = optimal_single_marked_iterations(search_size)
    if iterations < 0:
        raise ValueError("iterations must be non-negative")

    circuit = QuantumCircuit(n_qubits)
    circuit.h(range(n_qubits))
    qubits = tuple(range(n_qubits))

    for _ in range(iterations):
        # Phase oracle: map |marked> to |11...1>, phase flip it, then undo the map.
        for qubit in qubits:
            if ((marked_index >> qubit) & 1) == 0:
                circuit.x(qubit)
        _append_multi_controlled_z(circuit, qubits)
        for qubit in qubits:
            if ((marked_index >> qubit) & 1) == 0:
                circuit.x(qubit)

        # Grover diffusion about the uniform superposition.
        circuit.h(qubits)
        circuit.x(qubits)
        _append_multi_controlled_z(circuit, qubits)
        circuit.x(qubits)
        circuit.h(qubits)

    # Keep qiskit referenced so import/version checking cannot be optimized away in tests.
    assert qiskit.__version__ == PINNED_QISKIT_VERSION
    return circuit


def _ordered_classical_calls(marked_index: int) -> int:
    return marked_index + 1


def _random_classical_calls(search_size: int, marked_index: int, seed: int) -> int:
    order = list(range(search_size))
    random.Random(seed).shuffle(order)
    return order.index(marked_index) + 1


def execute_s1a_case(
    n_qubits: int,
    case_index: int,
    marked_index: int,
    *,
    max_attempts: int = 5,
) -> GroverCaseExecution:
    qiskit, qiskit_aer = _require_pinned_qiskit()
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    if max_attempts != 5:
        raise ValueError("S1A v1 freezes max_attempts=5")
    expected_positions = frozen_s1a_marked_positions(n_qubits)
    if case_index < 0 or case_index >= len(expected_positions):
        raise ValueError("case_index outside frozen S1A subject set")
    if expected_positions[case_index] != marked_index:
        raise ValueError("marked_index does not match frozen S1A subject identity")

    search_size = 1 << n_qubits
    iterations = optimal_single_marked_iterations(search_size)
    analytic_probability = analytic_grover_probability(search_size, iterations)
    logical = build_single_marked_grover_circuit(
        n_qubits,
        marked_index,
        iterations=iterations,
    )
    simulator = AerSimulator(method=PINNED_BACKEND_METHOD)
    compiled = transpile(logical, simulator, optimization_level=0)

    state_circuit = compiled.copy()
    state_circuit.save_statevector()
    state_result = simulator.run(state_circuit).result()
    statevector = state_result.get_statevector(state_circuit)
    probabilities = statevector.probabilities()
    simulated_probability = float(probabilities[marked_index])
    normalization_error = abs(float(sum(probabilities)) - 1.0)

    measured_candidates: list[int] = []
    returned_candidate: int | None = None
    attempts = 0
    for attempt_index in range(max_attempts):
        attempts = attempt_index + 1
        measured = compiled.copy()
        measured.measure_all()
        seed = 73400000 + n_qubits * 1000 + case_index * 10 + attempt_index
        result = simulator.run(measured, shots=1, seed_simulator=seed).result()
        counts = result.get_counts(measured)
        if len(counts) != 1:
            raise RuntimeError("one-shot measurement returned an unexpected counts shape")
        bitstring = next(iter(counts)).replace(" ", "")
        candidate = int(bitstring, 2)
        measured_candidates.append(candidate)
        if candidate == marked_index:
            returned_candidate = candidate
            break

    classical_seed = 73500000 + n_qubits * 1000 + case_index
    backend_identity = tuple(
        sorted(
            {
                "qiskit_version": qiskit.__version__,
                "qiskit_aer_version": qiskit_aer.__version__,
                "backend_family": "qiskit-aer",
                "backend_name": PINNED_BACKEND_NAME,
                "method": PINNED_BACKEND_METHOD,
                "noise_model": "none",
                "evidence_mode": "LOCAL_SIMULATION",
            }.items()
        )
    )

    return GroverCaseExecution(
        case_id=f"S1A-n{n_qubits}-case{case_index}-marked{marked_index}",
        n_qubits=n_qubits,
        search_size=search_size,
        case_index=case_index,
        marked_index=marked_index,
        iterations=iterations,
        analytic_marked_probability=analytic_probability,
        simulated_marked_probability=simulated_probability,
        normalization_error=normalization_error,
        measured_candidates=tuple(measured_candidates),
        returned_candidate=returned_candidate,
        attempts=attempts,
        oracle_calls=iterations * attempts,
        verification_predicate_calls=attempts,
        measurement_shots=attempts,
        classical_ordered_calls=_ordered_classical_calls(marked_index),
        classical_random_calls=_random_classical_calls(search_size, marked_index, classical_seed),
        classical_random_seed=classical_seed,
        backend_identity=backend_identity,
        circuit_qubits=logical.num_qubits,
        logical_depth=int(logical.depth()),
        transpiled_depth=int(compiled.depth()),
        logical_ops=tuple(sorted((str(key), int(value)) for key, value in logical.count_ops().items())),
        transpiled_ops=tuple(
            sorted((str(key), int(value)) for key, value in compiled.count_ops().items())
        ),
    )
