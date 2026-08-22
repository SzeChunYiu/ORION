"""A criterion changed after the outcome may not carry a pass on its own word.

Why this module exists
----------------------

Two lanes on the ORION-QG wave-3 branch changed their own acceptance criterion
*after* seeing what the run produced:

* **QG-23** restricted its H1 criterion mid-lane. It disclosed the change, which
  is what made adjudication possible: the restriction turned out to be correct,
  because the passing pair's consumed support measure was 0/120 both before and
  after and the passing predictor was constant on all 120 instances.
* **QG-24** edited its verifier and then reported ACCEPT. The edit also turned
  out to be sound -- a fabricated passage still REJECTs under the changed rule.

Both were sound. Neither was *checked* by anything in this harness. Both were
caught by hand, by an adjudicator who happened to re-run the changed verifier
against a deliberately fabricated input. That is a mechanism with two instances
and no enforcement point, which is the same shape as the gap ``donor_search``
closed for novelty claims.

The specific hazard is narrow and worth stating precisely. Changing a criterion
is not misconduct; a protocol frozen before the outcome is frozen precisely so
that it can be found wrong. The hazard is a criterion changed in the direction
that produces a pass, where nothing establishes the changed criterion could
still have produced a failure. A rule that accepts everything accepts this too.

So: a **pass** reported under a criterion that differs from the frozen one must
carry the deviation, the verdict the frozen criterion would have given, and --
when the frozen criterion would have failed -- an exhibited demonstration that
the changed criterion still rejects something. A negative result under a changed
criterion is not gated: loosening or tightening a rule into a *failure* is not
the failure mode this module exists to catch.

Prior art, and why this docstring names it
------------------------------------------

None of this is new, and per ``donor_search`` the parent literature is named
rather than rediscovered. This module asserts no novelty.

* **HARKing** -- Kerr, "HARKing: Hypothesizing After the Results are Known"
  (*Personality and Social Psychology Review*, 1998) -- names outcome-dependent
  hypothesis revision presented as a prior prediction.
* **Researcher degrees of freedom** -- Simmons, Nelson & Simonsohn, "False-Positive
  Psychology" (*Psychological Science*, 2011) -- shows that undisclosed
  analysis-choice latitude alone suffices to manufacture a positive result.
* **Preregistration** -- Nosek et al., "The preregistration revolution" (*PNAS*,
  2018) -- and **Registered Reports** (Chambers, *Cortex*, 2013) -- are the
  established remedy: freeze the analysis plan, then report deviations against
  it. What this module implements is deviation *checking* against a frozen plan,
  which is preregistration discipline, not an invention.
* In the computational setting the same problem is **adaptive data analysis**:
  Dwork et al., "The reusable holdout" (*Science*, 2015) formalizes how reusing
  a held-out criterion after seeing results degrades its guarantee.

What is local to this repository is the enforcement point and the exhibited-
rejection requirement: preregistration reporting asks that deviations be
disclosed; this module additionally refuses a pass whose frozen criterion would
have failed unless the changed criterion is *shown* still capable of failing.

What this module does NOT do
----------------------------

It cannot tell whether a criterion change was scientifically justified. That is
an adjudication, and no predicate replaces it. It checks that the change is
disclosed, that the counterfactual verdict is on the record, and that the
loosened rule was demonstrated to still bite -- so an adjudicator is looking at
the right thing rather than discovering the change by accident.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

#: The reported outcome cleared the criterion. Gated by this module.
PASS = "PASS"

#: The reported outcome did not clear the criterion. Not gated: a criterion
#: change that yields a negative is not the failure mode named above.
FAIL = "FAIL"

#: The criterion could not be evaluated. Treated as a non-pass.
INDETERMINATE = "INDETERMINATE"

VERDICTS = frozenset({PASS, FAIL, INDETERMINATE})

#: Verdicts that assert the criterion was met. Only these are gated.
PASSING_VERDICTS = frozenset({PASS})


def criterion_digest(text: str) -> str:
    """Digest of a criterion's text, whitespace-normalized.

    Normalized so that reflowing a paragraph is not reported as a criterion
    change -- the check is about what the rule says, not how it was wrapped.
    Any change to the words changes the digest.
    """
    return hashlib.sha256(" ".join(str(text).split()).encode("utf-8")).hexdigest()


def validate_criterion_binding(
    record: Mapping[str, Any], frozen_criterion_text: str | None = None
) -> None:
    """Fail closed on a pass reported under an outcome-time criterion change.

    ``record`` describes one adjudicated criterion. It must always bind
    ``frozen_criterion_digest``, ``applied_criterion_digest`` and
    ``reported_verdict`` -- the absence of a change has to be asserted and
    checkable, never inferred from a missing key. Everything else is required
    only when a passing verdict is reported under a changed criterion.

    Pass ``frozen_criterion_text`` -- the criterion as it stands in the frozen
    protocol -- to have the bound digest checked against it rather than taken on
    the record's word.
    """
    if not isinstance(record, Mapping):
        raise TypeError("criterion-binding record must be an object")

    frozen_digest = record.get("frozen_criterion_digest")
    if not frozen_digest:
        raise ValueError(
            "every adjudicated criterion must bind frozen_criterion_digest. "
            "Without it, 'the criterion did not change' is an assertion rather "
            "than something a reader can check, and an undisclosed change is "
            "indistinguishable from no change."
        )

    if frozen_criterion_text is not None:
        actual = criterion_digest(frozen_criterion_text)
        if actual != frozen_digest:
            raise ValueError(
                "frozen_criterion_digest does not match the supplied frozen "
                f"criterion text (bound {frozen_digest!r}, computed {actual!r}). "
                "The record is bound to a criterion that is not the one in the "
                "frozen protocol."
            )

    verdict = record.get("reported_verdict")
    if verdict not in VERDICTS:
        raise ValueError(
            f"reported_verdict must be one of {sorted(VERDICTS)}; got {verdict!r}"
        )

    applied_digest = record.get("applied_criterion_digest")
    if not applied_digest:
        raise ValueError(
            "applied_criterion_digest is required, even when it equals "
            "frozen_criterion_digest. Defaulting a missing field to 'unchanged' "
            "would let the one record this module exists to catch -- a criterion "
            "quietly changed at outcome time -- clear the gate by omitting a "
            "key. Sameness must be asserted, not inferred from silence."
        )
    if applied_digest == frozen_digest:
        return

    if verdict not in PASSING_VERDICTS:
        return

    deviation = record.get("deviation")
    if not isinstance(deviation, Mapping):
        raise ValueError(
            "a PASS reported under a criterion that differs from the frozen one "
            "must carry a deviation record. QG-23 and QG-24 both changed their "
            "criteria and both changes were sound -- but each was adjudicable "
            "only because it was disclosed."
        )
    for field in ("description", "rationale"):
        if not str(deviation.get(field, "")).strip():
            raise ValueError(
                f"deviation.{field} is required on a PASS under a changed "
                "criterion: what changed, and why it changed for a reason that "
                "is not 'the frozen rule did not pass'."
            )

    counterfactual = record.get("verdict_under_frozen_criterion")
    if counterfactual not in VERDICTS:
        raise ValueError(
            "a PASS under a changed criterion must record "
            "verdict_under_frozen_criterion -- what the frozen rule would have "
            f"returned, one of {sorted(VERDICTS)}. This is the number a reader "
            "needs and the one a changed criterion makes disappear."
        )

    if counterfactual in PASSING_VERDICTS:
        return

    if not str(record.get("exhibited_rejection_ref", "")).strip():
        raise ValueError(
            "the frozen criterion would not have passed, so the changed "
            "criterion must bind exhibited_rejection_ref: a checkable "
            "demonstration that it still rejects something it should. A rule "
            "relaxed until the result clears it, with no exhibited rejection, "
            "is not evidence that the result is right -- it is evidence that "
            "the rule stopped discriminating. QG-24's changed verifier passed "
            "exactly this test by hand, on a fabricated passage; this makes the "
            "test a precondition instead of an adjudicator's good habit."
        )


def describe(verdict: str) -> str:
    """One line stating what a verdict does and does not establish."""
    if verdict == PASS:
        return (
            "criterion met as reported; gated by this module when the applied "
            "criterion differs from the frozen one"
        )
    if verdict == FAIL:
        return "criterion not met; not gated, a changed criterion yielding a negative is not the hazard"
    if verdict == INDETERMINATE:
        return "criterion could not be evaluated; treated as a non-pass, never as a pass"
    raise ValueError(f"unknown criterion verdict: {verdict}")
