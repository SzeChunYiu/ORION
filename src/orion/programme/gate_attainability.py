"""Preregistered gates that cannot report a negative the protocol could not have avoided.

A preregistered gate is a threshold and a statistic, and a receipt reports which
side of it the run landed on. That report is identical in two entirely different
worlds: the run measured the system and fell short of a bar it could have
cleared, and the bar was set above every value the frozen protocol's own
sampling support is able to produce. A serialized ``false`` cannot tell them
apart, so a benchmark whose gate was arithmetic before the seed was drawn reads
exactly like a benchmark that ran and lost.

P14A is the live example, measured both ways. ``papers/paper-14-orion-rse/
run_p14a_controlled_governance_v1.py`` computes its terminal from a live
conjunction --- it is not the P8 literal ---

.. code-block:: python

    terminal = "..._SUPPORTED" if all(gates.values()) else "..._GATE_NOT_MET"

and publishes ``P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`` on the two
gates that compare ``ORION_RSE_FULL`` against the strongest rule baseline. Both
of those gates read one number: the frequency of the single fact state, of the
144 the case generator can emit, on which ``MULTI_REVIEW`` and the full contract
disagree. Over the protocol's own declared sampling ranges that frequency has a
supremum of ``0.042326``, and the two thresholds are ``0.05`` and ``0.08``. The
shipped run reports ``0.018375``; 2,000 independent seeds of the frozen protocol
reach at most ``0.027750``; pinning every family at the extremal corner of every
declared range reaches ``0.040250``. The remaining five gates are true for every
admissible input, so ``all(gates.values())`` is ``False`` for every seed the
protocol permits and the terminal is a constant.

The instrument was not incapable in general: re-opening the declared sampling
ranges --- and nothing else, same seed, same arms, same thresholds, same terminal
expression --- takes the statistic to ``0.142250`` and the terminal to
``..._SUPPORTED``. That is the distinction this module exists to draw. The
verdict is a function of the run, which is all
:mod:`orion.programme.terminal_responsiveness` asks; the pass region simply lies
outside the set of runs the preregistration admits.

The failure class is recorded under
``research/failures/2026-08-unattainable-gate-predetermined-terminal/``.

This is the mirror of :mod:`orion.programme.refutation_capacity`, and both
directions matter for the same reason. There a check could not fail, so its pass
was a statement about its own definitions; here a gate cannot pass, so its
failure is a statement about the threshold rather than about the system. A gate
that cannot pass is worth exactly as much as a guard that cannot fail, and a
programme that treats published negatives as evidence has to measure both.

The fix is to make the reachable set part of the verdict's type. A gate is
exercised against a register of **admissible worlds** --- inputs a reader can
read and agree the frozen protocol permits --- and the verdict is three-valued:

* some admissible world satisfies the gate and some does not: the gate
  discriminates, :data:`~orion.programme.records.Outcome.PASS`;
* no admissible world satisfies it (``THRESHOLD_UNATTAINABLE``) or every one
  does (``THRESHOLD_UNCONDITIONAL``): :data:`~orion.programme.records.Outcome.FAIL`,
  with the margin by which the threshold sits outside reach;
* nothing was registered: :data:`~orion.programme.records.Outcome.CANNOT_CHECK`,
  which by ``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does.

Two constraints carry most of the weight.

``admits`` is required, for the same reason
:class:`orion.programme.guard_exercise.GuardExercise`'s
``opportunity_definition`` is. A world whose admissibility cannot be stated in a
sentence is a perturbation of the protocol, not a draw from it, and the whole
question here is which side of the freeze the input came from. Registering a
world the protocol does not admit turns an unattainable gate back into an
attainable one, so the register is the artifact a reviewer audits.

The terminal is asked separately from the gates, because per-gate attainability
does not compose. Seven individually reachable thresholds can still have no
world that clears all seven at once, and a conjunction that no admissible world
satisfies emits one word whatever the run does.
:func:`measure_terminal_reach` intersects the per-world readings rather than the
per-gate verdicts, so it answers the question the receipt's reader actually has:
how many distinct terminals this artifact was ever able to print.

Scope-general on purpose. It knows nothing about governance, benchmarks or P14;
it takes a statistic, a threshold and a register of admissible inputs, and
returns a typed verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Sequence

from orion.programme.guard_exercise import GuardAssessment, GuardExercise, assess_guard
from orion.programme.records import Outcome

#: A gate's statistic: the callable that turns one admissible input into the one
#: number the threshold is compared against.
#:
#: The quantity the shipped receipt publishes, not a proxy for it. An
#: attainability measured against a paraphrase of the statistic is a statement
#: about the paraphrase, which is the mistake
#: ``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/``
#: records about a second implementation that could not disagree with the first.
Statistic = Callable[[Any], float]

#: The arm label every attainability exercise carries. There is only one arm ---
#: a gate is not compared against a comparator gate --- but ``GuardExercise``
#: requires the field, and naming it keeps the emitted JSON readable.
DECLARED_ADMISSIBLE_WORLDS = "declared-admissible-worlds"


class UnattainableGate(ValueError):
    """Raised when a gate's verdict is read before the protocol could have moved it."""


