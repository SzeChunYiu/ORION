"""P14 instruments that make a predetermined negative report as predetermined.

P14A's benchmark computes its terminal from a live conjunction of seven gates
and publishes ``P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET``. Four of
those gates are true for every input, because the graded ORION arm is the gold
adjudication function itself; the two that fail are both the frequency of one
fact state out of 144, whose supremum over the protocol's own declared sampling
support is ``0.042326`` against thresholds of ``0.05`` and ``0.08``. Widen the
declared ranges --- and nothing else --- and the same emitter prints the positive
terminal.

:mod:`governance_gates` registers the shipped generator, the seven thresholds
and two registers of worlds: ones the freeze admits, for attainability, and ones
it does not, for capability. :mod:`gate_audit` runs them and blocks when a
terminal turns out to have had one reachable value. The mechanism itself is
:mod:`orion.programme.gate_attainability`, which builds its verdict from
:class:`orion.programme.guard_exercise.GuardExercise`.

The failure they close is recorded under
``research/failures/2026-08-unattainable-gate-predetermined-terminal/``.
"""

from __future__ import annotations

from .governance_gates import (
    ABLATION_ARMS,
    ARMS,
    BASELINE_ARMS,
    DISCRIMINATING_STATE,
    GATES,
    POSITIVE_TERMINAL,
    SHIPPED_RESULT_DIGEST,
    SHIPPED_SUPPORT,
    SHIPPED_TERMINAL,
    BenchInput,
    arm_error_states,
    baseline_error_nesting,
    bench,
    bench_responsiveness,
    capability_cases,
    contrast_axis_sensitivity,
    declared_worlds,
    discriminator_infimum,
    discriminator_supremum,
    gate_reaches,
    orion_arm_divergence,
    reachable_states,
    seed_sweep,
    shipped_bench,
    shipped_input,
    terminal_reach,
)

__all__ = [
    "ABLATION_ARMS",
    "ARMS",
    "BASELINE_ARMS",
    "DISCRIMINATING_STATE",
    "GATES",
    "POSITIVE_TERMINAL",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_SUPPORT",
    "SHIPPED_TERMINAL",
    "BenchInput",
    "arm_error_states",
    "baseline_error_nesting",
    "bench",
    "bench_responsiveness",
    "capability_cases",
    "contrast_axis_sensitivity",
    "declared_worlds",
    "discriminator_infimum",
    "discriminator_supremum",
    "gate_reaches",
    "orion_arm_divergence",
    "reachable_states",
    "seed_sweep",
    "shipped_bench",
    "shipped_input",
    "terminal_reach",
]
