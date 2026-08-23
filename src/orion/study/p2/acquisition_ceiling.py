"""What a retrieval arm could have scored, for gates the programme already has.

:mod:`orion.programme.gate_attainability` asks whether a frozen threshold lies
inside the reach of the statistic it reads, and
:mod:`orion.programme.attainable_margin` asks whether a comparison arm could
have competed at all. Both existed before this module. Neither needs replacing,
and this module deliberately does not restate them.

What they need and could not get for a retrieval benchmark is a **ceiling**.
:func:`~orion.programme.attainable_margin.capability_from_cases` takes
``ceiling_scores`` as given; :class:`~orion.programme.gate_attainability.StatisticSupport`
takes an infimum and a supremum as given. Somebody has to produce those numbers,
and for a search system the answer is not in the scores --- it is in what the
routes returned. That constructor is what this module is.

P2 is the worked example, and the honest part of the example is that the
programme could have caught it with machinery already on the shelf.

``P2_V2_WIDE_BOUNDED_MATCHED_RESULT_2026-08-18.json`` compared a route-governed
multiroute system against a single-route lexical baseline over 24
AutoResearchBench Wide tasks under a matched budget of three provider requests
per task, and returned ``BOUNDED_EXTERNAL_SIGNAL_NOT_POSITIVE`` because the
frozen rule wanted ``iou_delta >= 0.03`` and measured ``0.003687``.

The stage diagnostic beside it makes that a different statement. Across the
slice the answer key holds 229 gold identifiers. The governed system's routes
*acquired* 7 --- 3.06 per cent --- and 6 of those 7 survived into its submitted
set, so exactly one gold identifier was acquired-then-discarded. 222 of 229 were
never returned by any route at any point. Selection was not the binding
constraint; acquisition was.

That bounds the metric, because the scorer's IoU is a closed form in three
numbers (:func:`intersection_over_union`, checked against both published arms to
six decimals before it is trusted to bound anything). A selector cannot submit
what its routes never returned, so the arm's best attainable score is what it
scores having kept every gold identifier it did acquire: ``avg_iou`` 0.011260
against an observed 0.009958. The entire headroom a perfect selector could buy
is 0.0013.

Handed to :func:`~orion.programme.gate_attainability.assess_threshold_support`,
that support returns ``THRESHOLD_UNATTAINABLE``. Against the baseline's observed
0.006271 the largest attainable delta was 0.004989, short of 0.03 by 6.01x.
Conceding the baseline every point it scored, the largest attainable delta was
0.011260, short by 2.66x. No query derivation, no route-governance policy, no
selection rule and no conduct by the control could have produced a pass; the
rule demanded a summed per-task IoU of 0.8705 where the acquisition supported at
most 0.2702. A negative from such a rule is a measurement of the rule.

Not every threshold on that campaign was unreachable --- ``recall_delta >= 0.0``
was reachable and was met at ``+0.016369``. A ceiling that condemned every gate
it was pointed at would be the defect it exists to catch.

The cause of the low ceiling is the second half, and it is
:mod:`~orion.programme.attainable_margin`'s question --- arms differing in a way
the claim does not name --- instantiated for retrieval. The scorer's gold is an
arXiv identifier. Of the governed system's three routes, arXiv returned 7 gold
identifiers and OpenAIRE and DBLP returned 0 between them: not failures, since
all 72 requests came back OK carrying records, but records that do not carry an
identifier in the scheme the answer key is written in. The runner's own note for
both is ``no_arxiv_identifier_in_response``.

So ``matched_provider_requests_per_task: true`` was the wrong matching
predicate. Both arms spent three requests per task; the baseline spent all three
on the one route that can emit a scoring identifier and the governed arm spent
one, having divided its budget across three routes of which two could not score
by construction. The counts matched and the opportunity did not.
:func:`matched_exposure` is that predicate stated correctly: a route is
admissible only once *observed* to emit the answer key's scheme, and arms match
when their admissible exposure matches.

Both halves fail closed. Unmeasured acquisition is
:data:`~orion.programme.records.Outcome.CANNOT_CHECK`, never an assumed zero,
because "we did not record what the routes returned" and "the routes returned
nothing" are the two worlds this module exists to keep apart. An unprobed route
is :data:`RouteAdmissibility.UNPROBED` and blocks a matched-exposure claim
rather than being credited as admissible.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.programme.attainable_margin import ArmCapability
from orion.programme.gate_attainability import StatisticSupport
from orion.programme.records import Outcome

__all__ = [
    "ArmCeiling",
    "ExposureAccount",
    "RouteAdmissibility",
    "RouteEvidence",
    "TaskAcquisition",
    "arm_ceiling",
    "as_capability",
    "classify_route",
    "delta_support",
    "intersection_over_union",
    "matched_exposure",
]


def intersection_over_union(hits: int, gold: int, submitted: int) -> float:
    """The scorer's per-task set metric: ``|A n G| / |A u G|``.

    With ``hits`` of the submitted set correct, the union is
    ``submitted + gold - hits``. Verified against both published P2 arms: the
    per-task values summed and divided by 24 reproduce ``avg_iou`` 0.009958 and
    0.006271 exactly.
    """

    if hits < 0 or gold < 0 or submitted < 0:
        raise ValueError("hits, gold and submitted must be non-negative")
    if hits > gold or hits > submitted:
        raise ValueError(f"hits={hits} exceeds gold={gold} or submitted={submitted}")
    union = submitted + gold - hits
    return hits / union if union else 0.0


@dataclass(frozen=True)
class TaskAcquisition:
    """What one arm retrieved on one task, and what it did with it.

    ``acquired_gold`` is the count of answer-key identifiers the arm's routes
    *returned*, before any selection. ``None`` means the trace did not record it
    --- which is not zero, and which makes any ceiling over this task
    ``CANNOT_CHECK``.
    """

    task_id: str
    gold_count: int
    submitted: int
    scored_hits: int
    acquired_gold: int | None

    def __post_init__(self) -> None:
        if self.gold_count <= 0:
            raise ValueError(f"{self.task_id}: gold_count must be positive")
        if self.scored_hits > self.gold_count:
            raise ValueError(f"{self.task_id}: scored more gold than exists")
        if self.acquired_gold is not None and self.acquired_gold < self.scored_hits:
            raise ValueError(
                f"{self.task_id}: scored {self.scored_hits} gold it never acquired "
                f"({self.acquired_gold}) -- the trace is inconsistent, not merely thin"
            )

    @property
    def measured(self) -> bool:
        return self.acquired_gold is not None

    @property
    def attainable_hits(self) -> int:
        """Hits under a selector that keeps every gold identifier acquired.

        Capped by the submission size: a selector cannot submit more than the
        protocol lets it, so acquisition beyond ``submitted`` is not headroom.
        """

        if self.acquired_gold is None:
            raise ValueError(f"{self.task_id}: acquisition was not measured")
        return min(self.acquired_gold, self.gold_count, self.submitted)

    @property
    def discarded_gold(self) -> int:
        """Gold the routes returned and the selector did not submit."""

        return self.attainable_hits - self.scored_hits


@dataclass(frozen=True)
class ArmCeiling:
    """Observed score and the best score this arm's own retrieval permitted."""

    arm_id: str
    tasks: int
    gold_total: int
    acquired_total: int
    scored_total: int
    observed_iou: float
    ceiling_iou: float
    observed_recall: float
    ceiling_recall: float
    unmeasured_tasks: tuple[str, ...]

    @property
    def outcome(self) -> Outcome:
        return Outcome.CANNOT_CHECK if self.unmeasured_tasks else Outcome.PASS

    @property
    def never_acquired(self) -> int:
        """Gold no route returned at any point."""

        return self.gold_total - self.acquired_total

    @property
    def selection_headroom(self) -> float:
        """IoU a perfect selector would add. The whole of what selection can buy."""

        return self.ceiling_iou - self.observed_iou


