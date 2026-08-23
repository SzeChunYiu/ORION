"""P12A's matched-budget arms, and the capability its "matched budget" does not match.

The shipped runner is
``papers/paper-12-adaptive-state-reasoning/run_p12a_matched_budget_v1.py``. It
generates 16 families of 512 items, each item drawn from one of four resource
regimes, and scores five allocation policies against a two-unit budget. Its
receipt reports ``mean_joint_gain_vs_best_one_axis = 0.334717`` and the terminal
``P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED``.

The world is re-implemented here rather than imported, because the paper
directory is a publication surface and this module has to survive its rebuilds.
The re-implementation is bound to the shipped artifact the only way that means
anything: it consumes the protected seed in the runner's own order and must
reproduce every number in :data:`SHIPPED_SUMMARY` exactly, which
``tests/unit/p12/test_p12_allocation_capability.py`` checks against the
committed receipt.

What the re-implementation adds is the arms' **action sets**, which the runner
holds implicitly in five lambda bodies and which the protocol never lists side by
side:

===========================  ==================================  ============
arm                          may allocate                        signals read
===========================  ==================================  ============
``FIXED_11``                 ``(1,1)``                           none
``ADAPTIVE_STATE_ONLY``      ``(0,0) (2,0)``                     ``s_c``
``ADAPTIVE_REASON_ONLY``     ``(0,0) (0,2)``                     ``s_r``
``JOINT_FROZEN``             ``(0,0) (1,1) (2,0) (0,2)``         ``s_c s_r``
===========================  ==================================  ============

Every arm respects the budget, so the protocol's "identical total budget" is
true and is not the constraint that separates them. The winner may express four
allocations and each baseline two, and the two the baselines lack are exactly the
ones the ``BOTH`` and the opposite-axis regimes require. Given a *perfect* signal
``ADAPTIVE_STATE_ONLY`` still scores 0.475464 against ``JOINT_FROZEN``'s achieved
0.858154.

:data:`MATCHED_ARMS` is the contrast the claim describes: policies that read one
signal and hold the same four allocations. Substituting them into the shipped
gate battery is the whole of the finding, and it is
:func:`gate_battery`'s job to make that a one-line change.

The failure class is recorded under
``research/failures/2026-08-handicapped-baseline-unattainable-margin/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from orion.programme.attainable_margin import ArmCapability, capability_from_cases

SEED = 2026082112
N_FAMILIES = 16
N_PER_FAMILY = 512
BUDGET = 2
BOOTSTRAP_RESAMPLES = 20000

REGIMES = ("EASY", "ACCESS", "REASON", "BOTH")
REQUIREMENTS: Mapping[str, tuple[int, int]] = {
    "EASY": (0, 0),
    "ACCESS": (2, 0),
    "REASON": (0, 2),
    "BOTH": (1, 1),
}
JOINT_OPTIONS: tuple[tuple[int, int], ...] = ((0, 0), (1, 1), (2, 0), (0, 2))

# Transcribed from P12A_MATCHED_BUDGET_RESULT_RECEIPT_V1.json. Pinned rather than
# read at import time so that a paper rebuild cannot quietly move the target this
# module reproduces; the test compares both directions.
SHIPPED_REPLAY_SHA256 = "0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947"
SHIPPED_TERMINAL = "P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED"
NEGATIVE_TERMINAL = "P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET"
SHIPPED_SUMMARY: Mapping[str, Any] = {
    "joint_success": 0.858154296875,
    "adaptive_state_only_success": 0.463134765625,
    "adaptive_reason_only_success": 0.4527587890625,
    "fixed_11_success": 0.5155029296875,
    "mean_joint_gain_vs_best_one_axis": 0.334716796875,
    "family_block_bootstrap_95ci": [0.2860076904296875, 0.38269348144531223],
    "worst_family_joint_gain": 0.158203125,
    "mean_joint_gain_vs_fixed_11": 0.3426513671875,
}


def satisfies(allocation: tuple[int, int], requirement: tuple[int, int]) -> bool:
    """P12A's verified success: the allocation covers the requirement on both axes."""

    return allocation[0] >= requirement[0] and allocation[1] >= requirement[1]


