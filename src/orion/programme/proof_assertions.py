"""Assertions over proof results, kept out of the content-bound modules.

This helper began life inside :mod:`orion.programme.mechanized`, whose docstring
argues that proof reporting should live in one place rather than three times over.
That is the right home on the merits and the wrong one in practice: `mechanized.py`
is a bound execution input of ORION-16's P6 V4 replay contract, so adding a
function to it drifts the contract, the content manifest, the manifest's own
digest pin, and finally the paper's `subject_commit` -- which cannot be re-taken
until the change is on main. A test helper is not worth breaking a paper's
content binding for.

So it lives here, beside the module rather than inside it, and nothing binds this
file.
"""

from __future__ import annotations

from orion.programme.mechanized import ProofOutcome, ProofResult

__all__ = ["assert_all_discharged"]


def assert_all_discharged(results: "tuple[ProofResult, ...] | list[ProofResult]", *, what: str) -> None:
    """Fail on a refutation and on a timeout, but never confuse the two.

    ``discharged`` is ``PROVED``, so a solver that ran out of wall clock and a
    solver that found a countermodel both read as "not discharged", and an
    assertion on that property says only that a theorem is undischarged. One of
    those worlds is the claim being false; the other is a measurement that was
    not taken. :func:`discharge` already keeps them apart in the result it
    returns; this keeps them apart at the point a caller asserts on it.

    Both still fail. Nothing is weakened. The failure just says which world it is
    in, instead of leaving the next reader to guess -- and a timeout that reads as
    a refutation is how a slow CI runner silently retracts a theorem.

    Lifted from P8's private ``_assert_all_discharged``, which is where the
    pattern was first written and where it stayed while P6 and P7 grew their own
    host-speed-dependent assertions (#2011, #2020).
    """

    refuted = [r.theorem.name for r in results if r.outcome is ProofOutcome.COUNTEREXAMPLE]
    undecided = [r.theorem.name for r in results if r.outcome is ProofOutcome.UNKNOWN]

    assert refuted == [], (
        f"{what}: Z3 found a countermodel for {refuted}. This is a refutation, not a "
        "flake, and it does not go away by re-running."
    )
    assert undecided == [], (
        f"{what}: Z3 returned UNKNOWN for {undecided}. That is the prover giving up, "
        "not the theorem being lost -- these proofs complete well under a second on an "
        "unloaded machine, so UNKNOWN means the host was contended. Re-run before "
        "reading anything else into it."
    )
