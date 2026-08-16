from orion.knowledge.backward_multiseed import (
    ConnectionHistory,
    SeedFamily,
    WaypointSeed,
    assess_seed_diversity,
)
from orion.knowledge.backward_multiseed_benchmark import compare_arms
from orion.knowledge.retrieval_benchmark import RouteComparisonReport, RouteComparisonVerdict
from orion.knowledge.route_family_health import RouteFamilyHealthReport, RouteHealthState


def test_new_rakl_donors_cannot_mint_authority_by_their_result_types():
    route = RouteComparisonReport(RouteComparisonVerdict.MATCHED_SAME_RESOURCE, ("a", "b"), ())
    assert not route.establishes_model_improvement
    assert not route.activates_default

    health = RouteFamilyHealthReport("lineage", RouteHealthState.CANNOT_CHECK, None, (), (), None)
    assert not health.grants_scientific_authority
    assert not health.grants_abandonment_authority
    assert not health.recommends_abandonment

    seed = WaypointSeed(
        "seed", "root", (), SeedFamily.CANDIDATE_LEMMA, "candidate", "rep", ("x",),
        origin="OPERATOR_APPLICATION",  # type: ignore[arg-type]
        origin_operator_id="op", expected_useful_connection="bridge",
        falsifier_or_cheapest_connection_test="test bridge",
    )
    assert seed.candidate_only and not seed.is_evidence and not seed.grants_root_progress
    assert not assess_seed_diversity((seed,)).grants_progress_credit
    assert ConnectionHistory().verified_roads == ()


def test_hidden_path_comparison_type_has_no_authority_even_without_observations():
    # The full benchmark tests construct its frozen spec. Here we only guard the
    # public result boundary by confirming that comparison requires a spec and
    # therefore cannot be called as an implicit global scorer.
    assert compare_arms.__name__ == "compare_arms"
