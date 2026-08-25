"""Route-level and task-level closure receipts for the P2 campaign schema (#650).

Issue #650 asks for "route-level and task-level closure receipts" because
retrieval, inclusion, route stopping, provider validity and task-global closure
are different obligations and a campaign that reports one number for all of them
cannot say which one held. This module supplies the receipts and, more
importantly, the *denominator* they carry.

What went wrong without them
----------------------------
The V1 controlled campaign reports ``premature_task_closure_rate`` as a mean
over every task in the slice. ``gold._stop_audits`` sets ``premature = False``
for a task stop that did not claim completeness --- correctly, since prematurity
is a property of the claim --- so the rate is zero both when a system closed and
was right and when it never closed at all.

On the external Wide acquisition slice that difference decided the campaign.
``P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json`` reports, for both the
diversified candidate and the lexical baseline over 24 tasks::

    "tasks_closed_as_complete": 0,
    "tasks_with_open_obligations": 0,

Every task ended in a state the schema does not name: neither a closure nor a
declared obligation. Both arms therefore score zero false closures, and P2-U-T2
("simultaneous non-inferiority/superiority on false closure") would have read
that as parity. It is not parity. It is two empty sets.

The same measurement on the controlled world, taken with the receipts below,
comes out very differently and much better:

=================================  =========  =========  ============
system                             closures   false      guard
=================================  =========  =========  ============
``orion_full``                           260          0  PASS
``no_question_conditioned_read_ledger``  260          0  PASS
``no_content_identity_dedup``            192          0  PASS
``no_unavailable_route_open_state``      331         12  FAIL
``adaptive_multiroute_exploratory``      312        296  FAIL
``bm25_keyword``                         390        390  FAIL
``route_stop_can_close_task``            390        390  FAIL
external Wide, both arms                   0          0  CANNOT_CHECK
=================================  =========  =========  ============

ORION declines to close 130 of 390 tasks and is never wrong on the 260 it does
close. That is a strictly stronger statement than "rate 0.0", and it is the one
the receipts let the paper make.

The numerators are unchanged from ``RESULTS_SUMMARY_V1.json``'s
``failure_counts.premature_closure`` --- the ledger cross-checks every arm
against it --- so this is an accounting correction to the denominator, not a
re-measurement. ``no_unavailable_route_open_state`` is why
:class:`FalseClosureKind` exists: its 12 failures are all censored-material
closures, which never set ``StopAudit.premature``, so a receipt reading
prematurity alone scored that ablation a clean 0 against a published 12.

Design
------
Both taxonomies are *total*: every task and every route lands in exactly one
kind, so the state that swallowed 24 of 24 tasks has a name
(``STOPPED_WITHOUT_CLOSURE_CLAIM``) and is visible in the ledger rather than
absorbed into a zero. Only the kinds whose
``exercises_false_closure_guard`` / ``exercises_route_stop_guard`` is true enter
a guard's denominator, so a slice on which nothing closed produces a
``GuardExercise`` with zero opportunities and
:func:`orion.programme.guard_exercise.assess_guard` returns ``CANNOT_CHECK``.

This module reads evaluations and host traces, never gold. It consumes canonical
``StopDecision`` records plus the split evaluator route audits introduced by
#1078. The package boundary rule in
``orion.study.p2`` --- nothing but ``gold`` reads ``protected_gold`` --- holds.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from orion.programme.guard_exercise import GuardExercise

from .corpus import DiscoveryRoute
from .gold import Evaluation
from .systems import StopScope, SystemTrace, TransportStatus

FALSE_CLOSURE_GUARD_ID = "P2.FALSE_TASK_CLOSURE"
ROUTE_STOP_GUARD_ID = "P2.PREMATURE_ROUTE_STOP"

FALSE_CLOSURE_OPPORTUNITY = (
    "one task on which the system declared task-global completeness; a task the "
    "system never closed offers no opportunity to close it falsely"
)
ROUTE_STOP_OPPORTUNITY = (
    "one route the system itself declared stopped; a route abandoned because its "
    "transport died was not the system's stopping decision to get wrong"
)


class TaskClosureKind(str, Enum):
    """Total taxonomy of how a task run ended.

    ``STOPPED_WITHOUT_CLOSURE_CLAIM`` and ``NO_CLOSURE_DECISION`` are the two
    states that the V1 counters could not express. Both are legitimate ways for
    a run to end; neither is evidence that a closure guard held.
    """

    CLOSED_COMPLETE = "CLOSED_COMPLETE"
    REFUSED_OPEN_OBLIGATIONS = "REFUSED_OPEN_OBLIGATIONS"
    ABANDONED_BUDGET_EXHAUSTED = "ABANDONED_BUDGET_EXHAUSTED"
    ABANDONED_RUN_ERROR = "ABANDONED_RUN_ERROR"
    STOPPED_WITHOUT_CLOSURE_CLAIM = "STOPPED_WITHOUT_CLOSURE_CLAIM"
    NO_CLOSURE_DECISION = "NO_CLOSURE_DECISION"

    @property
    def exercises_false_closure_guard(self) -> bool:
        """Only a declared completeness claim can be a false closure."""

        return self is TaskClosureKind.CLOSED_COMPLETE

    @property
    def is_closure_claim(self) -> bool:
        return self is TaskClosureKind.CLOSED_COMPLETE


class FalseClosureKind(str, Enum):
    """Why a declared closure was false, or ``NONE`` if it was not.

    The host evaluator condemns a closure on two disjoint grounds, and merging
    them into one boolean loses the more interesting half. A closure taken with
    gold still reachable through a live route is a stopping-discipline error. A
    closure taken while material sits behind a route that *died* is an authority
    error: nothing was reachable, so no amount of further searching would have
    helped, and the correct response was to refuse closure rather than to keep
    paying. The second is the failure ``no_unavailable_route_open_state``
    ablates, and it never sets ``StopAudit.premature`` --- the audit's live-reach
    calculation excludes dead routes, so nothing is outstanding by its
    arithmetic. A receipt that read prematurity alone scored that ablation a
    clean pass on all 331 of its closures while the campaign's own status
    assignment failed it 12 times.

    Precedence follows ``gold._status_and_failure``: reachable-gold first, then
    censored material, so a receipt and a status can never disagree.
    """

    NONE = "NONE"
    REACHABLE_GOLD_OUTSTANDING = "REACHABLE_GOLD_OUTSTANDING"
    CENSORED_MATERIAL_OUTSTANDING = "CENSORED_MATERIAL_OUTSTANDING"

    @property
    def is_violation(self) -> bool:
        return self is not FalseClosureKind.NONE


class RouteClosureKind(str, Enum):
    """Total taxonomy of how one route ended within a task run."""

    STOP_DECLARED = "STOP_DECLARED"
    ABANDONED_TRANSPORT_UNAVAILABLE = "ABANDONED_TRANSPORT_UNAVAILABLE"
    LEFT_OPEN = "LEFT_OPEN"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"

    @property
    def exercises_route_stop_guard(self) -> bool:
        """A forced abandonment is transport's decision, not the system's."""

        return self is RouteClosureKind.STOP_DECLARED


@dataclass(frozen=True)
class RouteClosureReceipt:
    """What one route did on one task, and whether stopping it was premature."""

    route: str
    kind: RouteClosureKind
    attempts: int
    premature_stops: int
    still_reachable_at_stop: int
    remaining_route_calls_at_stop: int

    def __post_init__(self) -> None:
        if not self.route.strip():
            raise ValueError("route closure receipt requires a route")
        if self.attempts < 0 or self.premature_stops < 0:
            raise ValueError(f"{self.route}: counts cannot be negative")
        if not self.kind.exercises_route_stop_guard and self.premature_stops:
            raise ValueError(
                f"{self.route}: {self.kind.value} cannot carry a premature stop; "
                "only a stop the system declared can be judged premature"
            )
        if self.kind is RouteClosureKind.NOT_ATTEMPTED and self.attempts:
            raise ValueError(f"{self.route}: NOT_ATTEMPTED contradicts {self.attempts} attempts")

    def as_json(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "kind": self.kind.value,
            "attempts": self.attempts,
            "premature_stops": self.premature_stops,
            "still_reachable_at_stop": self.still_reachable_at_stop,
            "remaining_route_calls_at_stop": self.remaining_route_calls_at_stop,
        }


@dataclass(frozen=True)
class TaskClosureReceipt:
    """One (system, task, seed) cell's closure state, with its route receipts."""

    system_id: str
    task_id: str
    seed: int
    kind: TaskClosureKind
    false_closure: FalseClosureKind
    reason: str
    still_reachable_at_closure: int
    remaining_route_calls_at_closure: int
    route_receipts: tuple[RouteClosureReceipt, ...]

    def __post_init__(self) -> None:
        if not self.system_id.strip() or not self.task_id.strip():
            raise ValueError("closure receipt requires a system and a task identity")
        if self.false_closure.is_violation and not self.kind.exercises_false_closure_guard:
            raise ValueError(
                f"{self.system_id}/{self.task_id}: {self.kind.value} cannot be a false "
                "closure; falsity is a property of a completeness claim"
            )
        routes = [item.route for item in self.route_receipts]
        if len(routes) != len(set(routes)):
            raise ValueError(f"{self.system_id}/{self.task_id}: duplicate route receipts")

    @property
    def cell(self) -> tuple[str, str, int]:
        return (self.system_id, self.task_id, self.seed)

    @property
    def premature_closure(self) -> bool:
        return self.false_closure.is_violation

    @property
    def premature_route_stops(self) -> int:
        return sum(item.premature_stops for item in self.route_receipts)

    @property
    def declared_route_stops(self) -> int:
        return sum(1 for item in self.route_receipts if item.kind.exercises_route_stop_guard)

    def as_json(self) -> dict[str, Any]:
        return {
            "system_id": self.system_id,
            "task_id": self.task_id,
            "seed": self.seed,
            "kind": self.kind.value,
            "false_closure": self.false_closure.value,
            "reason": self.reason,
            "still_reachable_at_closure": self.still_reachable_at_closure,
            "remaining_route_calls_at_closure": self.remaining_route_calls_at_closure,
            "routes": [item.as_json() for item in self.route_receipts],
        }


