"""Route/task closure receipts and the guard denominators they carry (#650).

The properties under test are the ones that failed silently in the V1 campaign:
a total task taxonomy so no run ends in an unnamed state, a false-closure
denominator counted from declared closures rather than from tasks run, and both
of the evaluator's grounds for condemning a closure carried separately.

Unit behaviour is asserted on hand-built evaluations. The two end-to-end tests
replay a small slice of the frozen world so the receipts are checked against
what the shipped systems actually do, not only against fixtures.
"""

from __future__ import annotations

import functools

import pytest

from orion.programme.guard_exercise import assess_guard, assess_non_inferiority
from orion.programme.records import Outcome
from orion.study.p2.cases import build_tasks
from orion.study.p2.closure_receipts import (
    CampaignClosureLedger,
    FalseClosureKind,
    OutcomesNotAdmissible,
    RouteClosureKind,
    RouteClosureReceipt,
    TaskClosureKind,
    TaskClosureReceipt,
    build_ledger,
    build_task_receipt,
    require_closure_receipts,
)
from orion.study.p2.corpus import build_world
from orion.study.p2.gold import Evaluation, EvaluationInputs, StopAudit, evaluate
from orion.study.p2.offline_systems import system_by_id
from orion.study.p2.runner import build_public_index, execute
from orion.study.p2.systems import StopScope, SystemReport, SystemTrace

SEED = 20260816
SLICE = 12


@functools.cache
def _suite():
    """Build the frozen world once; it is deterministic on SEED and immutable."""

    world = build_world(SEED)
    return world, build_tasks(world), build_public_index(world)


def _replay(system_id: str, count: int = SLICE):
    world, tasks, index = _suite()
    pairs = []
    system = system_by_id(system_id)
    for task in tasks[:count]:
        outcome = execute(
            system, world, task, seed=SEED, run_manifest_hash="0" * 64, index=index
        )
        pairs.append((evaluate(EvaluationInputs(world=world, task=task, trace=outcome.trace)), outcome.trace))
    return pairs


def _audit(*, scope: str, claimed: bool, premature: bool = False, route: str = "") -> StopAudit:
    return StopAudit(
        index=1,
        scope=scope,
        route=route,
        reason="r",
        claimed_complete=claimed,
        still_reachable_count=1 if premature else 0,
        still_reachable_identities=("x",) if premature else (),
        remaining_route_calls=5 if premature else 0,
        premature=premature,
    )


def _evaluation(**overrides) -> Evaluation:
    base = dict(
        task_id="t1", case_family="f", system_id="s1", seed=SEED, status="PASS",
        failure_class=None, gold_denominator=1, discovered_gold_identities=(),
        missed_gold_identities=(), claimed_identities=(), unsupported_claimed_identities=(),
        false_positive_identities=(), route_contributions=(), route_pair_overlap=(),
        marginal_relevant_gain=(), stop_audits=(), censored_identities=(),
        unavailable_route_events=(), processing_pairs=(), duplicate_processing_count=0,
        legitimate_reread_count=0, first_read_count=0, resources=(),
    )
    base.update(overrides)
    return Evaluation(**base)


def _trace(**overrides) -> SystemTrace:
    base = dict(task_id="t1", system_id="s1", seed=SEED, report=SystemReport())
    base.update(overrides)
    return SystemTrace(**base)


