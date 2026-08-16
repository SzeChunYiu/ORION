from dataclasses import replace

from orion.kernel.transition import (
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    LedgerExpectation,
    ProgramProjection,
    projection_hash,
)
from orion.kernel.transition_reducer import (
    TransitionOperationKind,
    TransitionResidualKind,
    plan_answer_transition,
    plan_batch_transition,
    plan_reopen_transition,
    reduce_transition,
)
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)


def _cell(mechanic_id="SEARCH.QUERY.v0"):
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose="Generate scoped search queries.",
        scope="Known-world transition reducer test.",
        provisional_dimensions=(MechanicDimension.INPUTS, MechanicDimension.HANDOFF, MechanicDimension.METRICS),
    )


def _projection(*cells):
    return ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        tuple(cells or (_cell(),)),
    )


def _expectation(projection):
    return LedgerExpectation(
        None,
        projection_hash(projection),
        "a" * 64,
        "b" * 64,
    )


def _record(record_id="r1", *, supersedes="", mechanic_id="SEARCH.QUERY.v0", dimension=MechanicDimension.INPUTS):
    return AnswerRecord(
        record_id=record_id,
        mechanic_id=mechanic_id,
        dimension=dimension,
        lane="proposal:test",
        payload=(("input_ids", (f"input:{record_id}",)),),
        supersedes=supersedes,
    )


def test_plan_and_reducer_bind_exact_pre_and_post_state_without_authority():
    projection = _projection()
    plan = plan_answer_transition(
        projection,
        _record(),
        expectation=_expectation(projection),
        evidence_snapshot_hash="c" * 64,
    )
    result = reduce_transition(projection, plan)
    assert plan.pre_state_hash == projection_hash(projection)
    assert result.hash == plan.proposed_post_state_hash
    assert result.applied_record_ids == ("r1",)
    assert result.projection.active_record_ids == ("r1",)
    assert not plan.grants_transition_authority
    assert not result.grants_transition_authority


def test_unknown_mechanic_is_recorded_noop_not_silent_drop():
    projection = _projection()
    plan = plan_answer_transition(
        projection,
        _record(mechanic_id="UNKNOWN.MECHANIC"),
        expectation=_expectation(projection),
        evidence_snapshot_hash="c" * 64,
    )
    assert plan.operations[0].kind is TransitionOperationKind.RECORDED_NOOP
    assert plan.residuals[0].kind is TransitionResidualKind.UNKNOWN_MECHANIC
    assert plan.proposed_post_state_hash == plan.pre_state_hash
    result = reduce_transition(projection, plan)
    assert result.hash == projection_hash(projection)
    assert result.residuals[0].kind is TransitionResidualKind.UNKNOWN_MECHANIC


def test_waiver_is_unauthorized_and_cannot_change_projection():
    projection = _projection()
    waiver = AnswerRecord(
        record_id="waiver",
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.INPUTS,
        lane="proposal:test",
        waiver_reason="skip required input contract",
    )
    plan = plan_answer_transition(
        projection,
        waiver,
        expectation=_expectation(projection),
        evidence_snapshot_hash="c" * 64,
    )
    assert plan.residuals[0].kind is TransitionResidualKind.UNAUTHORIZED_WAIVER
    assert plan.proposed_post_state_hash == plan.pre_state_hash


def test_same_record_same_content_is_explicit_idempotent_noop():
    projection = _projection()
    first = plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64)
    committed = reduce_transition(projection, first).projection
    retry = plan_answer_transition(committed, _record(), expectation=_expectation(committed), evidence_snapshot_hash="c" * 64)
    assert retry.operations[0].kind is TransitionOperationKind.IDEMPOTENT_NOOP
    result = reduce_transition(committed, retry)
    assert result.idempotent_record_ids == ("r1",)
    assert result.hash == projection_hash(committed)


def test_same_record_id_changed_content_is_conflict():
    projection = _projection()
    committed = reduce_transition(
        projection,
        plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64),
    ).projection
    changed = AnswerRecord(
        record_id="r1",
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.INPUTS,
        lane="proposal:test",
        payload=(("input_ids", ("different",)),),
    )
    plan = plan_answer_transition(committed, changed, expectation=_expectation(committed), evidence_snapshot_hash="c" * 64)
    assert plan.residuals[0].kind is TransitionResidualKind.DUPLICATE_ID_CONFLICT
    assert plan.proposed_post_state_hash == plan.pre_state_hash


def test_cross_round_supersession_replaces_only_active_tip():
    projection = _projection()
    committed = reduce_transition(
        projection,
        plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64),
    ).projection
    replacement = _record("r2", supersedes="r1")
    plan = plan_answer_transition(committed, replacement, expectation=_expectation(committed), evidence_snapshot_hash="d" * 64)
    post = reduce_transition(committed, plan).projection
    assert tuple(record.record_id for record in post.records) == ("r1", "r2")
    assert post.active_record_ids == ("r2",)

    stale = _record("r3", supersedes="r1")
    stale_plan = plan_answer_transition(post, stale, expectation=_expectation(post), evidence_snapshot_hash="e" * 64)
    assert stale_plan.residuals[0].kind is TransitionResidualKind.SUPERSESSION_PARENT_NOT_ACTIVE