def arm_ceiling(arm_id: str, tasks: Sequence[TaskAcquisition]) -> ArmCeiling:
    """Bound an arm's attainable score by what its routes actually returned.

    Fails closed: if any task's acquisition is unmeasured, the ceiling is
    computed over the measured tasks and the verdict is ``CANNOT_CHECK``, so a
    partial trace cannot be read as a proven bound.
    """

    if not tasks:
        raise ValueError("an arm ceiling needs at least one task")
    unmeasured = tuple(t.task_id for t in tasks if not t.measured)
    measured = [t for t in tasks if t.measured]
    n = len(tasks)

    observed_iou = sum(intersection_over_union(t.scored_hits, t.gold_count, t.submitted) for t in tasks) / n
    observed_recall = sum(t.scored_hits / t.gold_count for t in tasks) / n
    ceiling_iou = (
        sum(intersection_over_union(t.attainable_hits, t.gold_count, t.submitted) for t in measured) / n
    )
    ceiling_recall = sum(t.attainable_hits / t.gold_count for t in measured) / n

    return ArmCeiling(
        arm_id=arm_id,
        tasks=n,
        gold_total=sum(t.gold_count for t in tasks),
        acquired_total=sum(t.attainable_hits for t in measured),
        scored_total=sum(t.scored_hits for t in tasks),
        observed_iou=observed_iou,
        ceiling_iou=max(ceiling_iou, observed_iou),
        observed_recall=observed_recall,
        ceiling_recall=max(ceiling_recall, observed_recall),
        unmeasured_tasks=unmeasured,
    )


