"""Tests for the falsifiability gate.

Each of the three historical defects that motivated this module gets a test named
after it, so the suite says what it is defending rather than only that it passes.
"""

from __future__ import annotations

import pytest

from orion_research_harness.falsifiability import (
    validate_determinism,
    validate_falsifiability_demonstration,
)

EXPECTED = {
    "T1_headline_flipped": "terminal_consistent",
    "T2_distribution_shifted": "distribution_recomputed",
}


def _case(name, check, verdict="REJECT", resealed=True, failed=None):
    return {
        "case": name,
        "verdict": verdict,
        "result_digest_recomputed_so_copy_is_internally_self_consistent": resealed,
        "failed_checks": [check] if failed is None else failed,
    }


def _demo(*cases):
    return {"cases": list(cases)}


def test_a_clean_demonstration_passes():
    validate_falsifiability_demonstration(
        _demo(_case("T1_headline_flipped", "terminal_consistent"),
              _case("T2_distribution_shifted", "distribution_recomputed")),
        EXPECTED,
    )


def test_extra_failed_checks_are_fine_as_long_as_the_named_one_fired():
    validate_falsifiability_demonstration(
        _demo(_case("T1_headline_flipped", None,
                    failed=["terminal_consistent", "something_else"]),
              _case("T2_distribution_shifted", "distribution_recomputed")),
        EXPECTED,
    )


# --- the three historical defects -------------------------------------------


def test_the_qg24_t6_defect_a_tamper_the_verifier_simply_accepted():
    """T6 mutated a field the verifier does not read and was ACCEPTed."""
    with pytest.raises(ValueError, match="deliberately made wrong"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent", verdict="ACCEPT"),
                  _case("T2_distribution_shifted", "distribution_recomputed")),
            EXPECTED,
        )


def test_the_qg26_t9_defect_rejected_by_the_wrong_check():
    """The killing check was real but unrelated, so the named check stayed untested."""
    with pytest.raises(ValueError, match="still\\s+untested"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", None, failed=["some_other_check"]),
                  _case("T2_distribution_shifted", "distribution_recomputed")),
            EXPECTED,
        )


def test_a_case_with_no_declared_expectation_is_refused():
    """The QG-24 T5 defect: a tamper that found its target heuristically."""
    with pytest.raises(ValueError, match="declares no expected check"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent"),
                  _case("T99_undeclared", "whatever")),
            EXPECTED,
        )


# --- resealing ---------------------------------------------------------------


def test_an_unresealed_copy_proves_nothing():
    with pytest.raises(ValueError, match="hash mismatch rather than a re-derivation"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent", resealed=False),
                  _case("T2_distribution_shifted", "distribution_recomputed")),
            EXPECTED,
        )


def test_resealing_can_be_waived_explicitly_but_not_silently():
    validate_falsifiability_demonstration(
        _demo(_case("T1_headline_flipped", "terminal_consistent", resealed=False),
              _case("T2_distribution_shifted", "distribution_recomputed")),
        EXPECTED,
        require_resealed=False,
    )


# --- shape -------------------------------------------------------------------


def test_an_empty_demonstration_is_refused():
    with pytest.raises(ValueError, match="demonstrates nothing"):
        validate_falsifiability_demonstration({"cases": []}, EXPECTED)


def test_missing_cases_key_is_refused():
    with pytest.raises(ValueError, match="demonstrates nothing"):
        validate_falsifiability_demonstration({}, EXPECTED)


def test_declared_case_missing_from_the_suite_is_refused():
    """A case can be dropped from the runner while its expectation stays behind."""
    with pytest.raises(ValueError, match="not in the demonstration"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent")), EXPECTED
        )


def test_demonstration_must_be_a_mapping():
    with pytest.raises(TypeError):
        validate_falsifiability_demonstration([], EXPECTED)


def test_every_problem_is_reported_not_just_the_first():
    with pytest.raises(ValueError) as exc:
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", None, failed=["wrong"]),
                  _case("T2_distribution_shifted", "distribution_recomputed",
                        verdict="ACCEPT")),
            EXPECTED,
        )
    assert "T1_headline_flipped" in str(exc.value)
    assert "T2_distribution_shifted" in str(exc.value)


# --- determinism -------------------------------------------------------------


def test_determinism_must_actually_hold():
    with pytest.raises(ValueError, match="not byte-identical"):
        validate_determinism({"double_run": True, "stdout_identical": False})


def test_determinism_must_state_a_double_run_happened():
    with pytest.raises(ValueError, match="double run"):
        validate_determinism({"stdout_identical": True})


def test_a_held_determinism_record_passes():
    validate_determinism({"double_run": True, "stdout_identical": True})


# --- coverage: a check no tamper exercises is a stated gap, not a silent one ---


def test_a_check_no_tamper_exercises_must_be_named():
    """The decorative-check case: it survives precisely because nothing touches it."""
    with pytest.raises(ValueError, match="no tamper exercises"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent"),
                  _case("T2_distribution_shifted", "distribution_recomputed")),
            EXPECTED,
            all_checks=["terminal_consistent", "distribution_recomputed",
                        "a_check_nothing_tests"],
        )


def test_naming_the_gap_is_enough_because_some_checks_are_unexercisable_by_design():
    validate_falsifiability_demonstration(
        _demo(_case("T1_headline_flipped", "terminal_consistent"),
              _case("T2_distribution_shifted", "distribution_recomputed")),
        EXPECTED,
        all_checks=["terminal_consistent", "distribution_recomputed",
                    "result_digest_recomputes"],
        acknowledged_unexercised=["result_digest_recomputes"],
    )


def test_a_stale_acknowledgement_understates_coverage_and_is_refused():
    with pytest.raises(ValueError, match="out of date"):
        validate_falsifiability_demonstration(
            _demo(_case("T1_headline_flipped", "terminal_consistent"),
                  _case("T2_distribution_shifted", "distribution_recomputed")),
            EXPECTED,
            all_checks=["terminal_consistent", "distribution_recomputed"],
            acknowledged_unexercised=["terminal_consistent"],
        )


def test_coverage_is_not_checked_unless_all_checks_is_supplied():
    validate_falsifiability_demonstration(
        _demo(_case("T1_headline_flipped", "terminal_consistent"),
              _case("T2_distribution_shifted", "distribution_recomputed")),
        EXPECTED,
    )
