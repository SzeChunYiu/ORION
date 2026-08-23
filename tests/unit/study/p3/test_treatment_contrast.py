"""An ablation arm whose treatment was the identity must not report a null.

The regression these pin is ``research/failures/
2026-08-unapplied-treatment-vacuous-null/``: two P3 ablation arms report
``0.0 [0.0, 0.0]`` --- the tightest null an experiment can print --- while their
treatment altered 0 of 32 cases.
"""

from __future__ import annotations

import pytest

from orion.programme.records import Outcome
from orion.study.p3.treatment_contrast import (
    InertAblation,
    NecessityAssessment,
    NecessityVerdictReason,
    TreatmentContrast,
    assess_coordinate_necessity,
    contrast_from_runs,
    require_treatment_applied,
)

TREATMENT = "the coordinate under test emptied on both sides"


def _contrast(**overrides: object) -> TreatmentContrast:
    fields: dict[str, object] = {
        "arm_id": "remove_measurement",
        "cases": 32,
        "cases_treated": 0,
        "decisions_changed": 0,
        "treatment_definition": TREATMENT,
    }
    fields.update(overrides)
    return TreatmentContrast(**fields)  # type: ignore[arg-type]


class TestTreatmentContrast:
    def test_untreated_arm_reports_no_effect_rate_rather_than_zero(self) -> None:
        contrast = _contrast()
        assert contrast.applied is False
        assert contrast.effect_rate is None
        assert contrast.resolution is None
        assert contrast.treatment_rate == 0.0

    def test_treated_arm_reports_effect_and_resolution(self) -> None:
        contrast = _contrast(arm_id="remove_construct", cases_treated=19, decisions_changed=0)
        assert contrast.applied is True
        assert contrast.effect_rate == 0.0
        assert contrast.resolution == pytest.approx(1 / 19)

    def test_treatment_definition_is_required(self) -> None:
        with pytest.raises(ValueError, match="treatment definition is required"):
            _contrast(treatment_definition="   ")

    def test_effect_cannot_exceed_the_treated_set(self) -> None:
        with pytest.raises(ValueError, match="varies something it does not declare"):
            _contrast(cases_treated=2, decisions_changed=3)

    def test_treated_cannot_exceed_scored(self) -> None:
        with pytest.raises(ValueError, match="exceeds"):
            _contrast(cases=4, cases_treated=5)

    def test_zero_case_arm_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="zero cases"):
            _contrast(cases=0)

    def test_json_carries_the_denominator(self) -> None:
        payload = _contrast(cases_treated=19, decisions_changed=6).as_json()
        assert payload["cases_treated"] == 19
        assert payload["treatment_definition"] == TREATMENT
        assert payload["applied"] is True


class TestAssessCoordinateNecessity:
    def test_unapplied_treatment_is_cannot_check_not_a_null(self) -> None:
        assessment = assess_coordinate_necessity(_contrast())
        assert assessment.outcome is Outcome.CANNOT_CHECK
        assert assessment.reason is NecessityVerdictReason.TREATMENT_NEVER_APPLIED
        assert assessment.blocks is True
        assert "identical to the full system" in assessment.detail

    def test_applied_treatment_with_no_effect_is_a_measured_negative(self) -> None:
        assessment = assess_coordinate_necessity(
            _contrast(arm_id="remove_referent", cases_treated=32)
        )
        assert assessment.outcome is Outcome.FAIL
        assert assessment.reason is NecessityVerdictReason.COORDINATE_NOT_LOAD_BEARING

    def test_the_two_zero_effect_worlds_are_distinguishable(self) -> None:
        """The whole point: identical point estimates, different verdicts."""

        unapplied = assess_coordinate_necessity(_contrast())
        applied = assess_coordinate_necessity(_contrast(cases_treated=32))
        assert unapplied.contrast.decisions_changed == applied.contrast.decisions_changed == 0
        assert unapplied.reason is not applied.reason
        assert unapplied.outcome is not applied.outcome

    def test_demonstrated_necessity_passes(self) -> None:
        assessment = assess_coordinate_necessity(_contrast(cases_treated=19, decisions_changed=6))
        assert assessment.outcome is Outcome.PASS
        assert assessment.reason is NecessityVerdictReason.COORDINATE_LOAD_BEARING

    def test_sparse_treatment_blocks_below_the_stated_floor(self) -> None:
        assessment = assess_coordinate_necessity(_contrast(cases_treated=2), min_treated_cases=10)
        assert assessment.outcome is Outcome.CANNOT_CHECK
        assert assessment.reason is NecessityVerdictReason.TREATMENT_TOO_SPARSE

    def test_floor_below_one_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 1"):
            assess_coordinate_necessity(_contrast(cases_treated=1), min_treated_cases=0)

    def test_vacuity_can_never_be_paired_with_pass(self) -> None:
        with pytest.raises(ValueError, match="cannot yield PASS"):
            NecessityAssessment(
                arm_id="remove_measurement",
                outcome=Outcome.PASS,
                reason=NecessityVerdictReason.TREATMENT_NEVER_APPLIED,
                detail="a later edit tries to reintroduce the substitution",
                contrast=_contrast(),
            )

    def test_every_vacuity_reason_is_flagged_as_one(self) -> None:
        vacuous = {reason for reason in NecessityVerdictReason if reason.is_vacuity}
        assert vacuous == {
            NecessityVerdictReason.TREATMENT_NEVER_APPLIED,
            NecessityVerdictReason.TREATMENT_TOO_SPARSE,
        }