def _metric(ceiling: ArmCeiling, metric: str, which: str) -> float:
    if metric not in ("iou", "recall"):
        raise ValueError(f"unknown metric {metric!r}")
    return getattr(ceiling, f"{which}_{metric}")


def as_capability(ceiling: ArmCeiling, *, metric: str = "iou") -> ArmCapability:
    """Hand a retrieval arm to :mod:`orion.programme.attainable_margin`.

    The ceiling is the arm's capability in that module's sense: the score it
    reaches under the most favourable conduct of the part the claim is about
    (here, selection), holding fixed the part it is not (here, what the routes
    returned).
    """

    if ceiling.outcome is Outcome.CANNOT_CHECK:
        raise ValueError(
            f"{ceiling.arm_id}: acquisition unmeasured on "
            f"{len(ceiling.unmeasured_tasks)} task(s); a capability asserted over an "
            "unmeasured arm is the assumed zero this module exists to refuse"
        )
    return ArmCapability(
        arm_id=ceiling.arm_id,
        achieved=_metric(ceiling, metric, "observed"),
        ceiling=_metric(ceiling, metric, "ceiling"),
        capability_definition=(
            f"routes returned {ceiling.acquired_total} of {ceiling.gold_total} gold "
            f"identifiers across {ceiling.tasks} tasks; {ceiling.never_acquired} were "
            "never returned by any route"
        ),
        ceiling_definition=(
            f"avg_{metric} under a selector that submits every gold identifier the "
            "arm's routes returned, capped by the protocol's submission size"
        ),
    )


def delta_support(
    treatment: ArmCeiling,
    control: ArmCeiling,
    *,
    metric: str = "iou",
    concede_control: bool = False,
) -> StatisticSupport:
    """Bound ``treatment - control`` for :mod:`orion.programme.gate_attainability`.

    Two readings, because they answer different objections. By default the
    control is held at what it scored, which is the interval a re-run of the
    treatment could move within. With ``concede_control`` the control is granted
    every point it scored --- the most generous world the treatment could have
    been measured in --- and a threshold outside *that* interval is unreachable
    independent of anything either arm did.
    """

    if treatment.outcome is Outcome.CANNOT_CHECK:
        raise ValueError(
            f"{treatment.arm_id}: acquisition unmeasured, so the statistic has no "
            "derived support -- report CANNOT_CHECK rather than a bound"
        )
    ceiling = _metric(treatment, metric, "ceiling")
    control_score = 0.0 if concede_control else _metric(control, metric, "observed")
    basis = (
        "control conceded every point it scored"
        if concede_control
        else f"control held at its observed avg_{metric} of {control_score}"
    )
    return StatisticSupport(
        statistic=f"{metric}_delta",
        infimum=0.0 - control_score,
        supremum=ceiling - control_score,
        derivation=(
            f"{treatment.arm_id} acquisition ceiling: its routes returned "
            f"{treatment.acquired_total} of {treatment.gold_total} gold identifiers, "
            f"bounding avg_{metric} at {ceiling}; {basis}"
        ),
    )


