from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import runpy
import sys

import pytest

from orion.study.p1_p5_successor_readiness import (
    assess_protocol,
    load_and_assess,
    validate_attainability_fixture,
)

ROOT = Path(__file__).resolve().parents[3]
PROTOCOLS = {
    "P1": ROOT / "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json",
    "P2": ROOT / "papers/orion-12-open-world-scientific-discovery/protocol/P2_TASK_WORLD_SUCCESSOR_V2.json",
    "P3": ROOT / "papers/orion-13-global-knowledge-portrait/protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json",
    "P4": ROOT / "papers/orion-14-verified-scientific-discovery/protocol/P4_NATURALISTIC_IDENTIFIABILITY_SUCCESSOR_V1.json",
    "P5": ROOT / "papers/orion-15-self-orion/protocol/P5_WIDE_REVISION_LEVEL_SUCCESSOR_V1.json",
}
FIXTURES = {
    "P3": ROOT / "research/paper-programme-v1/fixtures/P3_PARTIAL_IDENTIFICATION_ATTAINABILITY_FIXTURE_V1.json",
    "P4": ROOT / "research/paper-programme-v1/fixtures/P4_NATURALISTIC_IDENTIFIABILITY_ATTAINABILITY_FIXTURE_V1.json",
    "P5": ROOT / "research/paper-programme-v1/fixtures/P5_REVISION_LEVEL_ATTAINABILITY_FIXTURE_V1.json",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _p1_identity(cluster: str) -> dict[str, str]:
    return {
        "normalized_url": f"https://example.invalid/{cluster}",
        "doi": f"10.9999/{cluster}",
        "stable_artifact_id": cluster,
        "title_first_author_year": f"title::{cluster}::author::2025",
        "official_repository_identity": f"repo::{cluster}",
        "shared_dataset_or_project_family": f"project::{cluster}",
    }


def _p1_r7a_frame(module) -> dict[str, object]:
    pairs = []
    for family in sorted(module.FAMILIES):
        for domain in sorted(module.DOMAINS):
            for index in range(12):
                cluster = f"r7a-pair-{family}-{domain}-{index}"
                pairs.append(
                    {
                        "cluster_id": cluster,
                        "family": family,
                        "domain": domain,
                        "query_ids": [f"query-{family}-{domain}"],
                        "source_identity": _p1_identity(cluster),
                        "members": {"adverse": f"{cluster}-a", "control": f"{cluster}-c"},
                    }
                )
    unresolved = []
    for domain in sorted(module.DOMAINS):
        for index in range(16):
            cluster = f"r7a-unresolved-{domain}-{index}"
            unresolved.append(
                {
                    "cluster_id": cluster,
                    "domain": domain,
                    "query_ids": [f"query-unresolved-{domain}"],
                    "source_identity": _p1_identity(cluster),
                }
            )
    return {"pairs": pairs, "unresolved": unresolved}


@pytest.mark.parametrize("paper_id", tuple(PROTOCOLS))
def test_each_successor_is_locally_ready_but_externally_fail_closed(paper_id: str) -> None:
    report = load_and_assess(PROTOCOLS[paper_id], root=ROOT)
    assert report.status == "READY_FOR_EXTERNAL_BINDING"
    assert report.blockers == ()
    assert report.power.passes
    assert report.execution_authorized is False
    assert "CANNOT_CHECK" in report.execution_terminal
    assert report.external_bindings_required
    assert report.grants_scientific_authority is False


def test_p1_seeded_max_t_receipt_is_exactly_reproducible_and_conditional() -> None:
    namespace = runpy.run_path(
        str(ROOT / "research/claim_expansion/p1/gpt_r7a/max_t_power.py")
    )
    observed = namespace["build_receipt"]()
    committed = _load(
        ROOT / "research/claim_expansion/p1/gpt_r7a/R7A_MAXT_POWER_RECEIPT_V1.json"
    )
    assert observed == committed
    registered = committed["registered_planning_point"]
    assert registered["minimum_balanced_source_clusters"] == 384
    assert registered["minimum_is_conditional_on_stated_planning_assumptions"] is True
    sensitivity = {
        (row["planning_delta"], row["planning_discordance"]): row
        for row in committed["sensitivity"]
    }
    assert sensitivity[(0.15, 0.4)]["minimum_balanced_source_clusters"] == 896
    assert sensitivity[(0.2, 0.5)]["minimum_balanced_source_clusters"] == 480


def test_p1_r7a_query_and_source_frames_really_bind_the_wider_quota() -> None:
    query = _load_module(
        ROOT / "research/claim_expansion/p1/gpt_r7a/query_frame.py", "p1_r7a_query_frame"
    )
    source = _load_module(
        ROOT / "research/claim_expansion/p1/gpt_r7/source_frame.py", "p1_r7a_source_frame"
    )
    frame = query.build_query_frame()
    assert frame["sampling"]["pairs_per_family_domain_cell"] == 12
    assert frame["sampling"]["primary_seed"] == 2026082302
    result = source.validate_source_frame(
        _p1_r7a_frame(source), pair_quota=12, unresolved_quota=16, study_id="R7A"
    )
    assert result["complete"], result["errors"]
    assert len(_p1_r7a_frame(source)["pairs"]) == 384


def test_p1_r7a_source_frame_refuses_one_missing_cluster() -> None:
    source = _load_module(
        ROOT / "research/claim_expansion/p1/gpt_r7/source_frame.py", "p1_r7a_source_frame_sparse"
    )
    frame = _p1_r7a_frame(source)
    frame["pairs"].pop()
    result = source.validate_source_frame(
        frame, pair_quota=12, unresolved_quota=16, study_id="R7A"
    )
    assert not result["complete"]
    assert result["terminal"] == "P1_R7A_CANNOT_CHECK_SOURCE_UNIVERSE"


@pytest.mark.parametrize("paper_id", tuple(PROTOCOLS))
def test_no_successor_uses_technical_cells_as_independent_units(paper_id: str) -> None:
    protocol = _load(PROTOCOLS[paper_id])
    design = protocol["design"]
    assert design["independent_unit"] not in set(design["not_independent_units"])
    assert design["planned_independent_units"] == (
        design["stratum_count"] * design["units_per_stratum"]
    )


@pytest.mark.parametrize("paper_id", tuple(FIXTURES))
def test_attainability_fixtures_are_two_sided_and_non_authoritative(paper_id: str) -> None:
    fixture = _load(FIXTURES[paper_id])
    assert validate_attainability_fixture(paper_id, fixture) == ()
    assert fixture["grants_scientific_authority"] is False
    assert set(fixture["admissible_terminals"]) == {"PASS", "FAIL"}


def test_lowering_p1_n_below_registered_max_t_minimum_fails() -> None:
    protocol = _load(PROTOCOLS["P1"])
    protocol["design"]["units_per_stratum"] = 11
    protocol["design"]["planned_independent_units"] = 352
    protocol["power"]["planned_independent_units"] = 352
    report = assess_protocol(protocol, root=ROOT)
    assert "joint_power_or_balance_gate_not_met" in report.blockers


def test_shrinking_p1_comparator_family_fails_even_if_power_looks_easier() -> None:
    protocol = _load(PROTOCOLS["P1"])
    protocol["power"]["comparator_count"] = 1
    report = assess_protocol(protocol, root=ROOT)
    assert "p1_mandatory_comparator_family_incomplete" in report.blockers


@pytest.mark.parametrize(
    ("mutation", "expected"),
    (
        (lambda p: p.__setitem__("outcomes_accessed", True), "protected_outcomes_accessed_before_freeze"),
        (lambda p: p.__setitem__("grants_scientific_authority", True), "preoutcome_protocol_claims_scientific_authority"),
        (lambda p: p.__setitem__("historical_results_immutable", False), "historical_result_mutability_not_prohibited"),
    ),
)
def test_preoutcome_authority_and_history_mutations_fail(mutation, expected: str) -> None:
    protocol = _load(PROTOCOLS["P2"])
    mutation(protocol)
    assert expected in assess_protocol(protocol, root=ROOT).blockers


def test_corrupt_local_binding_digest_fails() -> None:
    protocol = _load(PROTOCOLS["P2"])
    protocol["local_bindings"][0]["sha256"] = "0" * 64
    assert "local_binding_digest_mismatch:COMPARISON_RESOLUTION_PROTOCOL" in assess_protocol(
        protocol, root=ROOT
    ).blockers


def test_p2_unmatched_admissible_exposure_fails() -> None:
    protocol = _load(PROTOCOLS["P2"])
    protocol["design"]["matched_admissible_route_exposure"] = False
    assert "p2_admissible_route_exposure_unmatched" in assess_protocol(
        protocol, root=ROOT
    ).blockers


def test_p3_inert_coordinate_deletion_fails() -> None:
    protocol = _load(PROTOCOLS["P3"])
    protocol["design"]["coordinates_with_required_nonzero_variation"].pop()
    assert "p3_inert_coordinate_set_not_closed" in assess_protocol(protocol, root=ROOT).blockers


def test_p4_identifiable_control_deletion_fails() -> None:
    protocol = _load(PROTOCOLS["P4"])
    protocol["design"]["paired_identifiable_control_required"] = False
    assert "p4_naturalistic_pair_control_missing" in assess_protocol(protocol, root=ROOT).blockers


def test_p5_revision_class_deletion_fails() -> None:
    protocol = _load(PROTOCOLS["P5"])
    protocol["design"]["revision_classes"].pop()
    assert "p5_revision_class_coverage_incomplete" in assess_protocol(protocol, root=ROOT).blockers


@pytest.mark.parametrize("paper_id", tuple(FIXTURES))
def test_duplicate_fixture_cluster_is_rejected(paper_id: str) -> None:
    fixture = deepcopy(_load(FIXTURES[paper_id]))
    fixture["rows"][1]["cluster_id"] = fixture["rows"][0]["cluster_id"]
    assert "fixture_clusters_not_independent" in validate_attainability_fixture(
        paper_id, fixture
    )


@pytest.mark.parametrize("paper_id", tuple(FIXTURES))
def test_one_sided_attainability_fixture_is_rejected(paper_id: str) -> None:
    fixture = deepcopy(_load(FIXTURES[paper_id]))
    fixture["admissible_terminals"] = ["PASS"]
    assert "fixture_gate_not_two_sided" in validate_attainability_fixture(paper_id, fixture)