def nearest_option(sc: float, sr: float, options: Sequence[tuple[int, int]]) -> tuple[int, int]:
    """The runner's ``joint_alloc``: least squared distance, ties by option order."""

    return min(
        ((sc - c) ** 2 + (sr - r) ** 2, index, (c, r))
        for index, (c, r) in enumerate(options)
    )[2]


def _nearest_on_axis(
    signal: float, axis: int, options: Sequence[tuple[int, int]]
) -> tuple[int, int]:
    """Read one signal, then take the option that dominates on the axis not read.

    A policy restricted to one signal still knows that ``(0,2)`` covers every
    requirement ``(0,0)`` covers. Choosing the dominating option is what makes
    this a one-*signal* arm rather than a one-*axis* arm: it is the capability
    the shipped baselines lack, held constant while the signal count varies.
    """

    other = 1 - axis
    best = min(
        (abs(signal - option[axis]), index, option[axis])
        for index, option in enumerate(options)
    )[2]
    return max((option[other], option) for option in options if option[axis] == best)[1]


@dataclass(frozen=True)
class Arm:
    """One allocation policy, with the two things that distinguish it stated apart.

    ``signals_read`` is the variable P12A's claim names; ``allocations`` is the
    one it does not. Holding them in separate fields is the entire point of the
    record --- the runner encodes both inside a single lambda, where no reader
    and no gate can tell which of the two a margin came from.
    """

    arm_id: str
    signals_read: tuple[str, ...]
    allocations: tuple[tuple[int, int], ...]
    allocate: Callable[[float, float], tuple[int, int]]

    def __post_init__(self) -> None:
        if not self.allocations:
            raise ValueError(f"{self.arm_id}: an arm with no allocation can never succeed")
        over = [item for item in self.allocations if item[0] + item[1] > BUDGET]
        if over:
            raise ValueError(f"{self.arm_id}: allocations {over} exceed the {BUDGET}-unit budget")

    @property
    def capability_definition(self) -> str:
        allocations = " ".join(f"({c},{r})" for c, r in self.allocations)
        signals = ", ".join(self.signals_read) if self.signals_read else "none"
        return f"may allocate {allocations}; reads {signals}"

    def ceiling_definition(self) -> str:
        return (
            f"best score reachable by {self.arm_id}'s allocation set "
            f"{{{' '.join(f'({c},{r})' for c, r in self.allocations)}}} under a perfect "
            "signal, with the same items and the same two-unit budget"
        )


def _state_only(sc: float, sr: float) -> tuple[int, int]:
    return (2, 0) if sc >= 1.0 else (0, 0)


def _reason_only(sc: float, sr: float) -> tuple[int, int]:
    return (0, 2) if sr >= 1.0 else (0, 0)


SHIPPED_ARMS: tuple[Arm, ...] = (
    Arm("FIXED_11", (), ((1, 1),), lambda sc, sr: (1, 1)),
    Arm("ADAPTIVE_STATE_ONLY", ("s_c",), ((0, 0), (2, 0)), _state_only),
    Arm("ADAPTIVE_REASON_ONLY", ("s_r",), ((0, 0), (0, 2)), _reason_only),
    Arm(
        "JOINT_FROZEN",
        ("s_c", "s_r"),
        JOINT_OPTIONS,
        lambda sc, sr: nearest_option(sc, sr, JOINT_OPTIONS),
    ),
)

MATCHED_ARMS: tuple[Arm, ...] = (
    Arm(
        "STATE_SIGNAL_ONLY_MATCHED",
        ("s_c",),
        JOINT_OPTIONS,
        lambda sc, sr: _nearest_on_axis(sc, 0, JOINT_OPTIONS),
    ),
    Arm(
        "REASON_SIGNAL_ONLY_MATCHED",
        ("s_r",),
        JOINT_OPTIONS,
        lambda sc, sr: _nearest_on_axis(sr, 1, JOINT_OPTIONS),
    ),
)

