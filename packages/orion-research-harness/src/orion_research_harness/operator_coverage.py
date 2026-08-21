"""Which cycle operators a run actually executed.

``execution_coverage`` in this package answers a *static* question: does every
canonical mechanic have code that could run it? ``DIAGNOSE.v1`` resolves to
:class:`orion.engine.operators.diagnose.DiagnoseOperator`, so that check reports
ready. It does not, and cannot, tell you whether any particular run reached it.

That distinction is not academic. It is why this module exists.

The gap it closes
-----------------
The P1-U R6 campaign ran 48 episodes through this harness. Every run's operator
sequence was::

    RECURSE FRAME SEARCH ABSORB RECONSTRUCT DETECT RECURSE SATURATE_BOUNDED
    SEARCH ABSORB RECONSTRUCT DETECT RECURSE SATURATE_BOUNDED

``DIAGNOSE`` never appears. The solver reaches it only once per *material*
residual, and ``DetectOperator`` emitted none: each episode was encoded with one
candidate domain already searched and one claim already ``VERIFIED``, so no branch
of the detector could fire. The ablation arm that the campaign added specifically
to attribute its gain therefore returned ``UNRESOLVED`` on 48/48 episodes --- not
because the system was weak, but because that path was unreachable by
construction.

Nothing caught it. Static coverage said ready. The campaign asserted its trace
contained ``{FRAME, SEARCH, ABSORB, RECONSTRUCT}`` --- four operators, none of
them the one that was missing --- and passed. The result was fully receipted,
digest-bound and reproducible, and it could not support the claim it was built
for.

So a harness that lets a campaign say *which operators this arm must exercise*,
and fails loudly when one did not, is the mechanism that failure argues for.
:func:`require_operators_exercised` is that; it raises rather than returning
``False``, for the same reason ``orion.core.digests`` raises: a boundary error
that answers ``False`` is indistinguishable from a negative result.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

#: Every operator the recursive cycle can execute, in canonical order.
#: Mirrors :class:`orion.engine.cycle.CycleOperator` by value rather than by
#: import: this package is a host-side harness and does not take an engine
#: dependency for a list of ten strings. ``test_operator_coverage.py`` pins the
#: two together, so a new operator in the engine fails here rather than silently
#: dropping out of coverage.
CYCLE_OPERATORS: tuple[str, ...] = (
    "FRAME",
    "SEARCH",
    "ABSORB",
    "RECONSTRUCT",
    "DETECT",
    "DIAGNOSE",
    "REFRAME",
    "REOPEN",
    "RECURSE",
    "SATURATE_BOUNDED",
)


class OperatorNotExercised(RuntimeError):
    """A run did not execute an operator the caller required.

    Deliberately a ``RuntimeError`` and not a returned ``False``: the caller is
    about to score an arm that never ran the path it is meant to test, and that
    is a defect in the experiment rather than an outcome of it.
    """


def _sequence_of(outcome: object) -> tuple[str, ...]:
    """Pull the operator sequence out of a harness outcome, tolerantly.

    Accepts the outcome mapping :func:`orion_research_harness.runner.run_problem`
    returns, a bare sequence of operator names, or anything exposing
    ``operator_sequence``. Values may be plain strings or enum members.
    """

    raw: Any
    if isinstance(outcome, dict):
        raw = outcome.get("operator_sequence", ())
    elif isinstance(outcome, (list, tuple)):
        raw = outcome
    else:
        raw = getattr(outcome, "operator_sequence", ())
    return tuple(getattr(item, "value", item) for item in raw)


def run_operator_coverage(outcome: object) -> dict[str, Any]:
    """Report which cycle operators this run executed, and which it never did.

    ``never_executed`` is the interesting half. An operator absent from a single
    run is not by itself a defect --- ``REOPEN`` should not fire when nothing was
    invalidated --- which is exactly why this returns a report rather than a
    verdict. Only the caller knows which operators its experiment depends on.
    """

    sequence = _sequence_of(outcome)
    executed = [name for name in CYCLE_OPERATORS if name in sequence]
    unknown = sorted({name for name in sequence if name not in CYCLE_OPERATORS})
    counts = {name: sequence.count(name) for name in executed}
    return {
        "schema": "ORION.HarnessRunOperatorCoverage.v1",
        "operator_sequence": list(sequence),
        "executed": executed,
        "execution_counts": counts,
        "never_executed": [name for name in CYCLE_OPERATORS if name not in sequence],
        "unknown_operators": unknown,
        # A run is not required to exercise everything, and saying so here stops
        # a reader treating `never_executed` as a failure list.
        "grants_completeness": False,
    }


def require_operators_exercised(
    outcome: object,
    required: Iterable[str],
    *,
    label: str = "run",
) -> dict[str, Any]:
    """Return the coverage report, or raise naming exactly what never ran.

    Use this to guard an arm before scoring it::

        require_operators_exercised(outcome, {"DIAGNOSE"}, label="ORION_NATIVE_BASE")

    Had the R6 campaign written that line, its inert ablation would have failed on
    the first episode with the reason in the message, instead of producing 48
    scored rows whose comparison meant nothing.
    """

    required_names = tuple(dict.fromkeys(str(name) for name in required))
    unknown = [name for name in required_names if name not in CYCLE_OPERATORS]
    if unknown:
        raise OperatorNotExercised(
            f"{label}: not cycle operators: {', '.join(sorted(unknown))}; "
            f"known operators are {', '.join(CYCLE_OPERATORS)}"
        )

    coverage = run_operator_coverage(outcome)
    missing = [name for name in required_names if name not in coverage["executed"]]
    if missing:
        ran = ", ".join(coverage["executed"]) or "nothing"
        raise OperatorNotExercised(
            f"{label} never executed {', '.join(missing)}. It executed: {ran}. "
            "An arm that did not run the path it is meant to test cannot be scored "
            "against one that did."
        )
    return coverage


def compare_operator_coverage(
    outcomes: Sequence[tuple[str, object]],
) -> dict[str, Any]:
    """Compare arms, surfacing operators one ran and another did not.

    An ablation is only informative when the arms differ in the intended way. Two
    arms whose executed-operator sets are identical differ only in parameters; an
    arm missing an operator the other ran is not an ablation of it at all.
    """

    per_arm = {label: run_operator_coverage(outcome) for label, outcome in outcomes}
    executed = {label: set(report["executed"]) for label, report in per_arm.items()}
    shared = set.intersection(*executed.values()) if executed else set()
    union = set.union(*executed.values()) if executed else set()
    return {
        "schema": "ORION.HarnessArmOperatorComparison.v1",
        "arms": per_arm,
        "executed_by_all": sorted(shared),
        "executed_by_some": sorted(union - shared),
        "identical_operator_sets": len({frozenset(v) for v in executed.values()}) == 1,
    }


__all__ = [
    "CYCLE_OPERATORS",
    "OperatorNotExercised",
    "compare_operator_coverage",
    "require_operators_exercised",
    "run_operator_coverage",
]
