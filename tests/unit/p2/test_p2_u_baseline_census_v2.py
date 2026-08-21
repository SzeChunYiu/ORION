from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P2 = ROOT / "research" / "claim_expansion" / "p2"
V1_PATH = P2 / "P2_U_BASELINE_CENSUS_V1.json"
V2_PATH = P2 / "P2_U_BASELINE_CENSUS_V2.json"
PROTOCOL_PATH = P2 / "P2_U_SCIENTIFIC_PROTOCOL_V1.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def test_v2_is_additive_and_preserves_primary_causal_comparator():
    v1 = _load(V1_PATH)
    v2 = _load(V2_PATH)

    assert v2["extends"]["git_blob_sha"] == "bb1a7277ac8480d6d68b7936b7b747e91c7ac433"
    assert v2["extends"]["v1_remains_immutable"] is True
    unchanged = v2["unchanged_scientific_authority"]
    assert all(value is False for value in unchanged.values())
    assert "same-host" in v1["comparison_policy"]["primary_causal_comparator"]
    assert "donor-complete" in v1["comparison_policy"]["primary_causal_comparator"]


def test_added_public_surfaces_are_explicitly_non_authorizing():
    v2 = _load(V2_PATH)
    surfaces = {row["name"]: row for row in v2["added_public_benchmark_surfaces"]}

    assert set(surfaces) == {"TaxoBench", "TrialReviewBench"}
    assert surfaces["TaxoBench"]["repository_revision"] == "49a18698ff2d5efb696e0215642441ded668ae2f"
    assert "SOLE_PROTECTED_P2_U_SUPERIORITY_AUTHORITY" in surfaces["TaxoBench"]["forbidden_role"]
    assert "SYSTEMATIC_REVIEW_LIKE_TRANSFER_SANITY_CHECK" in surfaces["TrialReviewBench"]["allowed_role"]
    assert "SOLE_PROTECTED_P2_U_SUPERIORITY_OR_REPLICATION_AUTHORITY" in surfaces["TrialReviewBench"]["forbidden_role"]


def test_added_systems_cannot_replace_matched_donor_complete_comparator():
    v2 = _load(V2_PATH)
    systems = {row["name"]: row for row in v2["added_contemporaneous_system_census"]}

    assert set(systems) == {"S1-DeepResearch-32B", "TrialMind"}
    assert systems["S1-DeepResearch-32B"]["model_repository_revision_at_census"] == "784b5ef0104400d23206a752843f695ca4bf9530"
    assert "never float main" in systems["S1-DeepResearch-32B"]["execution_revision_rule"]
    assert systems["TrialMind"]["repository_revision"] == "235426b072747e9f6586020c2632b1e8a657ad10"
    assert all("SYSTEM_LEVEL_ONLY" in row["causal_status"] for row in systems.values())
    assert any("Neither added system replaces" in row for row in v2["execution_manifest_requirements_added_by_v2"])


def test_scientific_thresholds_remain_the_frozen_v1_values():
    protocol = _load(PROTOCOL_PATH)
    v2 = _load(V2_PATH)
    gates = protocol["primary_effect_and_safety_gates"]

    assert gates["route_use_recall_superiority"]["mean_task_delta_orion_minus_donor_at_least"] == 0.05
    assert gates["false_closure_noninferiority"]["noninferiority_margin"] == 0.02
    assert gates["final_scientific_utility_noninferiority"]["noninferiority_margin"] == 0.02
    assert gates["valid_closure_yield_noninferiority"]["noninferiority_margin_for_interval"] == 0.05
    assert protocol["inference"]["bootstrap"]["replicates"] == 20000
    assert protocol["inference"]["power_gate_before_execution"]["target_power_at_least"] == 0.8
    assert protocol["validity_and_invalidity"]["minimum_valid_paired_task_fraction_overall"] == 0.95
    assert protocol["validity_and_invalidity"]["minimum_valid_paired_task_fraction_per_frozen_domain"] == 0.9
    assert v2["issue_650_closure_authorized"] is False
    assert v2["promotion_authorized"] is False