class TestTaskTaxonomyIsTotal:
    def test_every_kind_is_produced_by_the_builder(self) -> None:
        """A kind nothing can produce is dead vocabulary; a run with no kind is the bug."""

        cases = {
            TaskClosureKind.CLOSED_COMPLETE: (
                _evaluation(stop_audits=(_audit(scope="TASK", claimed=True),)), _trace()
            ),
            TaskClosureKind.ABANDONED_RUN_ERROR: (
                _evaluation(stop_audits=(_audit(scope="TASK", claimed=False),)),
                _trace(error_class="candidate_error"),
            ),
            TaskClosureKind.ABANDONED_BUDGET_EXHAUSTED: (
                _evaluation(stop_audits=(_audit(scope="TASK", claimed=False),)),
                _trace(budget_exhausted="route_calls"),
            ),
            TaskClosureKind.REFUSED_OPEN_OBLIGATIONS: (
                _evaluation(
                    stop_audits=(_audit(scope="TASK", claimed=False),),
                    censored_identities=("c1",),
                ),
                _trace(),
            ),
            TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM: (
                _evaluation(stop_audits=(_audit(scope="TASK", claimed=False),)), _trace()
            ),
            TaskClosureKind.NO_CLOSURE_DECISION: (_evaluation(), _trace()),
        }
        assert set(cases) == set(TaskClosureKind)
        for expected, (evaluation, trace) in cases.items():
            assert build_task_receipt(evaluation, trace).kind is expected

    def test_the_external_slices_state_has_a_name(self) -> None:
        """24 of 24 external tasks ended here; the V1 counters could not say so."""

        receipt = build_task_receipt(
            _evaluation(stop_audits=(_audit(scope="TASK", claimed=False),)), _trace()
        )
        assert receipt.kind is TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM
        assert receipt.kind.exercises_false_closure_guard is False

    def test_only_a_closure_claim_exercises_the_guard(self) -> None:
        exercising = [kind for kind in TaskClosureKind if kind.exercises_false_closure_guard]
        assert exercising == [TaskClosureKind.CLOSED_COMPLETE]


class TestFalseClosureGrounds:
    def test_reachable_gold_outstanding(self) -> None:
        receipt = build_task_receipt(
            _evaluation(stop_audits=(_audit(scope="TASK", claimed=True, premature=True),)),
            _trace(),
        )
        assert receipt.false_closure is FalseClosureKind.REACHABLE_GOLD_OUTSTANDING
        assert receipt.premature_closure is True

    def test_censored_material_outstanding_is_counted_too(self) -> None:
        """The disjunct that never sets StopAudit.premature, and so hid 12 failures."""

        receipt = build_task_receipt(
            _evaluation(
                stop_audits=(_audit(scope="TASK", claimed=True),), censored_identities=("c1",)
            ),
            _trace(),
        )
        assert receipt.false_closure is FalseClosureKind.CENSORED_MATERIAL_OUTSTANDING
        assert receipt.premature_closure is True

    def test_refusing_closure_under_censoring_is_not_a_violation(self) -> None:
        """Refusing authority you do not have is the behaviour the paper claims."""

        receipt = build_task_receipt(
            _evaluation(
                stop_audits=(_audit(scope="TASK", claimed=False),), censored_identities=("c1",)
            ),
            _trace(),
        )
        assert receipt.kind is TaskClosureKind.REFUSED_OPEN_OBLIGATIONS
        assert receipt.false_closure is FalseClosureKind.NONE

    def test_a_non_closure_cannot_be_recorded_as_a_false_closure(self) -> None:
        with pytest.raises(ValueError, match="cannot be a false closure"):
            TaskClosureReceipt(
                system_id="s", task_id="t", seed=1,
                kind=TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM,
                false_closure=FalseClosureKind.REACHABLE_GOLD_OUTSTANDING,
                reason="r", still_reachable_at_closure=0,
                remaining_route_calls_at_closure=0, route_receipts=(),
            )


