import pytest

from orion.study.orion_q.qsvt_route_proxy import (
    DepthPreference,
    QSVTProxyParameters,
    QSVTRoute,
)


def test_randomized_proxy_is_lower_above_algebraic_crossover():
    params = QSVTProxyParameters(term_count=100, lambda_l1=2.0, polynomial_degree=10)

    assert params.crossover_term_count == 20.0
    assert params.standard_depth_proxy == 2000.0
    assert params.randomized_depth_proxy == 400.0
    assert params.depth_preference() is DepthPreference.RANDOMIZED
    assert params.algebraic_depth_preference() is DepthPreference.RANDOMIZED


def test_standard_proxy_is_lower_below_algebraic_crossover():
    params = QSVTProxyParameters(term_count=10, lambda_l1=2.0, polynomial_degree=10)

    assert params.standard_depth_proxy == 200.0
    assert params.randomized_depth_proxy == 400.0
    assert params.depth_preference() is DepthPreference.STANDARD
    assert params.algebraic_depth_preference() is DepthPreference.STANDARD


def test_equal_crossover_is_reported_as_no_depth_dominance():
    params = QSVTProxyParameters(term_count=20, lambda_l1=2.0, polynomial_degree=10)

    assert params.standard_depth_proxy == params.randomized_depth_proxy
    assert params.depth_preference() is DepthPreference.NO_DOMINANCE
    assert params.algebraic_depth_preference() is DepthPreference.NO_DOMINANCE


def test_increasing_term_count_alone_can_cross_to_randomized_proxy():
    low_l = QSVTProxyParameters(term_count=15, lambda_l1=2.0, polynomial_degree=10)
    high_l = QSVTProxyParameters(term_count=25, lambda_l1=2.0, polynomial_degree=10)

    assert low_l.depth_preference() is DepthPreference.STANDARD
    assert high_l.depth_preference() is DepthPreference.RANDOMIZED


def test_increasing_degree_alone_can_cross_toward_standard_proxy():
    low_degree = QSVTProxyParameters(term_count=30, lambda_l1=2.0, polynomial_degree=10)
    high_degree = QSVTProxyParameters(term_count=30, lambda_l1=2.0, polynomial_degree=20)

    assert low_degree.depth_preference() is DepthPreference.RANDOMIZED
    assert high_degree.depth_preference() is DepthPreference.STANDARD


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"term_count": 0, "lambda_l1": 1.0, "polynomial_degree": 1}, "term_count"),
        ({"term_count": -1, "lambda_l1": 1.0, "polynomial_degree": 1}, "term_count"),
        ({"term_count": 1.5, "lambda_l1": 1.0, "polynomial_degree": 1}, "integer"),
        ({"term_count": 1, "lambda_l1": 0.0, "polynomial_degree": 1}, "lambda_l1"),
        ({"term_count": 1, "lambda_l1": float("inf"), "polynomial_degree": 1}, "lambda_l1"),
        ({"term_count": 1, "lambda_l1": 1.0, "polynomial_degree": 0}, "polynomial_degree"),
        ({"term_count": 1, "lambda_l1": 1.0, "polynomial_degree": 1.5}, "integer"),
    ],
)
def test_invalid_proxy_parameters_fail_closed(kwargs, message):
    params = QSVTProxyParameters(**kwargs)

    with pytest.raises(ValueError, match=message):
        params.verify()


def test_receipt_keeps_depth_and_ancilla_information_separate_and_non_authorizing():
    params = QSVTProxyParameters(term_count=100, lambda_l1=2.0, polynomial_degree=10)
    receipt = params.receipt()

    assert receipt["depth_preference"] == DepthPreference.RANDOMIZED.value
    assert receipt["ancilla_information"][QSVTRoute.STANDARD_BLOCK_ENCODED.value] == "O(log L)"
    assert receipt["ancilla_information"][QSVTRoute.RANDOMIZED.value] == 1
    assert receipt["limitations"]["asymptotic_proxy_only"] is True
    assert receipt["limitations"]["hidden_constants_unresolved"] is True
    assert receipt["limitations"]["polylogarithmic_factors_unresolved"] is True
    assert receipt["limitations"]["access_model_matching_required"] is True
    assert receipt["limitations"]["compiled_resource_claim_authorized"] is False
    assert receipt["limitations"]["scientific_route_authority"] is False
    assert isinstance(receipt["receipt_digest"], str)


def test_closed_form_rule_matches_direct_proxy_comparison_on_grid():
    for term_count in (1, 2, 5, 10, 20, 50, 100):
        for lambda_l1 in (0.5, 1.0, 2.0, 5.0):
            for degree in (1, 2, 5, 10, 20):
                params = QSVTProxyParameters(
                    term_count=term_count,
                    lambda_l1=lambda_l1,
                    polynomial_degree=degree,
                )
                assert params.depth_preference() is params.algebraic_depth_preference()
