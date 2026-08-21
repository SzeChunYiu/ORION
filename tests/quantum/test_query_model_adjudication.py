import math

from orion.quantum.vs1 import query_model_comparison


def test_hidden_uniform_query_model_is_independent_of_public_fixture_distribution() -> None:
    expected_iterations = {3: 2, 4: 3, 5: 4, 6: 6, 7: 8, 8: 12, 9: 17, 10: 25}
    for n_qubits, iterations in expected_iterations.items():
        comparison = query_model_comparison(n_qubits)
        search_size = 1 << n_qubits
        classical_budget = search_size - 1
        classical_expected = classical_budget - (
            classical_budget * (classical_budget - 1) / (2 * search_size)
        )

        assert comparison["model"] == "HIDDEN_UNIFORM_SINGLE_MARK_QUERY_MODEL"
        assert comparison["fixture_cases_used_for_advantage"] is False
        assert comparison["quantum_query_budget"] == iterations
        assert comparison["classical_matching_query_budget"] == classical_budget
        assert math.isclose(
            comparison["classical_matching_expected_queries"],
            classical_expected,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        assert comparison["classical_free_final_guess_allowed"] is True
        assert comparison["external_output_verification_is_separate_resource"] is True
        assert comparison["quantum_query_budget"] < comparison["classical_matching_query_budget"]
        assert (
            comparison["quantum_query_budget"]
            < comparison["classical_matching_expected_queries"]
        )


def test_query_model_reports_analytic_success_not_fixture_success_frequency() -> None:
    comparison = query_model_comparison(3)

    assert math.isclose(
        comparison["quantum_single_run_success_probability"],
        0.9453125,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert comparison["success_probability_source"] == "ANALYTIC_GROVER_AMPLITUDE"
    assert "fixture" not in comparison["success_probability_source"].lower()
    assert comparison["classical_free_final_guess_allowed"] is True
    assert comparison["external_output_verification_is_separate_resource"] is True
