from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = (
    ROOT
    / "papers"
    / "orion-05-tare-expressivity"
    / "evidence"
    / "historical"
    / "pr-1498-q1-xover-v1"
)
VERIFIER = ARCHIVE / "verify_orion05_pr1498_custody_v1.py"


def _verifier():
    assert VERIFIER.is_file(), f"missing custody verifier: {VERIFIER}"
    spec = importlib.util.spec_from_file_location("orion05_pr1498_custody", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pr1498_archive_verifies_exact_donor_and_adverse_result_custody() -> None:
    report = _verifier().verify_archive()

    assert report["terminal"] == "ORION05_PR1498_HISTORICAL_CUSTODY_PASS"
    assert report["paper_id"] == "ORION-05"
    assert report["donor_head"] == "272f2a1aa7b63d409fc460b35bb89e4aa8b5dcbb"
    assert report["archive_tag"] == "archive/orion-01-05/pr-1498-head-272f2a1aa7b6"
    assert report["files_verified"] == 14
    assert report["raw_verdict"] == "RUN_INCOMPLETE"
    assert report["coverage"] == {
        "sampled": 384,
        "exact_n_le_5": 372,
        "timeouts_n_6": 12,
        "by_n": {
            1: {"sampled": 72, "exact": 72, "timeouts": 0},
            2: {"sampled": 96, "exact": 96, "timeouts": 0},
            3: {"sampled": 96, "exact": 96, "timeouts": 0},
            4: {"sampled": 72, "exact": 72, "timeouts": 0},
            5: {"sampled": 36, "exact": 36, "timeouts": 0},
            6: {"sampled": 12, "exact": 0, "timeouts": 12},
        },
    }
    assert report["authority_defects_preserved"] == {
        "registered_p6_did_not_predict_zero_timeouts": True,
        "evaluator_added_unregistered_timeouts_equal_zero_clause": True,
        "evaluator_structural_clause_did_not_test_named_n_gt_6_collections": True,
    }
    assert report["source_archive_binding"] == {
        "archived_blob_matches_run1_submission": True,
        "archived_blob_matches_run2_submission": False,
        "run2_source_archive_materialized": False,
    }


def test_pr1498_archive_rejects_raw_byte_mutation(tmp_path: Path) -> None:
    copied = tmp_path / ARCHIVE.name
    shutil.copytree(ARCHIVE, copied)
    target = (
        copied
        / "raw"
        / "research"
        / "extensions"
        / "orion-q"
        / "Q1_XOVER_RESULTS_V1.json"
    )
    target.write_bytes(target.read_bytes() + b"\n")

    with pytest.raises(AssertionError, match="archived_file_binding_drift"):
        _verifier().verify_archive(archive_root=copied)


@pytest.mark.parametrize(
    "proposed",
    ["GENERAL_POSITIVE_CROSSOVER", "SPARSE_O_N9_REFUTATION"],
)
def test_pr1498_archive_rejects_forbidden_scientific_promotion(proposed: str) -> None:
    with pytest.raises(AssertionError, match="promotion_not_permitted"):
        _verifier().require_scientific_disposition(proposed)

