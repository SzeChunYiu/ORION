from dataclasses import replace

import pytest

from orion.study.p9.uncertain_transport import (
    AffineObservation,
    HiddenAffineMap,
    ObservedAffineTransform,
    TransformCycleCase,
)
from orion.study.p9.structural_world import GluingVerdict


def _edge(
    transform_id: str,
    source: str,
    target: str,
    observations: tuple[AffineObservation, ...],
) -> ObservedAffineTransform:
    return ObservedAffineTransform(
        transform_id=transform_id,
        source_chart_id=source,
        target_chart_id=target,
        observations=observations,
    )


def _unresolved_glue_case() -> TransformCycleCase:
    return TransformCycleCase(
        cycle_id="hidden-glue",
        edges=(
            _edge("ab", "a", "b", (AffineObservation(0.0, 1.0), AffineObservation(1.0, 3.0))),
            _edge("bc", "b", "c", (AffineObservation(0.0, -0.5), AffineObservation(1.0, 0.0))),
            _edge("ca", "c", "a", (AffineObservation(0.0, 0.0),)),
        ),
        hidden_truth=(
            HiddenAffineMap(2.0, 1.0),
            HiddenAffineMap(0.5, -0.5),
            HiddenAffineMap(1.0, 0.0),
        ),
        gold_if_fully_known=GluingVerdict.GLUE,
    )


def test_hidden_truth_must_generate_every_visible_observation():
    case = _unresolved_glue_case()
    case.verify()
    corrupted = replace(
        case,
        hidden_truth=case.hidden_truth[:-1] + (HiddenAffineMap(1.0, 4.0),),
    )

    with pytest.raises(ValueError, match="hidden truth.*observation"):
        corrupted.verify()


def test_fully_known_gold_must_equal_exact_composition_of_hidden_truth():
    case = _unresolved_glue_case()
    case.verify()
    wrong_gold = replace(case, gold_if_fully_known=GluingVerdict.OBSTRUCTION)

    with pytest.raises(ValueError, match="fully-known gold"):
        wrong_gold.verify()
