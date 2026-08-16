from dataclasses import replace

from orion.kernel.protected_identity import protected_projection_hash
from orion.kernel.transition import (
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    ProgramProjection,
    projection_hash,
)
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import (
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)


def _seed():
    return (
        MechanicCell(
            "SEARCH.QUERY.v0",
            "query",
            "scope",
            provisional_dimensions=(MechanicDimension.METRICS,),
        ),
    )


def _projection(records=(), active=()):
    return ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        _seed(),
        records=records,
        active_record_ids=active,
    )


def _metric(description="retrieval recall", threshold="higher is better"):
    return MetricSpec(
        metric_id="recall",
        description=description,
        kind=MetricKind.COVERAGE,
        direction=MetricDirection.MAXIMIZE,
        unit="ratio",
        threshold_semantics=threshold,
        uncertainty_semantics="report confidence interval when available",
    )


def _record(metric):
    return AnswerRecord(
        record_id="metric:r1",
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.METRICS,
        lane="proposal:test",
        metric_payload=(metric,),
    )


def test_metric_free_projection_is_legacy_hash_compatible():
    projection = _projection()
    assert protected_projection_hash(projection) == projection_hash(projection)


def test_metric_payload_changes_protected_state_identity():
    first_record = _record(_metric())
    first = _projection((first_record,), (first_record.record_id,))
    changed_record = _record(_metric(description="recall over complete frozen relevant set"))
    changed = _projection((changed_record,), (changed_record.record_id,))

    # The historical V1 projection identity predates metric_payload and is kept
    # frozen for replay/migration. Protected transitions extend it explicitly.
    assert projection_hash(first) == projection_hash(changed)
    assert protected_projection_hash(first) != protected_projection_hash(changed)


def test_threshold_and_uncertainty_semantics_are_bound_too():
    base_record = _record(_metric())
    base = _projection((base_record,), (base_record.record_id,))

    threshold_record = _record(_metric(threshold="must exceed matched BM25 baseline"))
    threshold = _projection((threshold_record,), (threshold_record.record_id,))
    assert protected_projection_hash(base) != protected_projection_hash(threshold)

    uncertainty_record = _record(
        replace(_metric(), uncertainty_semantics="bootstrap interval over frozen tasks")
    )
    uncertainty = _projection((uncertainty_record,), (uncertainty_record.record_id,))
    assert protected_projection_hash(base) != protected_projection_hash(uncertainty)


def test_metric_record_id_and_complete_metric_vector_are_domain_bound():
    record = _record(_metric())
    first = _projection((record,), (record.record_id,))
    changed_id = replace(record, record_id="metric:r2")
    second = _projection((changed_id,), (changed_id.record_id,))
    assert protected_projection_hash(first) != protected_projection_hash(second)