def test_replacement_without_explicit_supersession_fails_closed():
    projection = _projection()
    post = reduce_transition(
        projection,
        plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64),
    ).projection
    plan = plan_answer_transition(post, _record("r2"), expectation=_expectation(post), evidence_snapshot_hash="d" * 64)
    assert plan.residuals[0].kind is TransitionResidualKind.SUPERSESSION_REQUIRED
    assert plan.proposed_post_state_hash == plan.pre_state_hash


def test_reopen_removes_active_tip_but_preserves_historical_record():
    projection = _projection()
    committed = reduce_transition(
        projection,
        plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64),
    ).projection
    reopen = plan_reopen_transition(
        committed,
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.INPUTS,
        reason="fresh contradiction requires revalidation",
        expectation=_expectation(committed),
        evidence_snapshot_hash="d" * 64,
    )
    post = reduce_transition(committed, reopen).projection
    assert post.active_record_ids == ()
    assert tuple(record.record_id for record in post.records) == ("r1",)
    assert post.reopened_coordinates == (("SEARCH.QUERY.v0", "INPUTS", "fresh contradiction requires revalidation"),)


def test_answer_after_reopen_reactivates_coordinate_without_deleting_history():
    projection = _projection()
    first = reduce_transition(
        projection,
        plan_answer_transition(projection, _record(), expectation=_expectation(projection), evidence_snapshot_hash="c" * 64),
    ).projection
    reopened = reduce_transition(
        first,
        plan_reopen_transition(
            first,
            mechanic_id="SEARCH.QUERY.v0",
            dimension=MechanicDimension.INPUTS,
            reason="dependency changed",
            expectation=_expectation(first),
            evidence_snapshot_hash="d" * 64,
        ),
    ).projection
    replacement = _record("r2", supersedes="r1")
    post = reduce_transition(
        reopened,
        plan_answer_transition(reopened, replacement, expectation=_expectation(reopened), evidence_snapshot_hash="e" * 64),
    ).projection
    assert post.active_record_ids == ("r2",)
    assert post.reopened_coordinates == ()


def test_batch_is_sequential_and_second_operation_can_supersede_first():
    projection = _projection()
    plan = plan_batch_transition(
        projection,
        (_record("r1"), _record("r2", supersedes="r1")),
        expectation=_expectation(projection),
        evidence_snapshot_hash="c" * 64,
    )
    assert tuple(op.operation_index for op in plan.operations) == (0, 1)
    result = reduce_transition(projection, plan)
    assert result.applied_record_ids == ("r1", "r2")
    assert result.projection.active_record_ids == ("r2",)
    assert result.hash == plan.proposed_post_state_hash


def test_batch_conflict_is_not_counted_as_applied():
    projection = _projection()
    plan = plan_batch_transition(
        projection,
        (_record("r1"), _record("conflict")),
        expectation=_expectation(projection),
        evidence_snapshot_hash="c" * 64,
    )
    result = reduce_transition(projection, plan)
    assert result.applied_record_ids == ("r1",)
    assert result.residuals[-1].kind is TransitionResidualKind.SUPERSESSION_REQUIRED


def test_plan_identity_binds_handoff_payload_and_supersession():
    projection = _projection()
    handoff = AnswerRecord(
        record_id="h1",
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.HANDOFF,
        lane="proposal:test",
        handoff_payload=(HandoffField("query", "query", "schema:query", True),),
    )
    first = plan_answer_transition(projection, handoff, expectation=_expectation(projection), evidence_snapshot_hash="c" * 64)
    changed = replace(handoff, handoff_payload=(HandoffField("query", "query", "schema:query", False),))
    second = plan_answer_transition(projection, changed, expectation=_expectation(projection), evidence_snapshot_hash="c" * 64)
    assert first.transition_id != second.transition_id


def test_metric_payload_is_bound_by_plan_even_while_legacy_projection_hash_is_not_used_as_authority():
    projection = _projection()
    metric = MetricSpec(
        metric_id="recall",
        description="retrieval recall",
        kind=MetricKind.COVERAGE,
        direction=MetricDirection.MAXIMIZE,
        unit="ratio",
    )
    record = AnswerRecord(
        record_id="m1",
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.METRICS,
        lane="proposal:test",
        metric_payload=(metric,),
    )
    changed = replace(record, metric_payload=(replace(metric, description="changed description"),))
    first = plan_answer_transition(projection, record, expectation=_expectation(projection), evidence_snapshot_hash="c" * 64)
    second = plan_answer_transition(projection, changed, expectation=_expectation(projection), evidence_snapshot_hash="c" * 64)
    assert first.transition_id != second.transition_id


def test_wrong_expectation_does_not_plan_mutation():
    projection = _projection()
    wrong = replace(_expectation(projection), research_state_hash="f" * 64)
    plan = plan_answer_transition(projection, _record(), expectation=wrong, evidence_snapshot_hash="c" * 64)
    assert plan.residuals[0].kind is TransitionResidualKind.PRE_STATE_MISMATCH
    assert plan.pre_state_hash == plan.proposed_post_state_hash


def test_reducer_refuses_plan_against_wrong_pre_state():
    first = _projection(_cell())
    second = _projection(_cell(), _cell("ABSORB.CLAIM.v0"))
    plan = plan_answer_transition(first, _record(), expectation=_expectation(first), evidence_snapshot_hash="c" * 64)
    result = reduce_transition(second, plan)
    assert result.projection == second
    assert result.residuals[0].kind is TransitionResidualKind.PRE_STATE_MISMATCH
