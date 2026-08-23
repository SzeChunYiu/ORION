"""Harm rates that could not have differed from the arm that produced them.

A controlled comparison reports, per arm, how often a harm occurred. That number
is zero in two entirely different worlds: the arm was free to cause the harm and
did not, and the harm is a restatement of the arm's own decision rule. A rate
cannot tell them apart, so an arm scored against itself reads exactly like an arm
that survived pressure.

P13A is the live example. ``papers/paper-13-responsibility-carrying-state/
run_p13a_rcs_efficacy_v1.py`` decides the treatment arm's action with::

    if arm == "RCS":
        if supported:
            return "REUSE"
        return "REOPEN" if recover else "CANNOT_CHECK"

and scores the harm, inside the ``REUSE`` branch, with::

    local[arm]["unsafe"] += int(not supported)

One boolean, read twice. ``unsafe`` counts ``REUSE and not supported`` and the
arm reuses exactly when ``supported``, so the count is zero for any seed, any
family, any recovery probability and any certificate the compiler could issue ---
including a certificate that claims a responsibility the state cannot support.
The receipt publishes it as ``0.0`` over 12,288 episodes.

This is not :mod:`orion.programme.guard_exercise`'s failure with a new name. There
the denominator was zero because the campaign never reached the guarded state; a
different campaign would have pressed it. Here no campaign can, because the arm
and the metric are one predicate: the independent and the dependent variable are
the same variable. Nor is it :mod:`orion.programme.refutation_capacity`'s: that
module asks whether a *check*'s condition is satisfiable, and needs a check to
ask it of. A harm counter is not a check, and this one is satisfiable --- the
other arms satisfy it --- just never by the arm being credited.

The fix is to make the denominator a measured quantity rather than a supplied
one. A harm is **reachable** on an episode where it happens as shipped or would
happen under a registered alternative world, and a harm reachable on no episode
returns :data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which by
``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does. The rate a receipt
prints divides by the whole benchmark; this one divides by the episodes that
could have carried the harm, which is the number the claim needs.

The register is the artifact a reviewer audits, so a world must be one a reader
can read and agree is wrong, in the sense
:class:`orion.programme.refutation_capacity.FalseTheory` fixes for rules. Worlds
that leave every episode where it was are reported as inert rather than silently
counted, because a register of no-ops is exactly as vacuous as an empty one.

Two further counts are reported, because they separate two states a bare verdict
merges. ``outcome_contingent`` is how many episodes the registered worlds moved
the published value on; zero means the arm's rate is a restatement of its rule.
``action_contingent`` is how many they moved the arm's *own decision* on. An
outcome that stays constant while the action moves is the sharp signature of this
failure --- something the policy itself responded to left the published harm rate
untouched --- and it is the state an arm with a merely weak register cannot be in.
For P13A's RCS arm the registered wrong certificates move the action on 2,304 of
3,840 enumerated episodes and move ``unsafe_reuse`` on **0**.

Nothing here weakens a real result, and the P13A case shows why. Asked with a
denominator, the same benchmark supports a narrower claim that is genuinely
measured --- RCS returns a wrong answer on 0 of the 768 episodes where a reuse
could have returned one --- and it is the claim the evidence actually supports.

This module is scope-general. It knows nothing about responsibility, reuse or
P13; it takes a policy, an outcome, an episode space and a register of wrong
worlds, and returns a typed verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Hashable, Sequence

from orion.programme.guard_exercise import GuardAssessment, GuardExercise, assess_guard
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import ModelPoint

#: One arm's action on one episode. Opaque: an arm's vocabulary is its own.
Decision = Hashable


class EntailedOutcome(ValueError):
    """Raised when a harm rate is scored before anything could have moved it."""


@dataclass(frozen=True)
class ArmPolicy:
    """One arm's decision rule, as the audited artifact actually runs it.

    ``decides`` is required prose. An arm whose rule cannot be stated in a
    sentence cannot be compared against the outcome that scores it, and this
    failure is precisely a rule and a score that turn out to be the same
    sentence written twice.
    """

    arm_id: str
    decides: str
    action: Callable[[ModelPoint], Decision]

    def __post_init__(self) -> None:
        if not self.arm_id.strip():
            raise ValueError("an arm id is required")
        if not self.decides.strip():
            raise ValueError(
                f"{self.arm_id}: state what this arm decides; a rule nobody can read "
                "cannot be shown to differ from the metric that grades it"
            )


@dataclass(frozen=True)
class ReportedOutcome:
    """One quantity a receipt publishes per arm, as a predicate over an episode.

    ``holds`` takes the arm's decision as well as the episode because that is how
    a receipt computes a harm: inside the branch the arm chose. Passing the
    decision in is what lets the measurement notice when the branch and the
    predicate are the same test.
    """

    outcome_id: str
    measures: str
    holds: Callable[[ModelPoint, Decision], bool]

    def __post_init__(self) -> None:
        if not self.outcome_id.strip():
            raise ValueError("an outcome id is required")
        if not self.measures.strip():
            raise ValueError(
                f"{self.outcome_id}: state what this outcome measures; an unstated "
                "harm cannot be shown to have been avoidable"
            )


@dataclass(frozen=True)
class WorldVariant:
    """An alternative world the benchmark could have been run in, and why it is wrong.

    ``rewrite`` maps an episode to the same episode as it stands in that world.
    It rewrites the *episode* rather than the arm because the question is what
    the shipped arm does when the world is not the one it was written for --- and
    a wrong world cannot be expressed as a different sample from the right one.
    """

    world_id: str
    wrong: str
    rewrite: Callable[[ModelPoint], ModelPoint]

    def __post_init__(self) -> None:
        if not self.world_id.strip():
            raise ValueError("a world id is required")
        if not self.wrong.strip():
            raise ValueError(
                f"{self.world_id}: state what this world gets wrong; a variant nobody "
                "can see is wrong does not test anything by being survived"
            )


@dataclass(frozen=True)
class OutcomeEntailment:
    """A three-valued verdict on "this arm could have scored worse", with its register."""

    outcome_id: str
    arm_id: str
    points: int
    realized: int
    outcome_contingent: int
    action_contingent: int
    live_worlds: tuple[str, ...]
    inert_worlds: tuple[str, ...]
    exercise: GuardExercise

    def __post_init__(self) -> None:
        if self.points <= 0:
            raise ValueError(f"{self.outcome_id}: an empty episode space measures nothing")
        if not 0 <= self.realized <= self.points:
            raise ValueError(
                f"{self.outcome_id}/{self.arm_id}: {self.realized} realized harms is not "
                f"within {self.points} episodes"
            )
        for label, count in (
            ("with a moved decision", self.action_contingent),
            ("with a moved outcome", self.outcome_contingent),
        ):
            if not 0 <= count <= self.points:
                raise ValueError(
                    f"{self.outcome_id}/{self.arm_id}: {count} episodes {label} is not "
                    f"within {self.points} enumerated"
                )
        if self.outcome_contingent > 0 and not self.exercise.exercised:
            raise ValueError(
                f"{self.outcome_id}/{self.arm_id}: {self.outcome_contingent} episodes move "
                "the outcome but none could reach it; a value that changed was reachable"
            )

    @property
    def assessment(self) -> GuardAssessment:
        """Three-valued, with no tolerance: one avoidable harm is one too many."""

        return assess_guard(self.exercise, max_violation_rate=0.0)

    @property
    def outcome(self) -> Outcome:
        return self.assessment.outcome

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def entailed(self) -> bool:
        """True when no registered world moves this outcome for this arm.

        The published rate is then a function of the arm's decision rule, and
        would read the same for a benchmark of any size.
        """

        return self.outcome_contingent == 0

    @property
    def blind(self) -> bool:
        """Entailed, and the arm's own action did move.

        The sharp state: something the policy itself responded to left the
        published harm rate exactly where it was. An entailed outcome whose arm
        also never moved may simply have a weak register; this one cannot.
        """

        return self.entailed and self.action_contingent > 0

    @property
    def published_rate(self) -> float:
        """The rate the receipt prints: harms over the whole episode space.

        Kept beside :attr:`exercise` so the two denominators can be read
        together. This is the number that carries the claim, and on an entailed
        outcome it is an absent measurement wearing a real denominator's clothes.
        """

        return self.realized / self.points

    def as_json(self) -> dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "arm_id": self.arm_id,
            "outcome": self.outcome.value,
            "reason": self.assessment.reason.value,
            "detail": self.assessment.detail,
            "points": self.points,
            "realized": self.realized,
            "published_rate": self.published_rate,
            "outcome_contingent": self.outcome_contingent,
            "action_contingent": self.action_contingent,
            "entailed": self.entailed,
            "blind": self.blind,
            "live_worlds": list(self.live_worlds),
            "inert_worlds": list(self.inert_worlds),
            "exercise": self.exercise.as_json(),
        }


def measure_outcome_entailment(
    outcome: ReportedOutcome,
    *,
    policy: ArmPolicy,
    space: Sequence[ModelPoint],
    worlds: Sequence[WorldVariant],
) -> OutcomeEntailment:
    """Measure how many episodes this arm's published harm could have come out otherwise.

    The space is enumerated rather than sampled: reachability is a question about
    which episodes exist, not about how often the benchmark draws them, and an
    episode the sampler is unlikely to reach still carries a harm the arm could
    cause.

    A world that leaves every episode where it was is dropped from the register
    and reported as inert, exactly as ``measure_refutation_capacity`` drops a
    theory that never diverges from the reference.
    """

    if not space:
        raise ValueError(f"{outcome.outcome_id}: an empty episode space measures nothing")
    if not worlds:
        raise EntailedOutcome(
            f"{outcome.outcome_id}/{policy.arm_id}: no alternative world is registered, so "
            "the rate is a statement about the one world it was computed in"
        )

    baseline_decisions = [policy.action(point) for point in space]
    baseline_values = [
        outcome.holds(point, decision)
        for point, decision in zip(space, baseline_decisions)
    ]

    live: list[str] = []
    inert: list[str] = []
    action_moved = [False] * len(space)
    outcome_moved = [False] * len(space)
    # Reachable under the shipped world or under any registered one. This, not
    # the contingent set, is the guard's denominator: "how many episodes could
    # this arm have suffered this harm on" is the question a violation count
    # needs answered, and an episode where the harm is realized answers it
    # whether or not a different world would have changed it.
    reachable = list(baseline_values)
    for world in worlds:
        rewritten = [world.rewrite(point) for point in space]
        if all(dict(new) == dict(old) for new, old in zip(rewritten, space)):
            inert.append(world.world_id)
            continue
        live.append(world.world_id)
        for index, point in enumerate(rewritten):
            decision = policy.action(point)
            if decision != baseline_decisions[index]:
                action_moved[index] = True
            value = outcome.holds(point, decision)
            if value != baseline_values[index]:
                outcome_moved[index] = True
            reachable[index] = reachable[index] or value

    if not live:
        raise EntailedOutcome(
            f"{outcome.outcome_id}/{policy.arm_id}: all {len(worlds)} registered worlds "
            f"({', '.join(inert)}) leave every one of the {len(space)} episodes unchanged; "
            "the register cannot press anything"
        )

    exercise = GuardExercise(
        guard_id=outcome.outcome_id,
        arm_id=policy.arm_id,
        opportunities=sum(reachable),
        violations=sum(baseline_values),
        opportunity_definition=(
            f"episodes on which {policy.arm_id} suffers {outcome.outcome_id} as shipped or "
            f"would under at least one of the {len(live)} live registered worlds; "
            f"{outcome.measures}"
        ),
    )
    return OutcomeEntailment(
        outcome_id=outcome.outcome_id,
        arm_id=policy.arm_id,
        points=len(space),
        realized=sum(baseline_values),
        outcome_contingent=sum(outcome_moved),
        action_contingent=sum(action_moved),
        live_worlds=tuple(live),
        inert_worlds=tuple(inert),
        exercise=exercise,
    )


def require_contingent(entailments: Sequence[OutcomeEntailment], *, label: str) -> None:
    """Refuse to quote a harm rate before it could have been a different number.

    The comparison-side counterpart of ``require_refutable`` and
    ``require_operators_exercised``: it raises, naming the arm/outcome pairs no
    registered world can move, before any rate is read as evidence.
    """

    if not entailments:
        raise EntailedOutcome(f"{label}: an empty measurement set reports nothing")

    entailed = [item for item in entailments if item.entailed]
    violated = [item for item in entailments if item.outcome is Outcome.FAIL]
    if not entailed and not violated:
        return

    parts = []
    if entailed:
        blind = [item for item in entailed if item.blind]
        parts.append(
            f"{len(entailed)} of {len(entailments)} reported outcomes cannot move for their "
            f"arm ({', '.join(sorted(f'{i.outcome_id}/{i.arm_id}' for i in entailed))})"
        )
        if blind:
            parts.append(
                f"{len(blind)} of those moved the arm's own decision and not the outcome "
                f"({', '.join(sorted(f'{i.outcome_id}/{i.arm_id}' for i in blind))})"
            )
    if violated:
        parts.append(
            f"{len(violated)} caused an avoidable harm "
            f"({', '.join(sorted(f'{i.outcome_id}/{i.arm_id}' for i in violated))})"
        )
    raise EntailedOutcome(f"{label}: " + "; ".join(parts))


__all__ = [
    "ArmPolicy",
    "Decision",
    "EntailedOutcome",
    "OutcomeEntailment",
    "ReportedOutcome",
    "WorldVariant",
    "measure_outcome_entailment",
    "require_contingent",
]
