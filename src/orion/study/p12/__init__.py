"""P12 instruments that make a handicapped baseline report as handicapped.

P12A's receipt reports a frozen two-signal allocation rule beating both "one-axis
adaptive" policies by 0.334717 at an identical two-unit budget. The budget is
identical and the arms' *action sets* are not: the winner may allocate any of
``(0,0) (1,1) (2,0) (0,2)`` and each baseline only two of them, so the baseline
fails every regime needing an allocation it cannot express, whatever its signal
says. Under a perfect signal ``ADAPTIVE_STATE_ONLY`` reaches 0.475464, below the
winner's achieved 0.858154 in 16 of 16 families.

:mod:`allocation_arms` re-implements the protected world --- reproducing every
published number to the bit --- with each arm's signals and allocations held in
separate fields, and runs the shipped gate battery against a capability-matched
baseline: one signal, same four allocations. The gain falls to 0.040771, the
worst family to 0.001953, and two of the seven gates flip, so the terminal
becomes ``P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET``.

:mod:`gate_theories` asks the other question, and it clears four of the seven
gates: the mean gain, the bootstrap bound, the ``FIXED_11`` margin and the worst
family all reject every declared wrong allocation rule. Three do not ---
``budget_respected`` is unsatisfiable, ``signals_pre_outcome_by_construction`` is
a literal, ``oracle_ceiling_holds`` compares against a rate that is always 1.0.

The mechanism itself is :mod:`orion.programme.attainable_margin`, which builds
its verdict from each arm's measured ceiling. The failure they close is recorded
under ``research/failures/2026-08-handicapped-baseline-unattainable-margin/``.
"""

from __future__ import annotations

from .allocation_arms import (
    ALL_ARMS,
    JOINT_OPTIONS,
    MATCHED_ARMS,
    NEGATIVE_TERMINAL,
    SHIPPED_ARMS,
    SHIPPED_REPLAY_SHA256,
    SHIPPED_SUMMARY,
    SHIPPED_TERMINAL,
    Arm,
    FamilyResult,
    arm_capability,
    gate_battery,
    run_families,
    summary,
)
from .gate_theories import (
    FALSE_THEORIES,
    GATE_IDS,
    STRUCTURALLY_UNFALSIFIABLE,
    baseline_signal_axis,
    measure_gate_capacities,
    reachable_allocations,
)

__all__ = [
    "ALL_ARMS",
    "FALSE_THEORIES",
    "GATE_IDS",
    "JOINT_OPTIONS",
    "MATCHED_ARMS",
    "NEGATIVE_TERMINAL",
    "SHIPPED_ARMS",
    "SHIPPED_REPLAY_SHA256",
    "SHIPPED_SUMMARY",
    "SHIPPED_TERMINAL",
    "STRUCTURALLY_UNFALSIFIABLE",
    "Arm",
    "FamilyResult",
    "arm_capability",
    "baseline_signal_axis",
    "gate_battery",
    "measure_gate_capacities",
    "reachable_allocations",
    "run_families",
    "summary",
]
