"""P8 instruments that make a self-issued authority verdict report as self-issued.

P8's anti-laundering receipt computed four rates and then published the string
``P8_P9_P10_ANTI_LAUNDERING_CLEAR``, which appeared nowhere in the computation
--- it was a literal in the dict beside them --- alongside a ``claim_ceiling``
copied from its own input. Replacing the graded authority table with one that
launders every capability into every coordinate made all seven named attacks
succeed and the block rate fall from 1.0 to 0.0, and the terminal did not move.

Repaired on 2026-08-21. The bench now derives its terminal from the four rates
through :mod:`orion.programme.guard_exercise`, so that same laundering table
publishes ``P8_P9_P10_ANTI_LAUNDERING_VIOLATED`` and a panel with an empty slice
publishes ``P8_P9_P10_ANTI_LAUNDERING_CANNOT_CHECK``; the shipped verdict is
still ``CLEAR`` because the shipped rates really are 1.0. The echoed bound is now
named ``declared_claim_ceiling_from_input``, which says where it came from
without pretending the run established it --- so the ceiling measurement below
still reports ``FAIL``, and the audit still blocks.

:mod:`authority_terminals` registers the shipped bench, its frozen panel and the
39,936-state X4 checker; :mod:`terminal_audit` runs them and blocks when a
verdict, a bound or an enumerated axis turns out not to be a function of the run.
The mechanism itself is :mod:`orion.programme.terminal_responsiveness`, which
builds its verdict from :class:`orion.programme.guard_exercise.GuardExercise`.

The failure they close is recorded under
``research/failures/2026-08-unconditional-terminal-self-issued-authority/``.
"""

from __future__ import annotations

from .authority_terminals import (
    BENCH_RATES,
    OVERREACHING_CEILING,
    SHIPPED_RESULT_DIGEST,
    SHIPPED_TERMINAL,
    BenchInput,
    bench_declared_ceiling,
    bench_emitter,
    bench_responsiveness,
    panel_gold_divergence,
    shipped_panel,
    shipped_summary,
    withholding_cases,
    x4_donor_axis,
)

__all__ = [
    "BENCH_RATES",
    "OVERREACHING_CEILING",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_TERMINAL",
    "BenchInput",
    "bench_declared_ceiling",
    "bench_emitter",
    "bench_responsiveness",
    "panel_gold_divergence",
    "shipped_panel",
    "shipped_summary",
    "withholding_cases",
    "x4_donor_axis",
]
