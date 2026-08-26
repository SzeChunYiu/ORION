"""Issue #157 closure receipt must bind committed hashes and refuse to promote nulls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import sha256_digest

PAPER = Path("papers/orion-12-open-world-scientific-discovery")
RECEIPT = PAPER / "evidence" / "external_results" / "ISSUE_157_CLOSURE_RECEIPT_V1.json"
PROBE = PAPER / "evidence" / "external_results" / "ISSUE_157_KEYLESS_BACKEND_PROBE_V1.json"
SUMMARY = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
GOLD = PAPER / "evidence" / "offline_gold" / "MANIFEST.json"
DEEP = PAPER / "evidence" / "external_results" / "DEEP_OFFICIAL_ARCHIVE_V1.json"
WIDE = PAPER / "evidence" / "external_results" / "AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_complete_gold_hashes_match_committed_390_task_summary() -> None:
    receipt = _load(RECEIPT)
    summary = _load(SUMMARY)
    gold = _load(GOLD)
    frozen = summary["frozen_run"]
    gold_block = receipt["complete_gold"]

    assert gold_block["status"] == "REPRODUCED"
    assert gold_block["projection_matches_committed_summary"] is True
    assert gold_block["n_tasks"] == frozen["n_tasks"] == gold["task_count"] == 390
    assert gold_block["n_result_records"] == frozen["n_result_records"] == 16380
    assert gold_block["analysis_authority"] == summary["analysis_authority"] == "TIER_B_committed"
    assert gold_block["primary_promoted"] is False
    assert summary["achieved_precision"]["primary_promoted"] is False
    assert gold_block["orion_complete_gold_recall"] == summary["systems"]["orion_full"][
        "mean_complete_gold_recall"
    ]
    assert gold_block["content_hashes"]["record_digest_sha256"] == frozen["record_digest_sha256"]
    assert (
        gold_block["content_hashes"]["raw_artifact_hash_list_digest_sha256"]
        == frozen["raw_artifact_hash_list_digest_sha256"]
    )
    assert gold_block["content_hashes"]["results_summary_file_sha256"] == _file_sha256(SUMMARY)
    assert gold_block["content_hashes"]["results_summary_canonical_sha256"] == sha256_digest(
        summary
    )
    assert gold_block["suite_fingerprint"] == gold["suite_fingerprint"]

    repair = gold_block["read_encounter_budget_reprojection"]
    adverse = repair["no_content_identity_dedup_adverse_change"]
    no_dedup = summary["systems"]["no_content_identity_dedup"]
    assert repair["authority"] == "HOST_BUDGET_CONTRACT_CORRECTION__NO_CLAIM_PROMOTION"
    assert adverse["corrected"]["PASS"] == no_dedup["status_counts"]["PASS"] == 144
    assert adverse["corrected"]["FAIL"] == no_dedup["status_counts"]["FAIL"] == 193
    assert adverse["corrected"]["CANNOT_CHECK"] == no_dedup["status_counts"][
        "CANNOT_CHECK"
    ] == 53
    assert adverse["corrected"]["budget_exhaustion_failures"] == no_dedup[
        "failure_counts"
    ]["budget_exhausted"] == 193


def test_deep_official_null_is_not_relabelled_positive() -> None:
    receipt = _load(RECEIPT)
    deep = _load(DEEP)
    block = receipt["deep"]

    assert deep["official_metrics"]["hit_rate"] == 0.0
    assert deep["official_metrics"]["hits"] == 0
    assert deep["official_metrics"]["total_items"] == 600
    assert block["hit_rate"] == 0.0
    assert block["relabelled_positive"] is False
    assert block["status"] == "EXECUTED_NULL_ON_MAIN"
    assert block["matched_multi_provider_deep"] == "CANNOT_CHECK"
    assert "positive" not in block["status"].lower()
    assert block["archive_file_sha256"] == _file_sha256(DEEP)


def test_matched_wide_without_arxiv_is_cannot_check_with_named_blockers() -> None:
    receipt = _load(RECEIPT)
    probe = _load(PROBE)
    wide = _load(WIDE)
    matched = receipt["wide"]["matched_orion_vs_baseline_keyless_no_arxiv"]

    assert receipt["close_issue"] is False
    assert matched["status"] == "CANNOT_CHECK"
    assert matched["executed"] is False
    assert matched["arxiv_api_called"] is False
    assert probe["arxiv_api_called"] is False
    assert probe["authority"] == "CONNECTIVITY_PROBE_NOT_MATCHED_CAMPAIGN"
    assert probe["identity_bridge"]["crossref_naive_regex_is_identity_bridge"] is False
    ids = {item["id"] for item in matched["blockers"]}
    assert ids == {
        "FROZEN_ADAPTER_REQUIRES_ARXIV",
        "OFFICIAL_SCORER_ARXIV_ID_IOU",
        "NO_ARXIV_MATCHED_RUNNER_ON_MAIN",
    }
    assert wide["official_metrics"]["avg_iou"] == 0.005226
    assert receipt["wide"]["official_keyless_arxiv_probe"]["avg_iou"] == 0.005226
    assert "matched ORION-vs-baseline superiority" in receipt["wide"]["official_keyless_arxiv_probe"][
        "not_claimed"
    ]
    for name in receipt["sibling_279_not_forked"]:
        assert "issue-279" in name or "V2" in name or "279" in name
