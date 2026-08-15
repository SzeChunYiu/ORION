import pytest

from orion.mechanics.answers import AnswerRecord, AnswerResidualKind, apply_answer_records
from orion.mechanics.model import (
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.questioning import generate_mechanic_questions


def _metric(metric_id="metric:test"):
    return MetricSpec(
        metric_id=metric_id,
        description="A step-specific diagnostic metric.",
        kind=MetricKind.DIAGNOSTIC,
        direction=MetricDirection.OBSERVE_ONLY,
        unit="typed",
    )


def test_metric_payload_is_only_valid_for_metrics_dimension_and_ids_must_be_unique():
    with pytest.raises(ValueError, match="only valid for the METRICS"):
        AnswerRecord(
            "r:wrong",
            "SEARCH.test",
            MechanicDimension.STATE,
            "test",
            evidence_refs=("e:1",),
            metric_payload=(_metric(),),
        )
    with pytest.raises(ValueError, match="ids must be unique"):
        AnswerRecord(
            "r:dup",
            "SEARCH.test",
            MechanicDimension.METRICS,
            "test",
            evidence_refs=("e:1",),
            metric_payload=(_metric(), _metric()),
        )


def test_valid_metric_answer_closes_exactly_the_metric_question_and_preserves_evidence_gate():
    cell = MechanicCell(
        "SEARCH.test",
        "Find evidence.",
        "fixture",
        provisional_dimensions=(MechanicDimension.METRICS,),
    )
    record = AnswerRecord(
        "r:metric",
        cell.mechanic_id,
        MechanicDimension.METRICS,
        "test",
        evidence_refs=("e:metric-contract",),
        metric_payload=(_metric(),),
    )
    updated, report = apply_answer_records((cell,), (record,))
    assert report.residuals == ()
    assert report.applied_record_ids == ("r:metric",)
    assert updated[0].metrics == (_metric(),)
    assert MechanicDimension.METRICS not in updated[0].provisional_dimensions
    assert all(item.dimension is not MechanicDimension.METRICS for item in generate_mechanic_questions(updated[0]))

    no_evidence = AnswerRecord(
        "r:no-evidence",
        cell.mechanic_id,
        MechanicDimension.METRICS,
        "test",
        metric_payload=(_metric("metric:no-evidence"),),
    )
    _, blocked = apply_answer_records((cell,), (no_evidence,))
    assert blocked.applied_record_ids == ()
    assert blocked.residuals[0].kind == AnswerResidualKind.NO_EVIDENCE
