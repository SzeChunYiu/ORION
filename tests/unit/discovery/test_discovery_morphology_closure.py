from __future__ import annotations

import copy
import json
from pathlib import Path

from orion.discovery.discovery_morphology_closure import (
    DiscoveryMorphologyTerminal,
    build_discovery_morphology_closure_report,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "orion-jump-recursive-atoms"
ATLAS = RESEARCH / "DISCOVERY_MORPHOLOGY_ATLAS_V1.json"
BASIS = RESEARCH / "DISCOVERY_MORPHOLOGY_BASIS_V1.json"
SATURATION = RESEARCH / "DISCOVERY_MORPHOLOGY_SATURATION_V1.json"
EXPECTED = RESEARCH / "DISCOVERY_MORPHOLOGY_CLOSURE_EXPECTED_V1.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report(
    *,
    atlas: dict[str, object] | None = None,
    basis: dict[str, object] | None = None,
    saturation: dict[str, object] | None = None,
):
    return build_discovery_morphology_closure_report(
        atlas=atlas or _load(ATLAS),
        basis=basis or _load(BASIS),
        saturation=saturation or _load(SATURATION),
        expected=_load(EXPECTED),
    )


def test_discovery_morphology_matches_pre_frozen_terminal_and_counts() -> None:
    expected = _load(EXPECTED)
    report = _report()

    assert report.episode_count == expected["atlas"]["episodes"] == 51
    assert dict(report.domain_counts) == expected["atlas"]["domain_counts"] == {
        "MATHEMATICS_FORMAL": 16,
        "SCIENCE": 15,
        "ENGINEERING_DESIGN": 12,
        "EVERYDAY_PRACTICAL": 8,
    }
    assert report.no_jump_control_count == expected["atlas"]["no_jump_controls"] == 5
    assert report.dimension_count == expected["basis"]["dimensions"] == 10
    assert dict(report.dimension_episode_support) == expected["basis"][
        "dimension_episode_support"
    ]
    assert report.post_basis_round_count == expected["post_basis_saturation"]["rounds"] == 2
    assert report.post_basis_primary_source_count == expected["post_basis_saturation"][
        "primary_sources"
    ] == 8
    assert report.material_change_round_ids == ()
    assert report.malformed_episode_ids == ()
    assert report.unknown_dimension_ids == ()
    assert report.basis_support_mismatch_ids == ()
    assert report.invalid_no_jump_control_ids == ()
    assert report.saturation_unknown_dimension_ids == ()
    assert len(report.all_four_domain_dimension_ids) >= 1
    assert "NEW_OPERATOR_PROCEDURE" in report.all_four_domain_dimension_ids
    assert report.terminal.value == expected["candidate_terminal"]
    assert report.terminal is DiscoveryMorphologyTerminal.USEFUL_MORPHOLOGY_BASIS_FOUND
    assert report.all_checks_passed is True

    assert report.grants_historical_cognition_authority is False
    assert report.grants_atom_independence_authority is False
    assert report.grants_jump_authority is False
    assert report.grants_novelty_authority is False
    assert report.grants_protected_benchmark_authority is False
    assert report.grants_issue_closure_authority is False
    assert expected["authority"] == {
        "grants_historical_cognition_authority": False,
        "grants_atom_independence_authority": False,
        "grants_jump_authority": False,
        "grants_novelty_authority": False,
        "grants_protected_benchmark_authority": False,
        "grants_issue_closure_authority": False,
    }


def test_every_historical_episode_preserves_source_and_hindsight_boundaries() -> None:
    atlas = _load(ATLAS)
    for episode in atlas["episodes"]:
        assert episode["source_kind"].startswith("PRIMARY_")
        assert episode["source_locator"]
        assert episode["documented_artifact_claim"]
        assert episode["private_cognitive_sequence"] == "CANNOT_INFER"
        assert episode["structural_interpretation_role"] == "STRUCTURAL_INTERPRETATION"
        assert len(set(episode["competing_interpretations"])) >= 2
        assert episode["historical_use"] == "MECHANISM_EXTRACTION_ONLY"
        assert episode["protected_confirmatory_gold"] is False


def test_every_no_jump_control_is_explicitly_fixed_regime() -> None:
    atlas = _load(ATLAS)
    controls = [
        episode
        for episode in atlas["episodes"]
        if episode["jump_status"] == "NO_JUMP_CONTROL"
    ]

    assert len(controls) == 5
    assert {
        "D013",
        "D014",
        "D015",
        "D016",
        "D029",
    } == {episode["episode_id"] for episode in controls}
    assert all(
        "FIXED_REGIME_SEARCH_CONTROL" in episode["candidate_morphology_ids"]
        for episode in controls
    )


def test_every_registered_dimension_has_multi_episode_multi_domain_support() -> None:
    report = _report()

    assert min(dict(report.dimension_episode_support).values()) >= 5
    assert min(dict(report.dimension_domain_support).values()) >= 2
    assert len(report.all_four_domain_dimension_ids) >= 1


def test_private_cognition_leak_fails_closed() -> None:
    atlas = _load(ATLAS)
    tampered = copy.deepcopy(atlas)
    tampered["episodes"][0]["private_cognitive_sequence"] = "invented-a-new-geometry-in-his-head"

    report = _report(atlas=tampered)

    assert "D001" in report.malformed_episode_ids
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK
    assert report.all_checks_passed is False


def test_historical_gold_promotion_fails_closed() -> None:
    atlas = _load(ATLAS)
    tampered = copy.deepcopy(atlas)
    tampered["episodes"][1]["protected_confirmatory_gold"] = True

    report = _report(atlas=tampered)

    assert "D002" in report.malformed_episode_ids
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK


def test_no_jump_control_without_fixed_regime_tag_fails_closed() -> None:
    atlas = _load(ATLAS)
    tampered = copy.deepcopy(atlas)
    control = next(
        episode for episode in tampered["episodes"] if episode["episode_id"] == "D013"
    )
    control["candidate_morphology_ids"] = ["NEW_OPERATOR_PROCEDURE"]

    report = _report(atlas=tampered)

    assert "D013" in report.invalid_no_jump_control_ids
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK


def test_unknown_morphology_tag_fails_closed() -> None:
    atlas = _load(ATLAS)
    tampered = copy.deepcopy(atlas)
    tampered["episodes"][2]["candidate_morphology_ids"].append("MAGIC_CREATIVE_LEAP")

    report = _report(atlas=tampered)

    assert report.unknown_dimension_ids == ("MAGIC_CREATIVE_LEAP",)
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK


def test_basis_metadata_drift_fails_closed() -> None:
    basis = _load(BASIS)
    tampered = copy.deepcopy(basis)
    dimension = next(
        row for row in tampered["dimensions"] if row["id"] == "NEW_OPERATOR_PROCEDURE"
    )
    dimension["frozen_episode_support"] += 1

    report = _report(basis=tampered)

    assert report.basis_support_mismatch_ids == ("NEW_OPERATOR_PROCEDURE",)
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK


def test_material_new_dimension_in_post_basis_round_reopens_closure() -> None:
    saturation = _load(SATURATION)
    tampered = copy.deepcopy(saturation)
    tampered["rounds"][1]["new_dimension_ids"] = ["SOME_NEW_REUSABLE_RELATION"]
    tampered["rounds"][1]["material_change"] = True
    tampered["rounds"][1]["result"] = "MATERIAL_CHANGE"

    report = _report(saturation=tampered)

    assert report.material_change_round_ids == ("POST_BASIS_ROUND_2",)
    assert report.terminal is DiscoveryMorphologyTerminal.CANNOT_CHECK