class GateDirection(str, Enum):
    """Which side of the threshold satisfies the gate."""

    AT_LEAST = "AT_LEAST"
    AT_MOST = "AT_MOST"

    def satisfied(self, value: float, threshold: float) -> bool:
        if self is GateDirection.AT_LEAST:
            return value >= threshold
        return value <= threshold

    def margin(self, value: float, threshold: float) -> float:
        """Signed distance toward satisfaction: negative means the gate is not met.

        Reported rather than the raw difference so that ``AT_LEAST`` and
        ``AT_MOST`` gates roll up into one table without the reader having to
        remember which way each one points.
        """

        if self is GateDirection.AT_LEAST:
            return value - threshold
        return threshold - value


@dataclass(frozen=True)
class PreregisteredGate:
    """One frozen threshold, and the statistic the receipt compares against it.

    ``reads`` is required and must be non-empty. A threshold whose statistic
    cannot be named is a threshold nobody can check for reachability, and the
    P14A protocol that motivated this module states all seven of its gates in
    prose and none of them with the quantity's support.
    """

    gate_id: str
    reads: str
    threshold: float
    direction: GateDirection = GateDirection.AT_LEAST

    def __post_init__(self) -> None:
        if not self.gate_id.strip():
            raise ValueError("a gate id is required")
        if not self.reads.strip():
            raise ValueError(
                f"{self.gate_id}: state which statistic this gate reads; a threshold "
                "without a named quantity cannot be shown to be reachable"
            )

    def satisfied_by(self, value: float) -> bool:
        return self.direction.satisfied(value, self.threshold)

    def margin_of(self, value: float) -> float:
        return self.direction.margin(value, self.threshold)

    def as_json(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "reads": self.reads,
            "threshold": self.threshold,
            "direction": self.direction.value,
        }


@dataclass(frozen=True)
class AdmissibleWorld:
    """An input a reader can read and agree the frozen protocol permits.

    ``admits`` is required and must be non-empty for the same reason
    ``GuardExercise.opportunity_definition`` is: an attainability measured over
    inputs the preregistration excludes proves the wrong thing in the most
    flattering direction, and the sentence is what a reviewer checks.
    """

    world_id: str
    admits: str
    payload: Any

    def __post_init__(self) -> None:
        if not self.world_id.strip():
            raise ValueError("an admissible world id is required")
        if not self.admits.strip():
            raise ValueError(
                f"{self.world_id}: state why the frozen protocol admits this input; a "
                "world nobody can see is admissible widens the gate rather than measuring it"
            )


@dataclass(frozen=True)
class WorldReading:
    """The statistic in one admissible world, and which side of the gate it fell."""

    world_id: str
    value: float
    satisfied: bool
    margin: float

    def as_json(self) -> dict[str, Any]:
        return {
            "world_id": self.world_id,
            "value": self.value,
            "satisfied": self.satisfied,
            "margin": self.margin,
        }


