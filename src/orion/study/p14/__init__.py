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

:mod:`balanced_governance` points the same instrument at P14B, the first
successor, whose receipt publishes a **positive** terminal on eight gates all
``true``. That terminal survives the question: the four component ablations the
protocol registers, placed in the graded slot, make the conjunction print both
its words, which P14A's could not. What does not survive is the count. Four of
the eight gates are satisfied by every world the freeze admits ---
``full_discovery_recall_one`` because no registered policy can decline any of the
three fact states gold adjudicates as a promotion, ``matched_budget`` because the
runner writes one literal into all nine arms, and two preconditions for which
holding everywhere is the intended behaviour. So the receipt offers four readings
and four constants, and a reader counting eight pieces of evidence is counting
twice. Nothing frozen moves; P14B keeps its terminal, its numbers and its
standing non-authoritative downgrade.

:mod:`specification_conformance` carries the residual that record could not
discharge. It points the same instrument at P14C, the specification-separated
successor, over the coordinate P14C actually leaves free --- which of the seven
registered implementations sits in the graded slot --- and finds a conjunction
that prints two terminals rather than one. It then reads P14A's two failing
thresholds, ``0.05`` and ``0.08`` unchanged, on P14C's benchmark, where the same
statistic is ``0.142857`` instead of capped at ``0.042326``. Both are met. P14A
is not edited, re-run or relabelled by that; what it gains is the classification
its own protocol could not supply, that its terminal recorded an unmeasurable
gate rather than a result.
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
    threshold_panel,
    threshold_reaches,
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
    "threshold_panel",
    "threshold_reaches",
]
