from __future__ import annotations

from orion.self_orion.saturation_vector import DevelopmentSaturationAxis
from orion_research_harness.epistemic_navigation import RouteContract
from orion_research_harness.research_saturation import (
    ResearchRoundEvidence,
    assess_evidence_derived_saturation,
    derive_development_novelty_rounds,
)


def _round(round_id: str, *routes: RouteContract) -> ResearchRoundEvidence:
    return ResearchRoundEvidence(
        round_id=round_id,
        route_contracts=tuple(routes),
        observed_axes=tuple(DevelopmentSaturationAxis),
        axis_item_ids=(),
    )


def test_mixed_dependent_and_independent_routes_do_not_mint_independent_flat_round():
    first = RouteContract("r:first", "PARENT", ("o",), ("assumption:shared",), ("scope",))
    dependent = RouteContract("r:dependent", "FRESH", ("o",), ("assumption:shared",), ("scope",))
    independent = RouteContract("r:independent", "OMISSION", ("o",), ("assumption:other",), ("scope",))

    derived = derive_development_novelty_rounds(
        (_round("1", first), _round("2", dependent, independent))
    )
    assert derived[0].independent_route is True
    assert derived[1].independent_route is False

    report = assess_evidence_derived_saturation(
        (_round("1", first), _round("2", dependent, independent)),
        min_independent_flat_routes=2,
    )
    assert report.bounded_saturated is False


def test_single_route_rounds_with_disjoint_structural_assumptions_still_count():
    first = RouteContract("r:first", "PARENT", ("o",), ("assumption:a",), ("scope",))
    second = RouteContract("r:second", "OMISSION", ("o",), ("assumption:b",), ("scope",))
    report = assess_evidence_derived_saturation(
        (_round("1", first), _round("2", second)),
        min_independent_flat_routes=2,
    )
    assert report.bounded_saturated is True
