"""What P12A's seven gates would have said if the allocation rule had been wrong.

``all(gates.values())`` is only as strong as the gates, so each of the seven is
registered here as a :class:`~orion.programme.refutation_capacity.MechanizedCheck`
whose ``accepts`` re-runs the whole 16-by-512 world with ``JOINT_FROZEN``
replaced by a candidate rule and returns that gate's boolean. Against a register
of six declared wrong allocation rules, three of the seven never move:

- ``budget_respected`` counts allocations with ``c + r > 2``. Every arm draws
  from ``{(0,0),(1,1),(2,0),(0,2)}`` and the oracle from the four requirements,
  which are the same four pairs; the maximum reachable sum is exactly 2, so the
  counter is unsatisfiable rather than zero.
- ``signals_pre_outcome_by_construction`` is the literal ``True``, written into
  the gate dict beside the computed ones. It is the protocol's clause 2 restated,
  not evaluated.
- ``oracle_ceiling_holds`` compares ``ORACLE_JOINT`` against ``JOINT_FROZEN``,
  and ``ORACLE_JOINT`` allocates the requirement itself, so its rate is 1.0 in
  every family for every world the runner can generate.

The remaining four --- the mean gain, the bootstrap lower bound, the margin over
``FIXED_11`` and the worst family --- reject all six wrong rules. P12A's numeric
gates are real gates; this module is what establishes that, and it is the reason
the paper's defect is not the one recorded for P8.

:func:`baseline_signal_axis` asks the second question. With the shipped
baseline's action set ``{(0,0),(2,0)}``, the nearest option is a function of
``s_c`` alone --- ``s_r`` cancels out of both squared distances --- so even a
policy that *reads* both signals allocates identically. Over the enumerated
signal grid the ``s_r`` axis changes 0 comparable sibling verdicts. "One axis
versus two" is not a contrast that can be run inside that action set at all.

The failure class is recorded under
``research/failures/2026-08-handicapped-baseline-unattainable-margin/``.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

import numpy as np

from orion.programme.refutation_capacity import (
    AxisSensitivity,
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    RefutationCapacity,
    axis_sensitivity,
    measure_refutation_capacity,
)
from orion.study.p12.allocation_arms import (
    JOINT_OPTIONS,
    REQUIREMENTS,
    SEED,
    Arm,
    gate_battery,
    nearest_option,
    run_families,
)

GATE_IDS: tuple[str, ...] = (
    "budget_respected",
    "signals_pre_outcome_by_construction",
    "mean_joint_gain_ge_0_15",
    "family_bootstrap_lower_gt_0",
    "mean_joint_minus_fixed_ge_0_10",
    "worst_family_joint_gain_ge_0_05",
    "oracle_ceiling_holds",
)

# The gates that are statements about the runner's own definitions. Named as data
# so a test can assert the measurement still finds exactly these three, rather
# than asserting a count that a new gate would silently satisfy.
STRUCTURALLY_UNFALSIFIABLE: frozenset[str] = frozenset(
    {"budget_respected", "signals_pre_outcome_by_construction", "oracle_ceiling_holds"}
)

# A grid rather than the sampled signals: refutation capacity is a question about
# the rule, and the sampled points are a property of one seed.
_GRID = tuple(float(value) for value in np.linspace(-1.0, 3.0, 21))
JOINT_SIGNAL_SPACE: tuple[ModelPoint, ...] = tuple(
    {"s_c": sc, "s_r": sr} for sc in _GRID for sr in _GRID
)

RESTRICTED_ACTIONS: tuple[tuple[int, int], ...] = ((0, 0), (2, 0))


def reference_rule(point: ModelPoint) -> tuple[int, int]:
    """The shipped ``JOINT_FROZEN`` allocation, as a rule over a signal point."""

    return nearest_option(float(point["s_c"]), float(point["s_r"]), JOINT_OPTIONS)


def _constant(allocation: tuple[int, int]) -> Callable[[ModelPoint], tuple[int, int]]:
    return lambda point: allocation


def _deaf_to_reasoning(point: ModelPoint) -> tuple[int, int]:
    return nearest_option(float(point["s_c"]), 0.0, JOINT_OPTIONS)


def _swapped_axes(point: ModelPoint) -> tuple[int, int]:
    return nearest_option(float(point["s_r"]), float(point["s_c"]), JOINT_OPTIONS)


def _farthest(point: ModelPoint) -> tuple[int, int]:
    sc, sr = float(point["s_c"]), float(point["s_r"])
    return max(
        ((sc - c) ** 2 + (sr - r) ** 2, index, (c, r))
        for index, (c, r) in enumerate(JOINT_OPTIONS)
    )[2]


FALSE_THEORIES: tuple[FalseTheory, ...] = (
    FalseTheory(
        theory_id="always_easy",
        breaks="denies that allocation should respond to the pre-outcome signals at all",
        rule=_constant((0, 0)),
    ),
    FalseTheory(
        theory_id="always_access",
        breaks="denies that the reasoning axis ever needs the budget",
        rule=_constant((2, 0)),
    ),
    FalseTheory(
        theory_id="always_fixed_11",
        breaks="denies that a frozen even split should ever be departed from",
        rule=_constant((1, 1)),
    ),
    FalseTheory(
        theory_id="deaf_to_reasoning_signal",
        breaks="denies that s_r carries allocation-relevant information",
        rule=_deaf_to_reasoning,
    ),
    FalseTheory(
        theory_id="swapped_axes",
        breaks="denies that each signal is bound to the axis it names",
        rule=_swapped_axes,
    ),
    FalseTheory(
        theory_id="anti_joint",
        breaks="denies that proximity to a requirement predicts that requirement",
        rule=_farthest,
    ),
)

_GATE_ASSERTIONS: Mapping[str, str] = {
    "budget_respected": "no arm allocated more than the two-unit budget on any item",
    "signals_pre_outcome_by_construction": "no signal reads a post-allocation outcome",
    "mean_joint_gain_ge_0_15": "mean joint gain over the best one-axis arm is at least 0.15",
    "family_bootstrap_lower_gt_0": "the family-block bootstrap lower bound is above 0",
    "mean_joint_minus_fixed_ge_0_10": "joint beats FIXED_11 by at least 0.10 on average",
    "worst_family_joint_gain_ge_0_05": "the worst family's joint gain is at least 0.05",
    "oracle_ceiling_holds": "the oracle scores at least as well as joint in every family",
}


def _joint_arm(rule: Callable[[ModelPoint], tuple[int, int]]) -> Arm:
    return Arm(
        arm_id="JOINT_FROZEN",
        signals_read=("s_c", "s_r"),
        allocations=JOINT_OPTIONS,
        allocate=lambda sc, sr: rule({"s_c": sc, "s_r": sr}),
    )


def gate_checks() -> tuple[MechanizedCheck, ...]:
    """Register each shipped gate as a check over the joint allocation rule.

    The seven checks share one cache of world replays, so substituting a theory
    costs one run of the 8,192-item world rather than seven. They are built
    together for that reason and must be measured together.
    """

    from orion.study.p12.allocation_arms import SHIPPED_ARMS

    others = tuple(arm for arm in SHIPPED_ARMS if arm.arm_id != "JOINT_FROZEN")
    cache: dict[Any, Mapping[str, bool]] = {}

    def gates_under(rule: Callable[[ModelPoint], tuple[int, int]]) -> Mapping[str, bool]:
        if rule not in cache:
            families = run_families(others + (_joint_arm(rule),))
            cache[rule] = gate_battery(families)["gates"]
        return cache[rule]

    return tuple(
        MechanizedCheck(
            check_id=gate_id,
            asserts=_GATE_ASSERTIONS[gate_id],
            accepts=lambda rule, gate_id=gate_id: bool(gates_under(rule)[gate_id]),
        )
        for gate_id in GATE_IDS
    )


def measure_gate_capacities(
    *, theories: Sequence[FalseTheory] = FALSE_THEORIES
) -> tuple[RefutationCapacity, ...]:
    """Measure, for every shipped gate, whether any wrong allocation rule fails it."""

    return tuple(
        measure_refutation_capacity(
            check,
            reference=reference_rule,
            reference_id="JOINT_FROZEN",
            theories=theories,
            space=JOINT_SIGNAL_SPACE,
        )
        for check in gate_checks()
    )


def baseline_signal_axis(axis: str = "s_r") -> AxisSensitivity:
    """Whether the shipped baseline's action set lets a second signal change anything.

    The rule given to :func:`~orion.programme.refutation_capacity.axis_sensitivity`
    is the *most* a one-axis arm could do with both signals: nearest option in
    ``{(0,0),(2,0)}``. If ``s_r`` is inert even for that rule, then
    ``ADAPTIVE_STATE_ONLY`` is not a policy that declines to use the second
    signal, it is a policy the second signal cannot reach.
    """

    return axis_sensitivity(
        axis,
        reference=lambda point: nearest_option(
            float(point["s_c"]), float(point["s_r"]), RESTRICTED_ACTIONS
        ),
        space=JOINT_SIGNAL_SPACE,
    )


def reachable_allocations() -> tuple[tuple[int, int], ...]:
    """Every allocation any shipped arm can emit, including the oracle's."""

    return tuple(sorted(set(JOINT_OPTIONS) | set(REQUIREMENTS.values())))


__all__ = [
    "FALSE_THEORIES",
    "GATE_IDS",
    "JOINT_SIGNAL_SPACE",
    "RESTRICTED_ACTIONS",
    "SEED",
    "STRUCTURALLY_UNFALSIFIABLE",
    "baseline_signal_axis",
    "gate_checks",
    "measure_gate_capacities",
    "reachable_allocations",
    "reference_rule",
]
