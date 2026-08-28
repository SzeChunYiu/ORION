from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_orion09_separator_and_adverse_transfer_are_bound() -> None:
    result = load_json(
        "papers/orion-09-compilation-regime-geometry/"
        "theory/regime-separator-complexity-v1/RESULT.json"
    )

    assert result["status"] == "PASS"
    assert result["independent_replay"]["mismatches"] == {}
    assert result["separator_complexity"]["k_star"] == 4
    assert result["separator_complexity"]["k_star_proved_exact"] is True
    assert result["separator_complexity"]["witness"]["floor"] == 0
    assert result["preserved_negative"]["H_B_N4_residual"] == "NOT_IMPROVED"
    assert result["preserved_negative"]["cv_errors_120"] == 32
    assert result["preserved_negative"]["shuffle_null_p"] == 0.51
    assert {
        finding["id"] for finding in result["adverse_findings"]
    } >= {"MECHANISM_ATTRIBUTION_NOT_SUPPORTED"}


def test_orion09_manuscript_reports_positive_and_adverse_results_together() -> None:
    abstract = (
        ROOT
        / "papers/orion-09-compilation-regime-geometry/manuscript/main.tex"
    ).read_text(encoding="utf-8")
    results = (
        ROOT
        / "papers/orion-09-compilation-regime-geometry/"
        "manuscript/sections/03-results.tex"
    ).read_text(encoding="utf-8")

    for text in (abstract, results):
        assert "unseen $n=4$" in text
        assert "state-sign" in text

    assert "four features" in abstract
    assert "four-feature witness" in results
    assert "size four" in results
    assert "43/1,146" in abstract
    assert "32/120" in results
    assert "p=0.51" in results


def test_orion10_certificate_explanation_gap_is_exact_and_bounded() -> None:
    result = load_json(
        "papers/orion-10-certified-static-forecasting/"
        "theory/certificate-explanation-gap-v1/RESULT.json"
    )

    exhaustive = result["check_A_B_C_exhaustive"]
    assert result["status"] == "PASS"
    assert exhaustive["structures_checked"] == 21501
    assert exhaustive["exactness_iff_fibre_constancy"] is True
    assert exhaustive["size_independence_verified"] is True
    assert result["check_D_manuscript_counts"]["mismatches"] == {}
    assert all(
        control["pass"]
        for control in result["check_E_negative_controls"].values()
    )


def test_orion13_unique_polarity_reduct_and_confound_are_retained() -> None:
    result = load_json(
        "papers/orion-13-global-knowledge-portrait/"
        "theory/minimal-semantic-separator-v1/RESULT.json"
    )
    disposition = (
        ROOT
        / "papers/orion-13-global-knowledge-portrait/"
        "theory/minimal-semantic-separator-v1/CLAIM_DISPOSITION.md"
    ).read_text(encoding="utf-8")

    assert result["status"] == "PASS"
    assert result["k_star_on_derivation"] == 1
    assert result["minimal_sufficient_subsets_reducts"] == [["polarity"]]
    assert result["core_coordinates_in_every_reduct"] == ["polarity"]
    assert result["held_out_validation"] == [
        {
            "subset": ["polarity"],
            "size": 1,
            "sufficient_on_challenge_set": True,
            "collisions_on_challenge_set": [],
        }
    ]
    assert "perfectly confounded" in disposition
    assert "full coordinate necessity" in disposition
    assert "undetermined" in disposition


def test_orion15_independent_verification_preserves_rule_defect_and_scope() -> None:
    result = load_json(
        "research/self-orion-v4/verification/"
        "SCIENTIFIC_RESULT_VERIFICATION_V1.json"
    )

    assert (
        result["verification_state"]
        == "BOUNDED_VERIFIED_WITH_NONCONTROLLING_EXECUTABLE_RULE_DEFECT"
    )
    assert result["recomputed_terminal"] == "REVISION_LEVEL_DISCRIMINATION_SUPPORTED"
    assert result["rule_implementation_defect"]["detected"] is True
    assert (
        result["rule_implementation_defect"]["controlling_for_observed_terminal"]
        is False
    )
    assert result["subject_metrics"]["accuracy"] == 1.0
    assert result["subject_metrics"]["false_broad"] == 0.0
    assert result["subject_metrics"]["harm"] == 0.0
    assert result["subject_metrics"]["authority"] == 0.0
    assert result["subject_metrics"]["preservation_refusal"] == 1.0
    assert result["subject_metrics"]["fresh"] == 0.8888888888888888
    assert result["v3_negative_retained"] == "NO_TERMINAL_UNDER_FROZEN_RULES"
    assert result["grants_live_provider_claim"] is False
    assert result["source_execution_replay_evidence"][
        "new_child_commit_execution_claimed"
    ] is False


def test_recovery_receipt_records_owned_lane_exclusions() -> None:
    receipt = load_json(
        "papers/publication_closure/"
        "ISSUE1701_MIDDLE_PAPERS_RECOVERY_V1.json"
    )
    excluded = {
        entry["paper_id"]: entry for entry in receipt["intentionally_not_duplicated"]
    }

    assert receipt["issue"] == 1701
    assert receipt["authority"]["new_empirical_outcomes_generated"] is False
    assert receipt["authority"]["post_outcome_tuning"] is False
    assert receipt["authority"]["cannot_check_promoted_to_pass"] is False
    assert excluded["ORION-16"]["reason"].endswith("#1695")
    assert excluded["ORION-17"]["pr"] == 1692
    assert (
        excluded["ORION-17"]["density_tree_sha"]
        == "2180731e6a340b25f41b65ef4d245327f679c164"
    )
