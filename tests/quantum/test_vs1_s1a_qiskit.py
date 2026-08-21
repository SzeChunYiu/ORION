import math

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from orion.quantum.simulator import (
    PINNED_QISKIT_AER_VERSION,
    PINNED_QISKIT_VERSION,
    analytic_grover_probability,
    execute_s1a_case,
    frozen_s1a_marked_positions,
    optimal_single_marked_iterations,
)
from orion.quantum.verification import reconstruct_s1a_case


def test_frozen_subject_generator_has_edges_and_six_interior_cases() -> None:
    for n_qubits in range(3, 11):
        positions = frozen_s1a_marked_positions(n_qubits)
        search_size = 1 << n_qubits
        assert len(positions) == 8
        assert len(set(positions)) == 8
        assert positions[0] == 0
        assert positions[1] == search_size - 1
        assert all(0 <= item < search_size for item in positions)


def test_iteration_rule_maximizes_nearest_integer_probability() -> None:
    expected = {3: 2, 4: 3, 5: 4, 6: 6, 7: 8, 8: 12, 9: 17, 10: 25}
    for n_qubits, iterations in expected.items():
        search_size = 1 << n_qubits
        assert optimal_single_marked_iterations(search_size) == iterations
        probability = analytic_grover_probability(search_size, iterations)
        assert 0.94 < probability <= 1.0


def test_pinned_qiskit_case_executes_through_measurement_and_reconstructs() -> None:
    import qiskit
    import qiskit_aer

    assert qiskit.__version__ == PINNED_QISKIT_VERSION
    assert qiskit_aer.__version__ == PINNED_QISKIT_AER_VERSION

    execution = execute_s1a_case(3, 0, 0)
    record = execution.as_dict()
    reconstruction = reconstruct_s1a_case(record)

    assert execution.returned_candidate == 0
    assert 1 <= execution.attempts <= 5
    assert execution.oracle_calls == execution.iterations * execution.attempts
    assert math.isclose(
        execution.simulated_marked_probability,
        execution.analytic_marked_probability,
        rel_tol=0.0,
        abs_tol=1e-10,
    )
    assert execution.normalization_error <= 1e-10
    assert reconstruction["valid_record"] is True
    assert reconstruction["candidate_verified"] is True


def test_second_edge_case_does_not_depend_on_ordered_classical_luck() -> None:
    marked = (1 << 3) - 1
    execution = execute_s1a_case(3, 1, marked)
    reconstruction = reconstruct_s1a_case(execution.as_dict())

    assert execution.classical_ordered_calls == 8
    assert execution.returned_candidate == marked
    assert reconstruction["valid_record"] is True
    assert reconstruction["candidate_verified"] is True
