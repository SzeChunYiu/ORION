from __future__ import annotations

import json

from orion_research_harness.paper_structure import run_paper_structure_consensus
from orion_research_harness.workspace import ResearchWorkspace


def _run(workspace, *, source="paper.txt", method="method:x"):
    return run_paper_structure_consensus(
        workspace,
        source_path=source,
        method_id=method,
        source_id="paper:x",
        source_version="v1",
    )


def _ingest_llm(workspace, pending, claims, *, executor):
    request = pending["request"]
    workspace.ingest_result(
        request["request_id"],
        success=True,
        output={"content": json.dumps({"claims": claims})},
        executor=executor,
    )


def test_two_proposer_lanes_are_distinct_and_complete_requires_coverage_and_verification(tmp_path):
    (tmp_path / "paper.txt").write_text(
        "We localize a bracketed target. First measure the midpoint.\n",
        encoding="utf-8",
    )
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    claims = [
        {
            "coordinate": "target_role",
            "value": "bracketed_localization",
            "quote": "localize a bracketed target",
        },
        {
            "coordinate": "mechanics",
            "value": "measure_midpoint",
            "quote": "measure the midpoint",
        },
    ]

    lane_a = _run(workspace)
    assert lane_a["status"] == "PENDING_CAPABILITY"
    assert lane_a["request"]["capability"] == "LLM_COMPLETE"
    assert lane_a["request"]["payload"]["task"] == "paper_method_structure_extract_v2_lane_a"
    request_a = lane_a["request"]["request_id"]
    _ingest_llm(workspace, lane_a, claims, executor="model:lane-a")

    lane_b = _run(workspace)
    assert lane_b["status"] == "PENDING_CAPABILITY"
    assert lane_b["request"]["payload"]["task"] == "paper_method_structure_extract_v2_lane_b"
    assert lane_b["request"]["request_id"] != request_a
    _ingest_llm(workspace, lane_b, claims, executor="model:lane-b")

    coverage = _run(workspace)
    assert coverage["status"] == "PENDING_CAPABILITY"
    assert coverage["request"]["capability"] == "INDEPENDENT_REVIEW"
    workspace.ingest_result(
        coverage["request"]["request_id"],
        success=True,
        output={"passed": True, "missed_claims": [], "reason": "no supported coordinate omitted"},
        executor="reviewer:coverage",
    )

    verify = _run(workspace)
    assert verify["status"] == "PENDING_CAPABILITY"
    assert verify["request"]["capability"] == "VERIFY_EVIDENCE"
    workspace.ingest_result(
        verify["request"]["request_id"],
        success=True,
        output={"passed": True, "certificate_ids": ["cert:consensus"], "reason": "supported"},
        executor="reviewer:support",
    )

    complete = _run(workspace)
    assert complete["status"] == "COMPLETE"
    assert complete["extraction_mode"] == "TWO_LANE_CONSENSUS_V3"
    by_coordinate = {row["coordinate"]: row for row in complete["support_claims"]}
    assert by_coordinate["target_role"]["proposer_lane_ids"] == ["lane_a", "lane_b"]
    assert complete["coverage_review"]["passed"] is True
    assert complete["verification"]["certificate_ids"] == ["cert:consensus"]
    assert complete["grants_scientific_authority"] is False
    assert complete["grants_novelty_authority"] is False
    assert complete["grants_method_fibre_authority"] is False
    assert complete["grants_promotion_authority"] is False


def test_scalar_proposer_disagreement_fails_closed_before_coverage_review(tmp_path):
    (tmp_path / "paper.txt").write_text(
        "We localize a bracketed target.\n",
        encoding="utf-8",
    )
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    first = _run(workspace)
    _ingest_llm(
        workspace,
        first,
        [{"coordinate": "target_role", "value": "localization", "quote": "localize a bracketed target"}],
        executor="model:a",
    )
    second = _run(workspace)
    _ingest_llm(
        workspace,
        second,
        [{"coordinate": "target_role", "value": "classification", "quote": "localize a bracketed target"}],
        executor="model:b",
    )
    blocked = _run(workspace)
    assert blocked["status"] == "CANNOT_CHECK_PROPOSER_DISAGREEMENT"
    assert blocked["conflicting_coordinates"] == ["target_role"]
    assert "request" not in blocked
    assert blocked["grants_scientific_authority"] is False


def test_coverage_reviewer_valid_missed_claim_reopens_extraction(tmp_path):
    (tmp_path / "paper.txt").write_text(
        "We localize a bracketed target. First measure the midpoint.\n",
        encoding="utf-8",
    )
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    claims = [{"coordinate": "mechanics", "value": "measure_midpoint", "quote": "measure the midpoint"}]
    first = _run(workspace)
    _ingest_llm(workspace, first, claims, executor="model:a")
    second = _run(workspace)
    _ingest_llm(workspace, second, claims, executor="model:b")
    coverage = _run(workspace)
    workspace.ingest_result(
        coverage["request"]["request_id"],
        success=True,
        output={
            "passed": False,
            "missed_claims": [
                {
                    "coordinate": "target_role",
                    "value": "bracketed_localization",
                    "quote": "localize a bracketed target",
                }
            ],
            "reason": "explicit target role was missed",
        },
        executor="reviewer:coverage",
    )
    reopened = _run(workspace)
    assert reopened["status"] == "CANNOT_CHECK_COVERAGE_GAP"
    assert reopened["coverage_review"]["passed"] is False
    assert reopened["coverage_review"]["missed_claims"][0]["coordinate"] == "target_role"
    assert reopened["grants_global_task_stop_authority"] is False


def test_invalid_reviewer_quote_is_host_capability_failure(tmp_path):
    (tmp_path / "paper.txt").write_text("First measure the midpoint.\n", encoding="utf-8")
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    claims = [{"coordinate": "mechanics", "value": "measure_midpoint", "quote": "measure the midpoint"}]
    first = _run(workspace)
    _ingest_llm(workspace, first, claims, executor="model:a")
    second = _run(workspace)
    _ingest_llm(workspace, second, claims, executor="model:b")
    coverage = _run(workspace)
    workspace.ingest_result(
        coverage["request"]["request_id"],
        success=True,
        output={
            "passed": False,
            "missed_claims": [
                {"coordinate": "target_role", "value": "invented", "quote": "quote not in source"}
            ],
            "reason": "bad reviewer fixture",
        },
        executor="reviewer:coverage",
    )
    failed = _run(workspace)
    assert failed["status"] == "HOST_CAPABILITY_FAILED"
    assert "quote" in failed["error"].casefold()


def test_invalid_quote_in_second_proposer_lane_is_rejected(tmp_path):
    (tmp_path / "paper.txt").write_text("First measure the midpoint.\n", encoding="utf-8")
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    first = _run(workspace)
    _ingest_llm(
        workspace,
        first,
        [{"coordinate": "mechanics", "value": "measure_midpoint", "quote": "measure the midpoint"}],
        executor="model:a",
    )
    second = _run(workspace)
    _ingest_llm(
        workspace,
        second,
        [{"coordinate": "mechanics", "value": "invented", "quote": "not present"}],
        executor="model:b",
    )
    failed = _run(workspace)
    assert failed["status"] == "HOST_CAPABILITY_FAILED"
    assert "quote" in failed["error"].casefold()
