"""Tests for the criterion-churn gate.

The two lanes that motivated this module (QG-23, QG-24) both changed a criterion
and both changes were sound. These tests therefore have to be careful about
what they assert: the gate must let a disclosed, demonstrated change through,
and must refuse only the undisclosed or undemonstrated one.
"""

from __future__ import annotations

import pytest

from orion_research_harness.criterion_binding import (
    FAIL,
    INDETERMINATE,
    PASS,
    criterion_digest,
    describe,
    validate_criterion_binding,
)

FROZEN = "The predictor must be exactly correct on all 120 held-out instances."
FROZEN_D = criterion_digest(FROZEN)
CHANGED_D = criterion_digest(
    "The predictor must be exactly correct on the 47 instances with nonzero support."
)


def _record(**over):
    base = {
        "frozen_criterion_digest": FROZEN_D,
        "applied_criterion_digest": FROZEN_D,
        "reported_verdict": PASS,
    }
    base.update(over)
    return base


# --- the unchanged case -------------------------------------------------------


def test_unchanged_criterion_needs_nothing_further():
    validate_criterion_binding(_record())


def test_digest_is_whitespace_normalized_so_reflowing_is_not_a_change():
    reflowed = "The predictor must be exactly correct\non all 120  held-out instances."
    assert criterion_digest(reflowed) == FROZEN_D


def test_changing_a_single_word_changes_the_digest():
    assert criterion_digest(FROZEN.replace("all 120", "all 119")) != FROZEN_D


# --- the binding must exist at all -------------------------------------------


def test_missing_frozen_digest_is_refused():
    rec = _record()
    del rec["frozen_criterion_digest"]
    with pytest.raises(ValueError, match="frozen_criterion_digest"):
        validate_criterion_binding(rec)


def test_omitting_applied_digest_does_not_mean_unchanged():
    """The gate must not be clearable by leaving a key out.

    This is the shape of the bug that got through in ``donor_search`` -- a
    record that says nothing satisfying a check that assumed silence meant
    compliance.
    """
    rec = _record()
    del rec["applied_criterion_digest"]
    with pytest.raises(ValueError, match="applied_criterion_digest is required"):
        validate_criterion_binding(rec)


def test_bad_verdict_is_refused():
    with pytest.raises(ValueError, match="reported_verdict"):
        validate_criterion_binding(_record(reported_verdict="ACCEPT"))


def test_record_must_be_a_mapping():
    with pytest.raises(TypeError):
        validate_criterion_binding(["frozen_criterion_digest", FROZEN_D])


# --- digest checked against the real frozen text -----------------------------


def test_digest_is_checked_against_the_supplied_frozen_text():
    rec = _record(frozen_criterion_digest=CHANGED_D, applied_criterion_digest=CHANGED_D)
    with pytest.raises(ValueError, match="does not match the supplied frozen"):
        validate_criterion_binding(rec, FROZEN)


def test_matching_frozen_text_passes():
    validate_criterion_binding(_record(), FROZEN)


# --- the gated case ----------------------------------------------------------


def test_pass_under_a_changed_criterion_needs_a_deviation():
    with pytest.raises(ValueError, match="must carry a deviation record"):
        validate_criterion_binding(_record(applied_criterion_digest=CHANGED_D))


@pytest.mark.parametrize("field", ["description", "rationale"])
def test_deviation_must_say_what_and_why(field):
    dev = {"description": "restricted to nonzero-support instances", "rationale": "x"}
    dev[field] = "   "
    with pytest.raises(ValueError, match=f"deviation.{field}"):
        validate_criterion_binding(
            _record(applied_criterion_digest=CHANGED_D, deviation=dev)
        )


def test_pass_under_a_changed_criterion_needs_the_counterfactual():
    with pytest.raises(ValueError, match="verdict_under_frozen_criterion"):
        validate_criterion_binding(
            _record(
                applied_criterion_digest=CHANGED_D,
                deviation={"description": "d", "rationale": "r"},
            )
        )


def test_the_qg24_case_a_loosened_rule_must_be_shown_to_still_reject():
    """The exact record shape that motivated this module.

    A criterion was changed, the changed rule passes, the frozen rule would not
    have. Nothing here says the changed rule is wrong -- QG-24's was right. It
    says the record may not stop before exhibiting that the changed rule still
    rejects something.
    """
    rec = _record(
        applied_criterion_digest=CHANGED_D,
        deviation={
            "description": "verifier accepts a passage located under normalized whitespace",
            "rationale": "the frozen rule compared raw bytes and failed on line wrapping",
        },
        verdict_under_frozen_criterion=FAIL,
    )
    with pytest.raises(ValueError, match="exhibited_rejection_ref"):
        validate_criterion_binding(rec)

    rec["exhibited_rejection_ref"] = "QG24_GENERIC_VERIFICATION.json#fabricated_passage_rejected"
    validate_criterion_binding(rec)


def test_if_the_frozen_rule_would_also_have_passed_no_demonstration_is_owed():
    validate_criterion_binding(
        _record(
            applied_criterion_digest=CHANGED_D,
            deviation={"description": "d", "rationale": "r"},
            verdict_under_frozen_criterion=PASS,
        )
    )


# --- what is deliberately NOT gated ------------------------------------------


@pytest.mark.parametrize("verdict", [FAIL, INDETERMINATE])
def test_a_changed_criterion_yielding_a_negative_is_not_gated(verdict):
    """Loosening or tightening a rule into a failure is not the hazard.

    Gating negatives would penalize exactly the behaviour this programme wants:
    a lane that finds its own frozen criterion wrong and reports a worse result.
    """
    validate_criterion_binding(
        _record(applied_criterion_digest=CHANGED_D, reported_verdict=verdict)
    )


def test_indeterminate_is_never_treated_as_a_pass():
    assert "never as a pass" in describe(INDETERMINATE)


def test_describe_refuses_an_unknown_verdict():
    with pytest.raises(ValueError, match="unknown criterion verdict"):
        describe("ACCEPT")


def test_a_change_cannot_be_concealed_by_claiming_sameness():
    """Setting the applied digest equal to the frozen one is the cheapest bypass.

    A lane's own verifier ACCEPTed exactly this tampered receipt, which is how the
    hole was found: with the digests equal, none of the gated checks run at all.
    A record that claims sameness while carrying deviation fields is contradictory.
    """
    for field, value in (
        ("deviation", {"description": "d", "rationale": "r"}),
        ("verdict_under_frozen_criterion", FAIL),
        ("exhibited_rejection_ref", "somewhere#case"),
    ):
        with pytest.raises(ValueError, match="concealed"):
            validate_criterion_binding(_record(**{field: value}))


def test_an_honestly_unchanged_record_still_passes():
    validate_criterion_binding(_record(note="nothing changed"))
