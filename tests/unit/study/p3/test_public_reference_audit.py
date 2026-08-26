"""The audit must find the defect in the frozen artifact, not only in a fixture.

These run against the two atlases that ship in the repo. If a later atlas
populates ``measurement_ids``/``temporal_context_ids`` the ``CANNOT_CHECK``
assertions here are the ones that will turn red, which is the intended signal:
the arms started measuring something.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.records import Outcome
from orion.study.p3.public_reference_audit import (
    RULE_OVERRIDE_ABLATION,
    audit_atlas,
    contrasts_for_atlas,
    ledger_for_atlas,
)
from orion.study.p3.treatment_contrast import (
    InertAblation,
    NecessityVerdictReason,
    require_treatment_applied,
)
from orion.study.p3_public_reference import load_jsonl
from orion.study.p3_public_reference_analysis import ABLATIONS

REPO_ROOT = Path(__file__).resolve().parents[4]
ATLAS_ROOT = REPO_ROOT / "papers/orion-13-global-knowledge-portrait/gold/adjudicated"
ATLASES = ("public-reference-v1", "public-reference-v1.1-confirmatory")

# Measured, not assumed: both frozen atlases leave these two coordinates empty
# on every case, so the arms named after them apply no treatment.
INERT_ARMS = {"remove_measurement", "remove_temporal_context"}


def _cases(atlas: str) -> list[dict[str, object]]:
    path = ATLAS_ROOT / atlas / "PUBLIC_REFERENCE_GOLD_V1.jsonl"
    if not path.exists():  # pragma: no cover - the atlas ships with the repo
        pytest.skip(f"frozen atlas {atlas} is not present")
    return load_jsonl(path)


@pytest.mark.parametrize("atlas", ATLASES)
class TestFrozenAtlas:
    def test_every_ablation_arm_gets_a_contrast(self, atlas: str) -> None:
        contrasts = contrasts_for_atlas(_cases(atlas))
        assert {item.arm_id for item in contrasts} == set(ABLATIONS)

    def test_two_arms_never_applied_their_treatment(self, atlas: str) -> None:
        contrasts = {item.arm_id: item for item in contrasts_for_atlas(_cases(atlas))}
        inert = {arm for arm, item in contrasts.items() if not item.applied}
        assert inert == INERT_ARMS
        for arm in INERT_ARMS:
            assert contrasts[arm].cases_treated == 0
            assert contrasts[arm].effect_rate is None

    def test_the_panel_precondition_names_them(self, atlas: str) -> None:
        with pytest.raises(InertAblation) as excinfo:
            require_treatment_applied(contrasts_for_atlas(_cases(atlas)), label=atlas)
        for arm in INERT_ARMS:
            assert arm in str(excinfo.value)

    def test_the_applied_null_arms_are_a_measured_negative(self, atlas: str) -> None:
        """``remove_referent`` really strips a populated coordinate and nothing moves."""

        report = audit_atlas(atlas, _cases(atlas))
        verdicts = {item["arm_id"]: item for item in report["coordinate_necessity"]}
        referent = verdicts["remove_referent"]
        assert referent["outcome"] == Outcome.FAIL.value
        assert referent["reason"] == NecessityVerdictReason.COORDINATE_NOT_LOAD_BEARING.value
        assert referent["contrast"]["cases_treated"] == report["n_cases"]

    def test_the_inert_arms_and_the_null_arms_get_different_verdicts(self, atlas: str) -> None:
        """Both print 0.0 in ANALYSIS.json; the audit separates them."""

        report = audit_atlas(atlas, _cases(atlas))
        verdicts = {item["arm_id"]: item["outcome"] for item in report["coordinate_necessity"]}
        assert verdicts["remove_measurement"] == Outcome.CANNOT_CHECK.value
        assert verdicts["remove_referent"] == Outcome.FAIL.value

    def test_the_obstruction_arms_demonstrate_necessity(self, atlas: str) -> None:
        report = audit_atlas(atlas, _cases(atlas))
        verdicts = {item["arm_id"]: item for item in report["coordinate_necessity"]}
        for arm in ("remove_modality_polarity_attribution_discourse", RULE_OVERRIDE_ABLATION):
            assert verdicts[arm]["outcome"] == Outcome.PASS.value
            assert verdicts[arm]["contrast"]["decisions_changed"] > 0

    def test_neither_comparator_ever_declines_to_merge(self, atlas: str) -> None:
        ledger = ledger_for_atlas(atlas, _cases(atlas))
        assert ledger.separations_emitted("flat_predicate_canonicalization") == 0
        assert ledger.separations_emitted("exact_coordinate_conservative") == 0
        assert ledger.separations_emitted("orion") > 0

    def test_the_false_merge_denominator_is_far_smaller_than_the_case_count(
        self, atlas: str
    ) -> None:
        cases = _cases(atlas)
        ledger = ledger_for_atlas(atlas, cases)
        flat = ledger.false_merge_exercise("flat_predicate_canonicalization")
        assert flat.opportunities < len(cases)
        assert flat.violations == flat.opportunities
        assert flat.violation_rate == 1.0

    def test_orion_holds_the_false_merge_guard_on_a_real_denominator(self, atlas: str) -> None:
        exercise = ledger_for_atlas(atlas, _cases(atlas)).false_merge_exercise("orion")
        assert exercise.opportunities > 0
        assert exercise.violations == 0

    def test_the_audit_blocks_overall(self, atlas: str) -> None:
        report = audit_atlas(atlas, _cases(atlas))
        assert Outcome(report["overall_outcome"]).blocks is True

    def test_the_report_is_json_serializable(self, atlas: str) -> None:
        json.dumps(audit_atlas(atlas, _cases(atlas)), sort_keys=True)


class TestSyntheticRepair:
    """An atlas that populates the missing coordinates must clear the block."""

    def _repaired(self) -> list[dict[str, object]]:
        cases = _cases("public-reference-v1.1-confirmatory")
        repaired = [json.loads(json.dumps(case)) for case in cases]
        for index, case in enumerate(repaired):
            left = case["left_projection"]
            right = case["right_projection"]
            assert isinstance(left, dict) and isinstance(right, dict)
            left["measurement_ids"] = ["M-shared"]
            right["measurement_ids"] = ["M-shared" if index % 2 else "M-other"]
            left["temporal_context_ids"] = ["T-shared"]
            right["temporal_context_ids"] = ["T-shared" if index % 3 else "T-other"]
        return repaired

    def test_populating_the_coordinates_makes_the_arms_measure_something(self) -> None:
        contrasts = {item.arm_id: item for item in contrasts_for_atlas(self._repaired())}
        for arm in INERT_ARMS:
            assert contrasts[arm].applied is True
            assert contrasts[arm].decisions_changed > 0

    def test_the_precondition_stops_raising(self) -> None:
        require_treatment_applied(contrasts_for_atlas(self._repaired()), label="repaired")
