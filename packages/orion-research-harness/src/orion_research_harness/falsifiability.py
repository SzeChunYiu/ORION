"""A falsifiability demonstration must show the checks it claims to exercise.

Why this module exists
----------------------

Gate G7 across this programme's lanes requires that an independent verifier be
*demonstrated* capable of failing: tampered copies of a receipt, each with its
digest recomputed so no hash mismatch is available, each rejected by
re-derivation. Every lane implements it, and every lane checked the same thing --
that all the tampered copies were rejected.

That is not enough, and on 2026-08-22 it was not enough three times on one branch:

* QG-24's ``T6_g4_staging_violated`` mutated ``stage1.referee_calls_during_stage1``.
  The verifier reads ``q2_regime.prospective_forecast.referee_calls_during_stage1``.
  The copy was ACCEPTed outright.
* The same suite's ``T5`` located its target by searching for any key containing
  "hit". It found the right one by luck, and a case that finds its target
  heuristically demonstrates nothing about the check it is named after.
* QG-26's first ``T9`` changed the applied criterion digest *and* flipped the
  verdict to a negative. A negative under a changed criterion is deliberately not
  gated, so the churn gate cleared it and an unrelated consistency check produced
  the rejection -- leaving the hazard that gate exists for with no tamper at all,
  while the suite reported eleven-for-eleven.

The shape is one shape. **A tamper rejected by the wrong check leaves the check it
was meant to cover completely untested, while looking exactly like coverage.** The
count goes up, the artifact says "all rejected", and the reader has no way to see
the hole without reading every ``failed_checks`` list against every case name.

So a demonstration must bind, per case, the check that is expected to catch it,
and this module refuses the demonstration when any case is caught by a different
one. That converts an inspection into a precondition.

What this module does NOT do
----------------------------

It cannot tell whether the tampers chosen are the interesting ones; choosing what
to attack is judgement and no predicate replaces it. It checks that each attack
lands where it was aimed, that every copy was resealed so its rejection came from
re-derivation rather than a hash mismatch, and that nothing was quietly accepted.

Prior art, and why this docstring names it
------------------------------------------

Per ``donor_search``, the parent literature is named rather than rediscovered, and
this module asserts no novelty.

* **Mutation testing** -- DeMillo, Lipton & Sayward, "Hints on Test Data Selection"
  (*Computer*, 1978), and Hamlet, "Testing Programs with the Aid of a Compiler"
  (*IEEE TSE*, 1977) -- is exactly this practice: seed a fault, require the suite
  to detect it, and treat a surviving mutant as missing coverage. The refinement
  here, requiring the *specific* test to be the one that kills the mutant rather
  than any test, is the standard reading of a mutant "killed by" a test case.
* **Fault injection** for dependability assessment (Avizienis et al., "Basic
  Concepts and Taxonomy of Dependable and Secure Computing", *IEEE TDSC*, 2004)
  makes the same demand of a detector.
* The failure being guarded against -- a test that passes for a reason unrelated
  to what it was written to check -- is the classic **vacuous pass**, named in
  formal verification as vacuity detection (Beer et al., "Efficient Detection of
  Vacuity in Temporal Model Checking", *FMSD*, 2001).

What is local is the enforcement point: a receipt-level demonstration that refuses
to be written when a case does not kill the mutant it was aimed at.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

#: The verdict a tampered copy must receive.
REJECT = "REJECT"

#: The verdict a tampered copy must never receive. Present so the failure is
#: named rather than inferred from "not REJECT".
ACCEPT = "ACCEPT"


def validate_falsifiability_demonstration(
    demonstration: Mapping[str, Any],
    expected_check: Mapping[str, str],
    *,
    require_resealed: bool = True,
) -> None:
    """Fail closed on a demonstration that does not demonstrate what it claims.

    ``demonstration`` carries a ``cases`` list; each case has ``case`` (its name),
    ``verdict``, and ``failed_checks``. ``expected_check`` maps each case name to
    the check that must be among its ``failed_checks``.

    ``require_resealed`` demands each case record that its digest was recomputed.
    A tampered copy whose digest was left stale is rejected on the hash alone, so
    its rejection says nothing about whether the science re-derives -- which is
    the whole point of the exercise.
    """
    if not isinstance(demonstration, Mapping):
        raise TypeError("falsifiability demonstration must be an object")

    cases = demonstration.get("cases")
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)) or not cases:
        raise ValueError(
            "a falsifiability demonstration with no cases demonstrates nothing. "
            "G7 asks whether the verifier CAN fail; an empty suite answers a "
            "different and easier question."
        )

    problems: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping):
            problems.append(f"case {index} is not an object")
            continue
        name = case.get("case") or f"<unnamed case {index}>"

        verdict = case.get("verdict")
        if verdict != REJECT:
            problems.append(
                f"{name} was {verdict!r}, not {REJECT}: the verifier accepted a "
                "receipt that was deliberately made wrong"
            )
            continue

        if require_resealed and not case.get(
            "result_digest_recomputed_so_copy_is_internally_self_consistent"
        ):
            problems.append(
                f"{name} does not record that its digest was recomputed, so its "
                "rejection may be a hash mismatch rather than a re-derivation"
            )

        want = expected_check.get(name)
        if want is None:
            problems.append(
                f"{name} declares no expected check, so nothing establishes which "
                "check it exercises"
            )
            continue

        failed = case.get("failed_checks")
        if not isinstance(failed, Sequence) or isinstance(failed, (str, bytes)):
            problems.append(f"{name} has no failed_checks list")
            continue
        if want not in failed:
            problems.append(
                f"{name} was rejected by {list(failed)} but not by {want!r}, the "
                "check it exists to exercise -- that check is therefore still "
                "untested, and the suite's count conceals it"
            )

    unused = sorted(
        set(expected_check)
        - {c.get("case") for c in cases if isinstance(c, Mapping)}
    )
    if unused:
        problems.append(
            f"expected_check names cases that are not in the demonstration: "
            f"{unused}"
        )

    if problems:
        raise ValueError(
            "falsifiability demonstration rejected:\n  - " + "\n  - ".join(problems)
        )


def validate_determinism(determinism: Mapping[str, Any]) -> None:
    """Fail closed on a determinism claim that was recorded but not met.

    Gate G8 asks for a byte-identical double run. Recording ``stdout_identical:
    false`` and continuing is the same defect this module's docstring describes:
    an outcome computed and then not allowed to matter.
    """
    if not isinstance(determinism, Mapping):
        raise TypeError("determinism record must be an object")
    if not determinism.get("double_run"):
        raise ValueError("determinism record does not state that a double run happened")
    if not determinism.get("stdout_identical"):
        raise ValueError(
            "the double run was not byte-identical, so the determinism gate did "
            "not hold and the artifact must not claim it did"
        )