class TestContrastFromRuns:
    def test_emptying_an_already_empty_field_measures_as_untreated(self) -> None:
        """The P3 shape in miniature: the arm's name says it removed something."""

        control = [("kept", ()), ("kept", ())]
        contrast = contrast_from_runs(
            "remove_measurement",
            control_inputs=control,
            treated_inputs=list(control),
            control_decisions=["COMPATIBLE", "CONTRADICTORY"],
            treated_decisions=["COMPATIBLE", "CONTRADICTORY"],
            treatment_definition=TREATMENT,
        )
        assert contrast.cases_treated == 0
        assert assess_coordinate_necessity(contrast).outcome is Outcome.CANNOT_CHECK

    def test_real_removal_counts_only_the_cases_it_altered(self) -> None:
        contrast = contrast_from_runs(
            "remove_construct",
            control_inputs=[("a", ("C1",)), ("b", ())],
            treated_inputs=[("a", ()), ("b", ())],
            control_decisions=["COMPATIBLE", "COMPATIBLE"],
            treated_decisions=["UNRESOLVED", "COMPATIBLE"],
            treatment_definition=TREATMENT,
        )
        assert (contrast.cases_treated, contrast.decisions_changed) == (1, 1)

    def test_a_decision_moving_on_an_untouched_case_is_refused(self) -> None:
        with pytest.raises(ValueError, match="does not declare"):
            contrast_from_runs(
                "remove_construct",
                control_inputs=[("a", ())],
                treated_inputs=[("a", ())],
                control_decisions=["COMPATIBLE"],
                treated_decisions=["UNRESOLVED"],
                treatment_definition=TREATMENT,
            )

    def test_mismatched_run_lengths_are_refused(self) -> None:
        with pytest.raises(ValueError, match="different case counts"):
            contrast_from_runs(
                "remove_construct",
                control_inputs=[("a", ())],
                treated_inputs=[],
                control_decisions=["COMPATIBLE"],
                treated_decisions=[],
                treatment_definition=TREATMENT,
            )

    def test_decisions_must_cover_their_inputs(self) -> None:
        with pytest.raises(ValueError, match="treated decisions do not cover"):
            contrast_from_runs(
                "remove_construct",
                control_inputs=[("a", ())],
                treated_inputs=[("a", ())],
                control_decisions=["COMPATIBLE"],
                treated_decisions=[],
                treatment_definition=TREATMENT,
            )


class TestRequireTreatmentApplied:
    def test_raises_naming_the_inert_arms(self) -> None:
        contrasts = [
            _contrast(arm_id="remove_referent", cases_treated=32),
            _contrast(arm_id="remove_measurement"),
            _contrast(arm_id="remove_temporal_context"),
        ]
        with pytest.raises(InertAblation) as excinfo:
            require_treatment_applied(contrasts, label="P3 public-reference atlas")
        message = str(excinfo.value)
        assert "remove_measurement" in message
        assert "remove_temporal_context" in message
        assert "remove_referent" not in message

    def test_passes_when_every_arm_applied_its_treatment(self) -> None:
        require_treatment_applied(
            [_contrast(arm_id="remove_referent", cases_treated=32)], label="panel"
        )

    def test_an_empty_panel_measures_nothing(self) -> None:
        with pytest.raises(InertAblation, match="measures nothing"):
            require_treatment_applied([], label="panel")