ALL_ARMS: tuple[Arm, ...] = SHIPPED_ARMS + MATCHED_ARMS


@dataclass(frozen=True)
class FamilyResult:
    """One family's per-arm achieved rates beside the per-arm attainable ceilings."""

    family: int
    sigma: float
    achieved: Mapping[str, tuple[int, ...]]
    attainable: Mapping[str, tuple[int, ...]]
    budget_violations: int

    def rate(self, arm_id: str) -> float:
        scores = self.achieved[arm_id]
        return sum(scores) / len(scores)

    def ceiling(self, arm_id: str) -> float:
        scores = self.attainable[arm_id]
        return sum(scores) / len(scores)


def run_families(
    arms: Sequence[Arm] = ALL_ARMS, *, seed: int = SEED, sigma: float | None = None
) -> tuple[FamilyResult, ...]:
    """Replay the protected world, scoring each arm and its perfect-signal ceiling.

    The generator's draw order is reproduced exactly --- family sigma, Dirichlet
    prior, regime labels, then ``s_c`` and ``s_r`` per item --- because the claim
    under audit is a claim about *this* seed's numbers, and an instrument that
    lands on different ones cannot be pointed at the receipt.

    ``sigma`` overrides the per-family draw without changing the draw order, so
    signal quality can be swept while every other coordinate of the world holds.
    A genuine adaptation advantage shrinks as signals sharpen; P12A's grows.
    """

    rng = np.random.default_rng(seed)
    results: list[FamilyResult] = []
    for family in range(N_FAMILIES):
        drawn = float(rng.uniform(0.30, 0.80))
        raw = rng.dirichlet(np.ones(4))
        probs = 0.5 * raw + 0.5 * np.ones(4) / 4.0
        labels = rng.choice(4, size=N_PER_FAMILY, p=probs)
        achieved: dict[str, list[int]] = {arm.arm_id: [] for arm in arms}
        attainable: dict[str, list[int]] = {arm.arm_id: [] for arm in arms}
        violations = 0
        width = drawn if sigma is None else sigma
        for index in labels:
            requirement = REQUIREMENTS[REGIMES[int(index)]]
            sc = float(requirement[0] + rng.normal(0, width))
            sr = float(requirement[1] + rng.normal(0, width))
            for arm in arms:
                allocation = arm.allocate(sc, sr)
                if allocation[0] + allocation[1] > BUDGET:
                    violations += 1
                achieved[arm.arm_id].append(int(satisfies(allocation, requirement)))
                attainable[arm.arm_id].append(
                    int(any(satisfies(option, requirement) for option in arm.allocations))
                )
        results.append(
            FamilyResult(
                family=family,
                sigma=drawn,
                achieved={key: tuple(value) for key, value in achieved.items()},
                attainable={key: tuple(value) for key, value in attainable.items()},
                budget_violations=violations,
            )
        )
    return tuple(results)


def arm_capability(families: Sequence[FamilyResult], arm: Arm) -> ArmCapability:
    """The arm's achieved mean beside the ceiling its own action set imposes."""

    achieved: list[float] = []
    attainable: list[float] = []
    for family in families:
        achieved.extend(float(value) for value in family.achieved[arm.arm_id])
        attainable.extend(float(value) for value in family.attainable[arm.arm_id])
    return capability_from_cases(
        arm.arm_id,
        achieved_scores=achieved,
        ceiling_scores=attainable,
        capability_definition=arm.capability_definition,
        ceiling_definition=arm.ceiling_definition(),
    )


