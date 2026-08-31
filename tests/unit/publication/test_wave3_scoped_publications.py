from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PORTFOLIO = ROOT / "papers/WAVE3_PORTFOLIO_PUBLICATION_DISPOSITION_V1.json"

EXPECTED = {
    "ORION-04": {
        "terminal": "ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT",
        "manuscript": ROOT
        / "papers/orion-04-rooted-completion-certificates/WAVE3_SCOPED_MANUSCRIPT_V1.md",
        "disposition": ROOT
        / "papers/orion-04-rooted-completion-certificates/WAVE3_PUBLICATION_DISPOSITION_V1.json",
    },
    "ORION-15": {
        "terminal": "SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED",
        "manuscript": ROOT / "papers/orion-15-self-orion/WAVE3_SCOPED_MANUSCRIPT_V1.md",
        "disposition": ROOT
        / "papers/orion-15-self-orion/WAVE3_PUBLICATION_DISPOSITION_V1.json",
    },
    "ORION-24": {
        "terminal": "ORION24_EXTERNAL_ACQUISITION_BLOCKED__EXECUTABLE_HANDOFF_COMPLETE",
        "manuscript": ROOT / "papers/orion-24-orion-rse/WAVE3_SCOPED_MANUSCRIPT_V1.md",
        "disposition": ROOT
        / "papers/orion-24-orion-rse/WAVE3_PUBLICATION_DISPOSITION_V1.json",
    },
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_wave3_portfolio_has_one_canonical_scoped_manuscript_per_paper() -> None:
    portfolio = _load(PORTFOLIO)
    assert portfolio["portfolio_terminal"] == (
        "WAVE3_THREE_PAPERS_SCOPED_TO_STRONGEST_DEFENSIBLE_EVIDENCE"
        "__SUCCESSOR_STUDIES_SEPARATED"
    )
    assert {row["paper"] for row in portfolio["papers"]} == set(EXPECTED)
    assert len(portfolio["expert_review_roles"]) == 4
    assert portfolio["portfolio_rules"] == {
        "historical_conflicting_manuscripts_are_wave3_canonical": False,
        "repository_ci_counts_as_external_scientific_independence": False,
        "protocol_readiness_counts_as_empirical_outcome": False,
        "adverse_null_blocked_history_is_retained": True,
        "future_successors_require_new_prospective_identity": True,
    }

    for row in portfolio["papers"]:
        expected = EXPECTED[row["paper"]]
        assert row["terminal"] == expected["terminal"]
        assert ROOT / row["manuscript"] == expected["manuscript"]
        assert ROOT / row["disposition"] == expected["disposition"]
        assert expected["manuscript"].is_file()
        assert expected["disposition"].is_file()


def test_every_scoped_manuscript_has_complete_reader_facing_sections() -> None:
    required = (
        "## Abstract",
        "## Data and code availability",
    )
    for expected in EXPECTED.values():
        text = expected["manuscript"].read_text()
        assert len(text.split()) >= 900
        for heading in required:
            assert heading in text
        assert "Limitations" in text


def test_orion04_closes_as_bounded_structural_result_only() -> None:
    disposition = _load(EXPECTED["ORION-04"]["disposition"])
    result = _load(
        ROOT / "research/orion-rg/wave3/orion04-support11-13-v1/RESULT.json"
    )
    generic = _load(
        ROOT / "research/orion-rg/wave3/orion04-support11-13-v1/GENERIC_RESULT.json"
    )

    assert disposition["terminal"] == EXPECTED["ORION-04"]["terminal"]
    assert disposition["admitted_claims"][
        "hypothetical_length31_obstruction_support_at_least_14"
    ] is True
    assert all(value is False for value in disposition["withheld_claims"].values())
    assert result["bounded_support_le13_theorem_authority"] is True
    assert result["support_14_plus_theorem_authority"] is False
    assert result["support_23_theorem_authority"] is False
    assert result["c0_31_authority"] is False
    assert result["exact_d4_authority"] is False
    assert generic["decision"] == "ACCEPT_ORION04_SUPPORT_LE13_EXCLUSION"
    assert all(generic["checks"].values())

    manuscript = EXPECTED["ORION-04"]["manuscript"].read_text()
    assert "support at least 14" in manuscript
    assert "Exact \\(D_4\\) is not established" in manuscript
    assert "support 11, 12 or 13" in manuscript


def test_orion15_preserves_bounded_nonreproduction_without_efficacy_promotion() -> None:
    disposition = _load(EXPECTED["ORION-15"]["disposition"])
    report = _load(
        ROOT / "papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2/report.json"
    )
    authority = _load(
        ROOT
        / "papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2/"
        "AUTHORITY_DISPOSITION_V1.json"
    )

    assert disposition["terminal"] == EXPECTED["ORION-15"]["terminal"]
    assert disposition["admitted_claims"]["control_correct"] == 22
    assert disposition["admitted_claims"]["treatment_correct"] == 23
    assert disposition["admitted_claims"]["cases_per_arm"] == 24
    assert disposition["admitted_claims"]["perfect_treatment_ceiling_reproduced"] is False
    assert all(value is False for value in disposition["withheld_claims"].values())
    assert report["arms"]["control"]["correct"] == 22
    assert report["arms"]["treatment"]["correct"] == 23
    assert "PERFECT_CEILING_NOT_REPRODUCED" in authority["terminal"]
    assert authority["scientific_authority_delta"] == "BOUNDED_DESCRIPTIVE_DIRECTION_ONLY"

    manuscript = EXPECTED["ORION-15"]["manuscript"].read_text()
    assert "22/24" in manuscript
    assert "23/24" in manuscript
    assert "protected longitudinal transfer is not established" in manuscript


def test_orion24_keeps_zero_external_denominator_at_cannot_check() -> None:
    disposition = _load(EXPECTED["ORION-24"]["disposition"])
    admitted = disposition["admitted_claims"]

    assert disposition["terminal"] == EXPECTED["ORION-24"]["terminal"]
    assert admitted["required_preflight_artifact_types"] == 8
    assert admitted["present_preflight_artifact_types"] == 0
    assert admitted["execution_authorized"] is False
    assert admitted["interface_and_harness_readiness"] is False
    assert admitted["external_endpoint_status"] == "CANNOT_CHECK"
    assert disposition["preflight_failure"]["retained_additively"] is True
    assert disposition["preflight_failure"][
        "internal_demonstrations_may_replace_external_denominator"
    ] is False
    assert all(value is False for value in disposition["withheld_claims"].values())

    manuscript = EXPECTED["ORION-24"]["manuscript"].read_text()
    assert "zero of eight required" in manuscript.lower()
    assert "negative acquisition result" not in manuscript.lower()
    assert "requested eight admissible artifacts" not in manuscript.lower()
    assert "external endpoints `CANNOT_CHECK`" in manuscript
    assert "not frontier-agent superiority" in manuscript