class OutcomesNotAdmissible(RuntimeError):
    """Raised when campaign outcomes are read before every cell carries a receipt."""


def _route_receipt(
    route: DiscoveryRoute, evaluation: Evaluation, trace: SystemTrace
) -> RouteClosureReceipt:
    events = [item for item in trace.route_trials if item.route_id == route.value]
    unavailable = any(item.transport_status == TransportStatus.UNAVAILABLE.value for item in events)
    decisions = [
        item
        for item in trace.stop_decisions
        if item.scope == StopScope.ROUTE.value and item.route_id == route.value
    ]
    audits = [item for item in evaluation.route_stop_audits if item.route_id == route.value]

    if decisions:
        kind = RouteClosureKind.STOP_DECLARED
    elif unavailable:
        kind = RouteClosureKind.ABANDONED_TRANSPORT_UNAVAILABLE
    elif events:
        kind = RouteClosureKind.LEFT_OPEN
    else:
        kind = RouteClosureKind.NOT_ATTEMPTED

    last = audits[-1] if audits else None
    return RouteClosureReceipt(
        route=route.value,
        kind=kind,
        attempts=len(events),
        premature_stops=sum(1 for item in audits if item.false_positive),
        still_reachable_at_stop=last.residual_yield_at_stop if last else 0,
        remaining_route_calls_at_stop=last.remaining_query_budget if last else 0,
    )