class TestRouteReceipts:
    def test_a_forced_abandonment_is_not_a_stopping_decision(self) -> None:
        with pytest.raises(ValueError, match="only a stop the system declared"):
            RouteClosureReceipt(
                route="r", kind=RouteClosureKind.ABANDONED_TRANSPORT_UNAVAILABLE,
                attempts=1, premature_stops=1, still_reachable_at_stop=0,
                remaining_route_calls_at_stop=0,
            )

    def test_not_attempted_cannot_carry_attempts(self) -> None:
        with pytest.raises(ValueError, match="contradicts"):
            RouteClosureReceipt(
                route="r", kind=RouteClosureKind.NOT_ATTEMPTED, attempts=2,
                premature_stops=0, still_reachable_at_stop=0, remaining_route_calls_at_stop=0,
            )

    def test_only_a_declared_stop_exercises_the_route_guard(self) -> None:
        exercising = [kind for kind in RouteClosureKind if kind.exercises_route_stop_guard]
        assert exercising == [RouteClosureKind.STOP_DECLARED]

    def test_a_route_never_touched_is_not_attempted(self) -> None:
        receipt = build_task_receipt(_evaluation(), _trace())
        assert {item.kind for item in receipt.route_receipts} == {RouteClosureKind.NOT_ATTEMPTED}


class TestLedgerDenominators:
    def _ledger(self, closures: int, violations: int, total: int) -> CampaignClosureLedger:
        receipts = []
        for position in range(total):
            closed = position < closures
            receipts.append(
                TaskClosureReceipt(
                    system_id="arm", task_id=f"t{position}", seed=1,
                    kind=(
                        TaskClosureKind.CLOSED_COMPLETE
                        if closed
                        else TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM
                    ),
                    false_closure=(
                        FalseClosureKind.REACHABLE_GOLD_OUTSTANDING
                        if closed and position < violations
                        else FalseClosureKind.NONE
                    ),
                    reason="r", still_reachable_at_closure=0,
                    remaining_route_calls_at_closure=0, route_receipts=(),
                )
            )
        return CampaignClosureLedger(campaign_id="c", receipts=tuple(receipts))

    def test_denominator_is_closures_not_tasks(self) -> None:
        exercise = self._ledger(closures=16, violations=0, total=20).false_closure_exercise("arm")
        assert (exercise.opportunities, exercise.violations) == (16, 0)

    def test_a_slice_with_no_closures_is_cannot_check(self) -> None:
        """The external Wide result, expressed through the shipped path."""

        exercise = self._ledger(closures=0, violations=0, total=24).false_closure_exercise("arm")
        assert exercise.exercised is False
        assert assess_guard(exercise).outcome is Outcome.CANNOT_CHECK

    def test_kind_counts_cover_every_receipt(self) -> None:
        ledger = self._ledger(closures=16, violations=3, total=20)
        assert sum(ledger.kind_counts("arm").values()) == 20
        assert sum(ledger.false_closure_kinds("arm").values()) == 20

    def test_duplicate_cells_are_rejected(self) -> None:
        one = self._ledger(closures=1, violations=0, total=1).receipts[0]
        with pytest.raises(ValueError, match="duplicate closure receipts"):
            CampaignClosureLedger(campaign_id="c", receipts=(one, one))

    def test_unknown_arm_raises(self) -> None:
        with pytest.raises(KeyError):
            self._ledger(closures=1, violations=0, total=1).false_closure_exercise("nope")


class TestAdmission:
    def _pair_ledger(self) -> CampaignClosureLedger:
        return CampaignClosureLedger(
            campaign_id="c",
            receipts=tuple(
                TaskClosureReceipt(
                    system_id=arm, task_id=task, seed=1,
                    kind=TaskClosureKind.CLOSED_COMPLETE,
                    false_closure=FalseClosureKind.NONE, reason="r",
                    still_reachable_at_closure=0, remaining_route_calls_at_closure=0,
                    route_receipts=(),
                )
                for arm in ("a", "b")
                for task in ("t1", "t2")
            ),
        )

    def test_a_complete_ledger_is_admissible(self) -> None:
        require_closure_receipts(
            self._pair_ledger(), expected_arms=["a", "b"], expected_task_ids=["t1", "t2"]
        )

    def test_a_missing_cell_blocks_outcome_access(self) -> None:
        """A cell nobody looked at is not a zero; admitting it shrinks the denominator."""

        ledger = CampaignClosureLedger(
            campaign_id="c", receipts=self._pair_ledger().receipts[:3]
        )
        with pytest.raises(OutcomesNotAdmissible, match="1 of 4 cells have no closure receipt"):
            require_closure_receipts(
                ledger, expected_arms=["a", "b"], expected_task_ids=["t1", "t2"]
            )

    def test_an_unregistered_arm_blocks(self) -> None:
        with pytest.raises(OutcomesNotAdmissible, match="unregistered arms or tasks"):
            require_closure_receipts(
                self._pair_ledger(), expected_arms=["a"], expected_task_ids=["t1", "t2"]
            )

    def test_an_empty_expectation_blocks(self) -> None:
        with pytest.raises(OutcomesNotAdmissible, match="non-empty expected arm"):
            require_closure_receipts(
                self._pair_ledger(), expected_arms=[], expected_task_ids=["t1"]
            )


