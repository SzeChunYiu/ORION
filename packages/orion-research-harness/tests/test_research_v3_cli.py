from __future__ import annotations

import json

from orion_research_harness.paper_cli import main
from orion_research_harness.workspace import ResearchWorkspace


def test_research_direct_cli_routes_verified_answer_to_saturation(capsys):
    code = main(
        [
            "research-direct",
            "--json",
            json.dumps({"solution_status": "SOLVED_VERIFIED", "residuals": []}),
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "ASSESS_SATURATION"
    assert payload["grants_global_task_stop_authority"] is False


def test_consensus_extractor_is_host_callable_and_starts_with_lane_a(tmp_path, capsys):
    (tmp_path / "paper.txt").write_text("First measure the midpoint.\n", encoding="utf-8")
    ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    code = main(
        [
            "paper-structure-consensus",
            str(tmp_path / "ws"),
            "paper.txt",
            "method:x",
            "--source-id",
            "paper:x",
        ]
    )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PENDING_CAPABILITY"
    assert payload["extraction_mode"] == "TWO_LANE_CONSENSUS_V3"
    assert payload["request"]["capability"] == "LLM_COMPLETE"
    assert payload["request"]["payload"]["task"] == "paper_method_structure_extract_v2_lane_a"


def test_v3_conformance_cli_is_green(capsys):
    code = main(["research-v3-conformance"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["terminal"] == "ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL"
    assert payload["operational"] is True