def _task_kind(evaluation: Evaluation, trace: SystemTrace) -> tuple[TaskClosureKind, str]:
    task_stops = [
        item for item in trace.stop_decisions if item.scope == StopScope.TASK.value
    ]
    if not task_stops:
        return (
            TaskClosureKind.NO_CLOSURE_DECISION,
            "run ended without recording a task-scope stop",
        )

    decision = task_stops[-1]
    if decision.declared:
        return TaskClosureKind.CLOSED_COMPLETE, decision.reason
    if trace.error_class:
        return TaskClosureKind.ABANDONED_RUN_ERROR, trace.error_class
    if trace.truncated_at_cap:
        return TaskClosureKind.ABANDONED_BUDGET_EXHAUSTED, trace.truncated_at_cap
    # A refusal is only a refusal if something was actually left open. Ending
    # with nothing outstanding and no claim is a run that simply stopped, and
    # calling that a governed refusal would credit the mechanism for silence.
    if (
        evaluation.censored_ids
        or evaluation.task_residual_discoverable_within_budget
        or trace.unresolved_obligation_ids
    ):
        return TaskClosureKind.REFUSED_OPEN_OBLIGATIONS, decision.reason
    return TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM, decision.reason


def _false_closure_kind(
    evaluation: Evaluation, kind: TaskClosureKind
) -> FalseClosureKind:
    """Mirror ``gold._status_and_failure``'s two grounds, in its precedence.

    Kept as one function so the two disjuncts cannot drift apart, and so a reader
    checking this against the evaluator has a single place to look.
    """

    if not kind.exercises_false_closure_guard:
        return FalseClosureKind.NONE
    if evaluation.premature_closure:
        return FalseClosureKind.REACHABLE_GOLD_OUTSTANDING
    if evaluation.censored_ids or evaluation.closure_cannot_check:
        return FalseClosureKind.CENSORED_MATERIAL_OUTSTANDING
    return FalseClosureKind.NONE


