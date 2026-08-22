"""The extension must actually apply the two treatments the frozen atlases never did.

The assertions that matter here are not "24 cases were emitted". They are that
the added cases make ``remove_measurement`` and ``remove_temporal_context``
alter their inputs *and* move decisions, measured with the same instrument that
found the defect, and that nothing outside the coordinate values varies with the
answer. The second is a regression test with a history: the first build of this
atlas used a hex digest in ``case_id``, whose leading non-digit run is not
constant, and shipped seven distinct identifier prefixes across 24 cases.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.knowledge.semantics import MeaningRelation
from orion.programme.records import Outcome
from orion.study.p3.public_reference_audit import audit_atlas, contrasts_for_atlas
from orion.study.p3.treatment_contrast import (
    NecessityVerdictReason,
    require_treatment_applied,
)
from orion.study.p3_coordinate_necessity_build import (
    COORDINATE_FIELDS,
    build_extension,
    build_report,
    dependence_receipts,
    gold_relation,
    measurement_dimensions,
    observation_epochs,
    shape_invariants,
    standard_bytes,
    synthetic_coordinate_cases,
    write_jsonl,
)
from orion.study.p3_public_reference import load_jsonl, validate_case

COORDINATE_ARMS = {
    "measurement_ids": "remove_measurement",
    "temporal_context_ids": "remove_temporal_context",
}


def _parent_case(case_id: str, relation: str = "COMPATIBLE") -> dict[str, object]:
    """A parent-atlas case shaped like the frozen ones: both coordinates empty."""

    projection = {
        "projection_id": f"{case_id}:left",
        "source_id": "fixture-source",
        "source_span": "record/a",
        "predicate": "states_effect",
        "referent_ids": ["fixture:referent"],
        "construct_ids": ["fixture:construct"],
        "measurement_ids": [],
        "temporal_context_ids": [],
        "polarity": "POSITIVE",
        "modality": "ASSERTED",
    }
    right = dict(projection, projection_id=f"{case_id}:right", source_span="record/b")
    return {
        "schema_version": "orion.p3.public-reference-case.v1",
        "case_id": case_id,
        "discipline": "physics",
        "case_family": "different_name_same_referent",
        "source_records": [
            {
                "dataset": "fixture-upstream",
                "revision": "0123456789abcdef",
                "locator": "record/a",
                "content_hash": "a" * 64,
            }
        ],
        "left_projection": projection,
        "right_projection": right,
        "expected": {
            "meaning_relation": relation,
            "authority": {"kind": "UPSTREAM_EXPERT", "evidence": ["fixture:record/a"]},
        },
    }


@pytest.fixture()
def parent_atlas(tmp_path: Path) -> Path:
    path = tmp_path / "parent.jsonl"
    write_jsonl(path, [_parent_case(f"fixture-{index:02d}") for index in range(4)])
    return path


class TestAddedCases:
    def test_every_added_case_is_a_valid_public_reference_case(self) -> None:
        for case in synthetic_coordinate_cases():
            validate_case(case)

    def test_both_absent_coordinates_are_populated_on_every_added_case(self) -> None:
        for case in synthetic_coordinate_cases():
            for side in ("left_projection", "right_projection"):
                projection = case[side]
                assert isinstance(projection, dict)
                for field in COORDINATE_FIELDS:
                    assert len(projection[field]) == 1, (field, side, case["case_id"])

    def test_counts_match_the_frozen_protocol(self) -> None:
        cases = synthetic_coordinate_cases()
        relations = [str(dict(case["expected"])["meaning_relation"]) for case in cases]
        assert len(cases) == 24
        assert relations.count("DISTINCT_MEASUREMENT") == 4
        assert relations.count("CONTEXTUAL_DIFFERENCE") == 4
        assert relations.count("COMPATIBLE") == 16

    def test_compatible_is_the_strict_majority_of_every_added_family(self) -> None:
        # The property that stops a family token from recovering the answer: a
        # majority-vote rule over any construction cue lands on COMPATIBLE.
        by_family: dict[str, list[str]] = {}
        for case in synthetic_coordinate_cases():
            relation = str(dict(case["expected"])["meaning_relation"])
            by_family.setdefault(str(case["case_family"]), []).append(relation)
        for family, relations in by_family.items():
            other = max(
                (relations.count(name) for name in set(relations) if name != "COMPATIBLE"),
                default=0,
            )
            assert relations.count("COMPATIBLE") > other, family

    def test_gold_follows_from_the_coordinates_not_from_the_slot(self) -> None:
        assert (
            gold_relation(
                measurement_left="a",
                measurement_right="b",
                temporal_left="t",
                temporal_right="t",
            )
            is MeaningRelation.DISTINCT_MEASUREMENT
        )
        assert (
            gold_relation(
                measurement_left="a",
                measurement_right="a",
                temporal_left="t",
                temporal_right="u",
            )
            is MeaningRelation.CONTEXTUAL_DIFFERENCE
        )
        assert (
            gold_relation(
                measurement_left="a",
                measurement_right="a",
                temporal_left="t",
                temporal_right="t",
            )
            is MeaningRelation.COMPATIBLE
        )

    def test_every_non_compatible_case_depends_on_its_coordinate(self) -> None:
        receipts = dependence_receipts(synthetic_coordinate_cases())
        assert len(receipts) == 8
        for receipt in receipts:
            assert receipt["full_system_correct"], receipt
            assert receipt["ablation_changes_answer"], receipt
            assert receipt["ablated"] == "COMPATIBLE"
            assert receipt["arm"] == COORDINATE_ARMS[str(receipt["coordinate"])]

    def test_construction_shapes_are_constant_across_the_added_cases(self) -> None:
        for name, values in shape_invariants(synthetic_coordinate_cases()).items():
            assert len(values) == 1, (name, values)

    def test_shape_invariants_notice_a_varying_identifier(self) -> None:
        cases = [dict(case) for case in synthetic_coordinate_cases()]
        cases[0]["case_id"] = "coordinate-synth-x0000000000000001"
        invariants = shape_invariants(cases)
        assert len(invariants["case_id_alpha_prefix"]) == 2

    def test_the_standard_table_reuses_the_frozen_unit_dimensions(self) -> None:
        payload = json.loads(standard_bytes())
        dimensions = {entry["dimension"] for entry in payload["measurement_dimensions"]}
        assert dimensions == {name for name, _ in measurement_dimensions()}
        assert payload["observation_epochs"] == list(observation_epochs())


class TestExtension:
    def test_parent_cases_pass_through_unchanged(self, parent_atlas: Path) -> None:
        parent = load_jsonl(parent_atlas)
        merged, report = build_extension(parent_atlas)
        by_id = {str(case["case_id"]): case for case in merged}
        for case in parent:
            assert by_id[str(case["case_id"])] == case
        assert report["parent_atlas"]["case_count"] == len(parent)
        assert report["built_n"] == len(parent) + 24

    def test_report_is_ready_and_deterministic(self, parent_atlas: Path) -> None:
        first_cases, first = build_extension(parent_atlas)
        second_cases, second = build_extension(parent_atlas)
        assert first["status"] == "READY"
        assert first["blockers"] == []
        assert first["cases_hash"] == second["cases_hash"]
        assert [case["case_id"] for case in first_cases] == [
            case["case_id"] for case in second_cases
        ]

    def test_cases_are_emitted_in_case_id_order(self, parent_atlas: Path) -> None:
        merged, _ = build_extension(parent_atlas)
        ids = [str(case["case_id"]) for case in merged]
        assert ids == sorted(ids)

    def test_report_blocks_when_a_case_does_not_depend_on_its_coordinate(
        self, parent_atlas: Path
    ) -> None:
        parent = load_jsonl(parent_atlas)
        added = [dict(case) for case in synthetic_coordinate_cases()]
        # Empty the coordinate the case's gold was derived from: the arm can no
        # longer alter it, which is exactly the defect being repaired.
        for case in added:
            expected = dict(case["expected"])
            if str(expected["meaning_relation"]) == "DISTINCT_MEASUREMENT":
                left = dict(case["left_projection"])
                right = dict(case["right_projection"])
                left["measurement_ids"] = []
                right["measurement_ids"] = []
                case["left_projection"] = left
                case["right_projection"] = right
        report = build_report(parent_atlas, parent, added, [*parent, *added])
        assert report["status"] == "CANNOT_CHECK"
        assert any("remove_measurement" in blocker for blocker in report["blockers"])


class TestArmsOnTheExtendedAtlas:
    def test_the_two_arms_now_apply_their_treatment(self, parent_atlas: Path) -> None:
        merged, _ = build_extension(parent_atlas)
        contrasts = {item.arm_id: item for item in contrasts_for_atlas(merged)}
        for arm in COORDINATE_ARMS.values():
            assert contrasts[arm].cases_treated == 24
            assert contrasts[arm].decisions_changed == 4
            assert contrasts[arm].resolution == pytest.approx(1 / 24)
        require_treatment_applied(tuple(contrasts.values()), label="extension")

    def test_the_two_arms_report_a_measured_verdict(self, parent_atlas: Path) -> None:
        merged, _ = build_extension(parent_atlas)
        report = audit_atlas("test-extension", merged)
        verdicts = {
            str(item["arm_id"]): (item["outcome"], item["reason"])
            for item in report["coordinate_necessity"]
        }
        for arm in COORDINATE_ARMS.values():
            assert verdicts[arm] == (
                Outcome.PASS.value,
                NecessityVerdictReason.COORDINATE_LOAD_BEARING.value,
            )

    def test_the_referent_arm_keeps_its_real_negative(self, parent_atlas: Path) -> None:
        # The extension may not turn a published negative into a pass: every
        # added case holds referent_ids and construct_ids equal across the pair.
        merged, _ = build_extension(parent_atlas)
        contrasts = {item.arm_id: item for item in contrasts_for_atlas(merged)}
        for arm in ("remove_referent", "remove_construct"):
            assert contrasts[arm].cases_treated > 0
            assert contrasts[arm].decisions_changed == 0