def _bootstrap_ci(gains: np.ndarray, *, seed: int) -> tuple[float, float]:
    """The runner's family-block bootstrap, resample order included."""

    rng = np.random.default_rng(seed + 991)
    draws = np.empty(BOOTSTRAP_RESAMPLES)
    for index in range(BOOTSTRAP_RESAMPLES):
        draws[index] = np.mean(gains[rng.integers(0, N_FAMILIES, size=N_FAMILIES)])
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def gate_battery(
    families: Sequence[FamilyResult],
    *,
    one_axis_arms: tuple[str, str] = ("ADAPTIVE_STATE_ONLY", "ADAPTIVE_REASON_ONLY"),
    seed: int = SEED,
) -> dict[str, Any]:
    """Run P12A's seven frozen gates, with the baseline pair as the only free choice.

    Everything else --- thresholds, comparators, the bootstrap, the terminal
    string --- is the shipped runner's. ``one_axis_arms`` is the single lever,
    because substituting a capability-matched baseline is the one perturbation
    the protocol's own words permit and its code does not express.
    """

    joint = np.array([family.rate("JOINT_FROZEN") for family in families])
    fixed = np.array([family.rate("FIXED_11") for family in families])
    best_one = np.array(
        [max(family.rate(one_axis_arms[0]), family.rate(one_axis_arms[1])) for family in families]
    )
    gains = joint - best_one
    fixed_gains = joint - fixed
    low, high = _bootstrap_ci(gains, seed=seed)
    oracle_holds = all(1.0 + 1e-12 >= family.rate("JOINT_FROZEN") for family in families)
    gates = {
        "budget_respected": sum(family.budget_violations for family in families) == 0,
        "signals_pre_outcome_by_construction": True,
        "mean_joint_gain_ge_0_15": float(np.mean(gains)) >= 0.15,
        "family_bootstrap_lower_gt_0": low > 0.0,
        "mean_joint_minus_fixed_ge_0_10": float(np.mean(fixed_gains)) >= 0.10,
        "worst_family_joint_gain_ge_0_05": float(np.min(gains)) >= 0.05,
        "oracle_ceiling_holds": oracle_holds,
    }
    return {
        "one_axis_arms": list(one_axis_arms),
        "mean_joint_gain": float(np.mean(gains)),
        "family_bootstrap_95ci": [low, high],
        "worst_family_joint_gain": float(np.min(gains)),
        "mean_joint_gain_vs_fixed_11": float(np.mean(fixed_gains)),
        "gates": gates,
        "terminal": SHIPPED_TERMINAL if all(gates.values()) else NEGATIVE_TERMINAL,
    }


def summary(families: Sequence[FamilyResult], *, seed: int = SEED) -> dict[str, Any]:
    """The receipt's summary block, recomputed, for comparison against the artifact."""

    battery = gate_battery(families, seed=seed)
    return {
        "joint_success": float(np.mean([family.rate("JOINT_FROZEN") for family in families])),
        "adaptive_state_only_success": float(
            np.mean([family.rate("ADAPTIVE_STATE_ONLY") for family in families])
        ),
        "adaptive_reason_only_success": float(
            np.mean([family.rate("ADAPTIVE_REASON_ONLY") for family in families])
        ),
        "fixed_11_success": float(np.mean([family.rate("FIXED_11") for family in families])),
        "mean_joint_gain_vs_best_one_axis": battery["mean_joint_gain"],
        "family_block_bootstrap_95ci": battery["family_bootstrap_95ci"],
        "worst_family_joint_gain": battery["worst_family_joint_gain"],
        "mean_joint_gain_vs_fixed_11": battery["mean_joint_gain_vs_fixed_11"],
    }


__all__ = [
    "ALL_ARMS",
    "BUDGET",
    "JOINT_OPTIONS",
    "MATCHED_ARMS",
    "NEGATIVE_TERMINAL",
    "N_FAMILIES",
    "N_PER_FAMILY",
    "REQUIREMENTS",
    "SEED",
    "SHIPPED_ARMS",
    "SHIPPED_REPLAY_SHA256",
    "SHIPPED_SUMMARY",
    "SHIPPED_TERMINAL",
    "Arm",
    "FamilyResult",
    "arm_capability",
    "gate_battery",
    "run_families",
    "nearest_option",
    "satisfies",
    "summary",
]