# ---------------------------------------------------------------------------
# Why the ceiling was low: routes that cannot emit the answer key's identifiers
# ---------------------------------------------------------------------------


class RouteAdmissibility(str, Enum):
    """Can this route emit an identifier the scorer can match?"""

    #: Observed to return identifiers in the answer key's scheme.
    ADMISSIBLE = "ADMISSIBLE"
    #: Returned records, none carrying an identifier in the scheme.
    INADMISSIBLE = "INADMISSIBLE"
    #: Never probed against the scheme. Not evidence of either.
    UNPROBED = "UNPROBED"


@dataclass(frozen=True)
class RouteEvidence:
    """What a route was observed to return, against the scorer's identifier scheme."""

    route_id: str
    scheme: str
    records_returned: int
    records_carrying_scheme: int
    probed: bool = True

    def __post_init__(self) -> None:
        if self.records_carrying_scheme > self.records_returned:
            raise ValueError(f"{self.route_id}: more scheme-bearing records than records")


def classify_route(evidence: RouteEvidence) -> RouteAdmissibility:
    """A route earns admissibility by emitting the scheme, not by being configured.

    A route that returned nothing at all is ``UNPROBED``, not ``INADMISSIBLE``:
    an empty result is a fact about the query, and holding it against the route
    would convict a capable backend of a bad question.
    """

    if not evidence.probed or evidence.records_returned == 0:
        return RouteAdmissibility.UNPROBED
    if evidence.records_carrying_scheme > 0:
        return RouteAdmissibility.ADMISSIBLE
    return RouteAdmissibility.INADMISSIBLE


@dataclass(frozen=True)
class ExposureAccount:
    """How one arm spent its budget, split by whether the spend could score."""

    arm_id: str
    scheme: str
    requests_by_route: Mapping[str, int]
    admissibility: Mapping[str, RouteAdmissibility]

    @property
    def total_requests(self) -> int:
        return sum(self.requests_by_route.values())

    @property
    def admissible_requests(self) -> int:
        return sum(
            n
            for route, n in self.requests_by_route.items()
            if self.admissibility.get(route) is RouteAdmissibility.ADMISSIBLE
        )

    @property
    def inadmissible_requests(self) -> int:
        return sum(
            n
            for route, n in self.requests_by_route.items()
            if self.admissibility.get(route) is RouteAdmissibility.INADMISSIBLE
        )

    @property
    def unprobed_requests(self) -> int:
        return self.total_requests - self.admissible_requests - self.inadmissible_requests

    @property
    def scoring_eligible_fraction(self) -> float:
        return self.admissible_requests / self.total_requests if self.total_requests else 0.0


def matched_exposure(a: ExposureAccount, b: ExposureAccount) -> Outcome:
    """Are two arms matched on the spend that could produce a score?

    ``matched_provider_requests_per_task`` compares :attr:`total_requests`, which
    two arms can match while differing several-fold in
    :attr:`admissible_requests`. That is the P2 case: both arms spent 3 requests
    per task, the baseline spending 3 on an admissible route and the treatment
    spending 1, because 2 of its 3 routes could not emit a scoring identifier at
    all. Returns ``CANNOT_CHECK`` when either arm spent budget on a route whose
    admissibility was never probed --- an unprobed route could be either, and
    guessing is the failure this predicate exists to prevent.
    """

    if a.scheme != b.scheme:
        raise ValueError(f"arms scored against different schemes: {a.scheme!r} vs {b.scheme!r}")
    if a.unprobed_requests or b.unprobed_requests:
        return Outcome.CANNOT_CHECK
    return Outcome.PASS if a.admissible_requests == b.admissible_requests else Outcome.FAIL