def build_task_receipt(evaluation: Evaluation, trace: SystemTrace) -> TaskClosureReceipt:
    """Build one cell's receipt from the host evaluation and the host trace."""

    if (evaluation.task_id, evaluation.system_id) != (trace.task_id, trace.system_id):
        raise ValueError(
            f"evaluation {evaluation.system_id}/{evaluation.task_id} does not match "
            f"trace {trace.system_id}/{trace.task_id}"
        )

    kind, reason = _task_kind(evaluation, trace)
    task_stops = [
        item for item in trace.stop_decisions if item.scope == StopScope.TASK.value
    ]
    last = task_stops[-1] if task_stops else None
    used_route_calls = int(dict(evaluation.resources).get("query_count", 0))
    return TaskClosureReceipt(
        system_id=evaluation.system_id,
        task_id=evaluation.task_id,
        seed=evaluation.seed,
        kind=kind,
        false_closure=_false_closure_kind(evaluation, kind),
        reason=reason,
        still_reachable_at_closure=(
            evaluation.task_residual_discoverable_within_budget if last else 0
        ),
        remaining_route_calls_at_closure=(
            max(0, evaluation.max_route_calls - used_route_calls) if last else 0
        ),
        route_receipts=tuple(_route_receipt(route, evaluation, trace) for route in DiscoveryRoute),
    )


