from __future__ import annotations

import json
from pathlib import Path

from orion.knowledge.nearest_work import NoveltyVerdict
from orion.transfer.scientific.closure import (
    TransferArm,
    build_assimilation_demo,
    build_assimilation_novelty_assessment,
    build_closure_report,
    build_protected_panel,
)
from orion.transfer.scientific.closure_independent import (
    IndependentMetrics,
    reconstruct_signature_arm,
    reconstruct_terminal,
)

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = ROOT / "development" / "cross-domain-transfer-closure" / "EXPECTED_V1.json"


def _expected() -> dict:
    return json.loads(EXPECTED.read_text())


def test_frozen_panel_has_all_domains_case_types_and_no_gold_in_public_record() -> None:
    cases = build_protected_panel()
    assert len(cases) == 40
    assert {case.public.target_domain for case in cases} == {
        "software", "retrieval", "semantics", "authority", "measurement"
    }
    assert len({case.public.case_id for case in cases}) == 40
    for case in cases:
        assert not hasattr(case.public, "gold_action")
        assert not hasattr(case.public, "case_type")


def test_main_report_matches_pre_run_expected_table_exactly() -> None:
    report = build_closure_report()
    expected = _expected()
    assert expected["frozen_before_runner"] is True
    assert expected["outcome_accessed"] is False
    assert report.case_count == expected["case_count"]
    for arm, metrics in report.arm_metrics:
        assert metrics.__dict__ == expected["expected_metrics"][arm]
    assert report.issue_286_terminal == expected["expected_issue_286_terminal_if_reconstructed"]
    assert report.issue_318_terminal == expected["expected_issue_318_terminal_if_reconstructed"]
    assert report.parent_ties_contract is True
    assert report.assimilation_novelty_verdict == "SUBSUMED"
    assert report.grants_scientific_authority is False
    assert report.grants_novelty_authority is False
    assert report.grants_issue_closure_authority is False


def test_strong_abstract_signature_parent_ties_contract_arm() -> None:
    metrics = dict(build_closure_report().arm_metrics)
    assert metrics[TransferArm.ABSTRACT_INSIGHT_SIGNATURE.value] == metrics[
        TransferArm.MECHANIC_CONTRACT_RECEIPT.value
    ]
    assert metrics[TransferArm.ABSTRACT_INSIGHT_SIGNATURE.value].correct == 40
    assert metrics[TransferArm.ABSTRACT_INSIGHT_SIGNATURE.value].negative_transfer == 0


def test_surface_and_ungated_memory_controls_show_negative_transfer() -> None:
    metrics = dict(build_closure_report().arm_metrics)
    assert metrics[TransferArm.SURFACE_SIMILARITY.value].negative_transfer == 15
    assert metrics[TransferArm.ABSTRACT_INSIGHT.value].negative_transfer == 10
    assert metrics[TransferArm.MECHANIC_CONTRACT_RECEIPT.value].negative_transfer == 0


def test_independent_reconstruction_does_not_need_main_scorer() -> None:
    assert reconstruct_signature_arm() == IndependentMetrics(40, 0, 15, 5, 8)
    assert reconstruct_terminal() == ("ABSTRACTION_ONLY", "PROCESS_USEFUL_NOT_NOVEL")


def test_assimilation_demo_has_clean_adopt_adapt_compose_paths() -> None:
    assert build_assimilation_demo() == (
        ("ADOPT-1", "ADMITTED"),
        ("ADAPT-1", "ADMITTED"),
        ("COMPOSE-1", "ADMITTED"),
    )


def test_absorbed_generic_transfer_claim_is_removed_from_novelty_state() -> None:
    assessment = build_assimilation_novelty_assessment()
    assert assessment.verdict is NoveltyVerdict.SUBSUMED
    assert assessment.candidate_delta_ids == ()
    assert assessment.publication_novelty_authorized is False
