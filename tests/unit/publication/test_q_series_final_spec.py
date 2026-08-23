from pathlib import Path

from orion.programme.q_series_sync import validate_q_series_sync
from orion.registry import Q_SERIES_PAPER_IDS, Q_SERIES_PUBLICATION_SPEC_ID


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_final_q_series_spec_matches_framework_and_evidence():
    report = validate_q_series_sync(REPO_ROOT)
    assert report.schema == Q_SERIES_PUBLICATION_SPEC_ID
    assert report.checked_papers == Q_SERIES_PAPER_IDS
    assert {
        "q1_sanity",
        "q1_all_n_receipt",
        "q1_sharpness_witness",
        "q2_final_closure_receipts",
        "q3_scoped_harness_contract",
        "q4_synthetic_scope",
    } <= set(report.checks)


def test_final_q_series_spec_never_grants_authority():
    report = validate_q_series_sync(REPO_ROOT).as_json()
    assert report["grants_scientific_authority"] is False
    assert report["grants_novelty_authority"] is False