class TestAgainstTheFrozenSystems:
    """Replayed rather than fixtured: the receipts must match real system behaviour."""

    def test_orion_declines_to_close_and_is_never_wrong_when_it_does(self) -> None:
        ledger = build_ledger("t", _replay("orion_full"))
        exercise = ledger.false_closure_exercise("orion_full")
        assert exercise.exercised is True
        assert exercise.opportunities < SLICE, "ORION must decline some closures"
        assert exercise.violations == 0
        assert assess_guard(exercise).outcome is Outcome.PASS

    def test_a_baseline_closes_everything_and_is_always_wrong(self) -> None:
        ledger = build_ledger("t", _replay("bm25_keyword"))
        exercise = ledger.false_closure_exercise("bm25_keyword")
        assert exercise.opportunities == SLICE
        assert exercise.violations == SLICE
        assert assess_guard(exercise).outcome is Outcome.FAIL

    def test_route_stopping_and_task_closure_separate(self) -> None:
        """#650's premise: these are different obligations and can disagree.

        ``bm25_keyword`` stops its single route without ever getting that stop
        wrong, and closes the task falsely every time. One number for both would
        report neither.
        """

        ledger = build_ledger("t", _replay("bm25_keyword"))
        assert assess_guard(ledger.route_stop_exercise("bm25_keyword")).outcome is Outcome.PASS
        assert assess_guard(ledger.false_closure_exercise("bm25_keyword")).outcome is Outcome.FAIL

    def test_non_inferiority_against_a_baseline_is_decidable_here(self) -> None:
        pairs = _replay("orion_full") + _replay("bm25_keyword")
        ledger = build_ledger("t", pairs)
        result = assess_non_inferiority(
            candidate=ledger.false_closure_exercise("orion_full"),
            comparator=ledger.false_closure_exercise("bm25_keyword"),
        )
        assert result.outcome is Outcome.PASS
        assert all(item.exercised for item in result.exercises)

    def test_every_replayed_task_lands_in_the_taxonomy(self) -> None:
        ledger = build_ledger("t", _replay("orion_full"))
        assert sum(ledger.kind_counts("orion_full").values()) == SLICE

    def test_admission_accepts_a_replayed_slice(self) -> None:
        _, tasks, _ = _suite()
        ledger = build_ledger("t", _replay("orion_full"))
        require_closure_receipts(
            ledger,
            expected_arms=["orion_full"],
            expected_task_ids=[task.task_id for task in tasks[:SLICE]],
        )

    def test_mismatched_evaluation_and_trace_are_rejected(self) -> None:
        evaluation, trace = _replay("orion_full", count=1)[0]
        with pytest.raises(ValueError, match="does not match"):
            build_task_receipt(evaluation, _trace(task_id="other", system_id=trace.system_id))


def test_task_stop_scope_constant_matches_the_study_vocabulary() -> None:
    """Pin the string the receipts filter on, so a rename cannot silently empty them."""

    assert StopScope.TASK.value == "TASK"
    assert StopScope.ROUTE.value == "ROUTE"