class GateReachReason(str, Enum):
    """Why an attainability assessment came out the way it did.

    ``THRESHOLD_UNATTAINABLE`` and ``THRESHOLD_UNCONDITIONAL`` are the point of
    the module: they are the two states a published gate verdict renders as an
    indistinguishable boolean.
    """

    BOTH_OUTCOMES_REACHABLE = "BOTH_OUTCOMES_REACHABLE"
    THRESHOLD_UNATTAINABLE = "THRESHOLD_UNATTAINABLE"
    THRESHOLD_UNCONDITIONAL = "THRESHOLD_UNCONDITIONAL"
    NO_ADMISSIBLE_WORLD = "NO_ADMISSIBLE_WORLD"

    @property
    def is_vacuity(self) -> bool:
        """True for the reason that reports an absent register, not a result."""

        return self is GateReachReason.NO_ADMISSIBLE_WORLD


@dataclass(frozen=True)
class GateReach:
    """A three-valued verdict on "this gate could have gone either way", with its register."""

    gate: PreregisteredGate
    readings: tuple[WorldReading, ...]
    exercise: GuardExercise

    def __post_init__(self) -> None:
        if not self.readings:
            raise ValueError(
                f"{self.gate.gate_id}: a reach must carry the worlds it was measured over"
            )

    @property
    def satisfying(self) -> tuple[str, ...]:
        return tuple(item.world_id for item in self.readings if item.satisfied)

    @property
    def refuting(self) -> tuple[str, ...]:
        return tuple(item.world_id for item in self.readings if not item.satisfied)

    @property
    def attainable(self) -> bool:
        return bool(self.satisfying)

    @property
    def unconditional(self) -> bool:
        return not self.refuting

    @property
    def best_value(self) -> float:
        """The registered value closest to satisfying the gate.

        The headline number for an unattainable gate: paired with
        :attr:`attainment_margin` it says how far outside the protocol's reach
        the threshold was placed, which a boolean ``false`` does not.
        """

        return max(self.readings, key=lambda item: item.margin).value

    @property
    def attainment_margin(self) -> float:
        return self.gate.margin_of(self.best_value)

    @property
    def reason(self) -> GateReachReason:
        if not self.exercise.exercised:
            return GateReachReason.NO_ADMISSIBLE_WORLD
        if not self.attainable:
            return GateReachReason.THRESHOLD_UNATTAINABLE
        if self.unconditional:
            return GateReachReason.THRESHOLD_UNCONDITIONAL
        return GateReachReason.BOTH_OUTCOMES_REACHABLE

    @property
    def assessment(self) -> GuardAssessment:
        """The attainability half, as a guard: did any registered world satisfy the gate?

        The ceiling is "at least one satisfied" rather than "all satisfied"
        because a gate is supposed to reject some worlds --- that is what makes
        it a gate. Whether it rejects *every* world is the other half, and
        :attr:`outcome` is what carries it.
        """

        live = self.exercise.opportunities
        ceiling = (live - 1) / live if live else 0.0
        return assess_guard(self.exercise, max_violation_rate=ceiling)

    @property
    def outcome(self) -> Outcome:
        if self.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE:
            return Outcome.PASS
        if self.reason.is_vacuity:
            return Outcome.CANNOT_CHECK
        return Outcome.FAIL

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "gate": self.gate.as_json(),
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "best_value": self.best_value,
            "attainment_margin": self.attainment_margin,
            "satisfying": list(self.satisfying),
            "refuting": list(self.refuting),
            "readings": [item.as_json() for item in self.readings],
            "assessment": self.assessment.as_json(),
        }


def measure_gate_attainability(
    statistic: Statistic,
    *,
    gate: PreregisteredGate,
    worlds: Sequence[AdmissibleWorld],
) -> GateReach:
    """Measure whether any world the frozen protocol admits would have cleared this gate.

    ``worlds`` is the preregistration's own reachable set, not a fuzz corpus. The
    measurement is only as strong as that register covers the support: a gate
    reported attainable because somebody registered a world the protocol
    excludes has been widened, not measured.
    """

    if not worlds:
        raise UnattainableGate(
            f"{gate.gate_id}: no admissible world is registered, so nothing establishes "
            "the threshold was reachable and the gate's verdict is arithmetic"
        )
    ids = [world.world_id for world in worlds]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{gate.gate_id}: admissible world ids must be distinct")

    readings: list[WorldReading] = []
    for world in worlds:
        value = float(statistic(world.payload))
        readings.append(
            WorldReading(
                world_id=world.world_id,
                value=value,
                satisfied=gate.satisfied_by(value),
                margin=gate.margin_of(value),
            )
        )

    exercise = GuardExercise(
        guard_id=gate.gate_id,
        arm_id=DECLARED_ADMISSIBLE_WORLDS,
        opportunities=len(readings),
        violations=sum(1 for item in readings if not item.satisfied),
        opportunity_definition=(
            f"registered inputs the frozen protocol admits, scored on {gate.reads} against "
            f"{gate.direction.value} {gate.threshold}"
        ),
    )
    return GateReach(gate=gate, readings=tuple(readings), exercise=exercise)


