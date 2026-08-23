from pathlib import Path

from orion.programme.q_series_sync import validate_q_series_sync
from orion.registry import Q_SERIES_PAPER_IDS, Q_SERIES_PUBLICATION_SPEC_ID


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_final_q_series_spec_matches_framework_evidence_and_readiness_boundaries():
    report = validate_q_series_sync(REPO_ROOT)
    assert report.schema == Q_SERIES_PUBLICATION_SPEC_ID
    assert report.checked_papers == Q_SERIES_PAPER_IDS
    assert {
        "recursive_refinement_contract",
        "canonical_v3_manuscripts",
        "q1_v3_scope",
        "q1_sanity",
        "q1_all_n_receipt",
        "q1_sharpness_witness",
        "q2_v3_scope",
        "q2_final_closure_receipts",
        "q2_stretch_blocker_preserved",
        "q3_typed_benchmark_contract",
        "q3_one_item_boundary",
        "q3_predictive_blocker_preserved",
        "q4_v3_scope",
        "q4_paired_analysis",
        "q4_n4b_boundary",
        "q4_transfer_blocker_preserved",
    } <= set(report.checks)


def test_final_q_series_spec_never_grants_authority_or_acceptance_prediction():
    report = validate_q_series_sync(REPO_ROOT).as_json()
    assert report["grants_scientific_authority"] is False
    assert report["grants_novelty_authority"] is False
    assert report["predicts_journal_acceptance"] is False