@dataclass(frozen=True)
class CampaignClosureLedger:
    """Every cell's receipt for one campaign, and the guard denominators it implies."""

    campaign_id: str
    receipts: tuple[TaskClosureReceipt, ...]

    def __post_init__(self) -> None:
        if not self.campaign_id.strip():
            raise ValueError("a closure ledger requires a campaign identity")
        cells = [item.cell for item in self.receipts]
        if len(cells) != len(set(cells)):
            raise ValueError(f"{self.campaign_id}: duplicate closure receipts for one cell")

    @property
    def arms(self) -> tuple[str, ...]:
        return tuple(sorted({item.system_id for item in self.receipts}))

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(sorted({item.task_id for item in self.receipts}))

    def for_arm(self, arm_id: str) -> tuple[TaskClosureReceipt, ...]:
        return tuple(item for item in self.receipts if item.system_id == arm_id)

    def kind_counts(self, arm_id: str) -> dict[str, int]:
        """Counts over the *total* taxonomy, so every cell is visible somewhere."""

        counted = Counter(item.kind.value for item in self.for_arm(arm_id))
        return {kind.value: counted.get(kind.value, 0) for kind in TaskClosureKind}

    def false_closure_kinds(self, arm_id: str) -> dict[str, int]:
        """Which ground condemned each false closure, so the two never merge."""

        counted = Counter(item.false_closure.value for item in self.for_arm(arm_id))
        return {kind.value: counted.get(kind.value, 0) for kind in FalseClosureKind}

    def false_closure_exercise(self, arm_id: str) -> GuardExercise:
        """The false-closure guard's denominator: closures claimed, not tasks run."""

        receipts = self.for_arm(arm_id)
        if not receipts:
            raise KeyError(f"{self.campaign_id}: no receipts for arm {arm_id}")
        return GuardExercise(
            guard_id=FALSE_CLOSURE_GUARD_ID,
            arm_id=arm_id,
            opportunities=sum(1 for item in receipts if item.kind.exercises_false_closure_guard),
            violations=sum(1 for item in receipts if item.premature_closure),
            opportunity_definition=FALSE_CLOSURE_OPPORTUNITY,
        )

    def route_stop_exercise(self, arm_id: str) -> GuardExercise:
        """The route-stop guard's denominator: stops declared, not routes touched."""

        receipts = self.for_arm(arm_id)
        if not receipts:
            raise KeyError(f"{self.campaign_id}: no receipts for arm {arm_id}")
        return GuardExercise(
            guard_id=ROUTE_STOP_GUARD_ID,
            arm_id=arm_id,
            opportunities=sum(item.declared_route_stops for item in receipts),
            violations=sum(item.premature_route_stops for item in receipts),
            opportunity_definition=ROUTE_STOP_OPPORTUNITY,
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": "orion.p2.closure-receipts.v1",
            "campaign_id": self.campaign_id,
            "arms": list(self.arms),
            "n_tasks": len(self.task_ids),
            "n_receipts": len(self.receipts),
            "by_arm": {
                arm: {
                    "task_closure_kinds": self.kind_counts(arm),
                    "false_closure_kinds": self.false_closure_kinds(arm),
                    "false_closure_exercise": self.false_closure_exercise(arm).as_json(),
                    "route_stop_exercise": self.route_stop_exercise(arm).as_json(),
                }
                for arm in self.arms
            },
        }


def build_ledger(
    campaign_id: str, pairs: Iterable[tuple[Evaluation, SystemTrace]]
) -> CampaignClosureLedger:
    return CampaignClosureLedger(
        campaign_id=campaign_id,
        receipts=tuple(build_task_receipt(evaluation, trace) for evaluation, trace in pairs),
    )


def require_closure_receipts(
    ledger: CampaignClosureLedger,
    *,
    expected_arms: Iterable[str],
    expected_task_ids: Iterable[str],
) -> None:
    """Refuse access to campaign outcomes until every cell carries a receipt.

    This is #650's "require route-level and task-level closure receipts", stated
    as a precondition rather than a report field. A missing cell is not a zero:
    it is a cell whose closure behaviour nobody looked at, and admitting it into
    an aggregate is how a denominator silently shrinks.
    """

    arms = tuple(dict.fromkeys(expected_arms))
    tasks = tuple(dict.fromkeys(expected_task_ids))
    if not arms or not tasks:
        raise OutcomesNotAdmissible(
            f"{ledger.campaign_id}: admission requires a non-empty expected arm and task set"
        )

    have = {(item.system_id, item.task_id) for item in ledger.receipts}
    missing = [(arm, task) for arm in arms for task in tasks if (arm, task) not in have]
    if missing:
        shown = ", ".join(f"{arm}/{task}" for arm, task in missing[:5])
        more = "" if len(missing) <= 5 else f" (+{len(missing) - 5} more)"
        raise OutcomesNotAdmissible(
            f"{ledger.campaign_id}: {len(missing)} of {len(arms) * len(tasks)} cells have no "
            f"closure receipt: {shown}{more}"
        )

    unexpected = sorted(
        {item.system_id for item in ledger.receipts} - set(arms)
        | {item.task_id for item in ledger.receipts} - set(tasks)
    )
    if unexpected:
        raise OutcomesNotAdmissible(
            f"{ledger.campaign_id}: receipts present for unregistered arms or tasks: "
            f"{', '.join(unexpected)}"
        )


__all__ = [
    "CampaignClosureLedger",
    "FALSE_CLOSURE_GUARD_ID",
    "FalseClosureKind",
    "OutcomesNotAdmissible",
    "ROUTE_STOP_GUARD_ID",
    "RouteClosureKind",
    "RouteClosureReceipt",
    "TaskClosureKind",
    "TaskClosureReceipt",
    "build_ledger",
    "build_task_receipt",
    "require_closure_receipts",
]