@dataclass(frozen=True)
class TerminalReach:
    """A three-valued verdict on "this terminal has more than one word to say".

    Built by intersecting per-world readings rather than per-gate verdicts,
    because a conjunction of individually reachable gates can still be
    unsatisfiable in every world at once.
    """

    label: str
    reaches: tuple[GateReach, ...]

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("a terminal reach label is required")
        if not self.reaches:
            raise ValueError(f"{self.label}: a terminal with no gates is not a conjunction")
        registers = {tuple(item.world_id for item in reach.readings) for reach in self.reaches}
        if len(registers) != 1:
            raise ValueError(
                f"{self.label}: every gate must be measured over the same admissible worlds; "
                "intersecting readings taken in different worlds compares nothing"
            )

    @property
    def world_ids(self) -> tuple[str, ...]:
        return tuple(item.world_id for item in self.reaches[0].readings)

    @property
    def unattainable(self) -> tuple[str, ...]:
        return tuple(
            reach.gate.gate_id
            for reach in self.reaches
            if reach.reason is GateReachReason.THRESHOLD_UNATTAINABLE
        )

    @property
    def unconditional(self) -> tuple[str, ...]:
        return tuple(
            reach.gate.gate_id
            for reach in self.reaches
            if reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
        )

    @property
    def clearing(self) -> tuple[str, ...]:
        """Worlds in which every gate is satisfied --- the ones that reach the positive terminal."""

        return tuple(
            world
            for index, world in enumerate(self.world_ids)
            if all(reach.readings[index].satisfied for reach in self.reaches)
        )

    @property
    def distinct_terminals(self) -> int:
        """How many words the conjunction can emit over the register. One is the failure."""

        cleared = len(self.clearing)
        return 2 if 0 < cleared < len(self.world_ids) else 1

    @property
    def outcome(self) -> Outcome:
        if not self.world_ids:
            return Outcome.CANNOT_CHECK
        return Outcome.PASS if self.distinct_terminals > 1 else Outcome.FAIL

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "outcome": self.outcome.value,
            "distinct_terminals": self.distinct_terminals,
            "worlds": list(self.world_ids),
            "clearing_every_gate": list(self.clearing),
            "unattainable": list(self.unattainable),
            "unconditional": list(self.unconditional),
            "gates": [reach.as_json() for reach in self.reaches],
        }


def measure_terminal_reach(reaches: Sequence[GateReach], *, label: str) -> TerminalReach:
    """Roll per-gate readings up into "how many terminals could this artifact print"."""

    return TerminalReach(label=label, reaches=tuple(reaches))


def require_reachable(terminal: TerminalReach) -> None:
    """Raise unless the conjunction could have emitted either terminal.

    The point of call is before a terminal is read as a result. A negative from a
    conjunction with one reachable value is a property of the thresholds, and
    quoting it as a finding about the system is the failure this module records.
    """

    if not terminal.blocks:
        return
    parts = [f"{terminal.label}: the terminal has {terminal.distinct_terminals} reachable value"]
    if terminal.unattainable:
        parts.append(f"no admissible world satisfies {', '.join(terminal.unattainable)}")
    if terminal.unconditional:
        parts.append(f"every admissible world satisfies {', '.join(terminal.unconditional)}")
    if not terminal.clearing:
        parts.append("no registered world clears every gate at once")
    raise UnattainableGate("; ".join(parts))


__all__ = [
    "DECLARED_ADMISSIBLE_WORLDS",
    "AdmissibleWorld",
    "GateDirection",
    "GateReach",
    "GateReachReason",
    "PreregisteredGate",
    "Statistic",
    "TerminalReach",
    "UnattainableGate",
    "WorldReading",
    "measure_gate_attainability",
    "measure_terminal_reach",
    "require_reachable",
]
