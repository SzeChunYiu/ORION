#!/usr/bin/env python3
"""Run QG-6 analyzer through the generic harness and native ORION-Q admission."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts"
ANALYZER_PATH = ARTIFACTS / "orion-qg-qg6-syndrome-rank.json"
GENERIC_PATH = ARTIFACTS / "orion-qg-qg6-generic-verification.json"
DUAL_PATH = ARTIFACTS / "orion-qg-qg6-dual-harness.json"
GENERIC_WS = REPO_ROOT / ".orion-qg-qg6-generic"
NATIVE_WS = REPO_ROOT / ".orion-qg-qg6-native"
ANALYZER_PREFIX = "ORIONQG_QG6_SYNDROME_RANK="
GENERIC_PREFIX = "ORIONQG_QG6_GENERIC_VERIFY="


def _token(stdout: str, prefix: str) -> dict[str, Any]:
    rows = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected one {prefix} token, got {len(rows)}")
    payload = json.loads(rows[0][len(prefix) :])
    if not isinstance(payload, dict):
        raise TypeError("token payload must be an object")
    return payload


def _run_local(workspace: ResearchWorkspace, code: str, timeout: int = 180):
    request = workspace.get_or_create_request(
        capability="PYTHON", payload={"code": code, "cwd": ".", "timeout": timeout}
    )
    result = service_local_request(workspace, request.request_id)
    if not result.success:
        raise RuntimeError(f"QG-6 local capability failed: {result.error}")
    if not isinstance(result.output, dict) or result.output.get("returncode") != 0:
        raise RuntimeError("QG-6 local process did not exit cleanly")
    if result.output.get("sandboxed") is not False:
        raise RuntimeError("QG-6 process receipt must preserve sandboxed=false")
    return request, result


def main() -> int:
    for path in (GENERIC_WS, NATIVE_WS):
        if path.exists():
            shutil.rmtree(path)
    for path in (ANALYZER_PATH, GENERIC_PATH, DUAL_PATH):
        path.unlink(missing_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    generic_ws = ResearchWorkspace.initialize(
        GENERIC_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    analyzer_code = (
        "import runpy; runpy.run_path('research/extensions/orion-qg/"
        "qg6_syndrome_rank.py', run_name='__main__')"
    )
    analyzer_request, analyzer_result = _run_local(generic_ws, analyzer_code, timeout=240)
    analyzer_token = _token(str(analyzer_result.output.get("stdout", "")), ANALYZER_PREFIX)
    if not ANALYZER_PATH.is_file():
        raise FileNotFoundError(ANALYZER_PATH)
    analyzer = json.loads(ANALYZER_PATH.read_text(encoding="utf-8"))
    if analyzer_token.get("result_digest") != analyzer.get("result_digest"):
        raise ValueError("QG-6 analyzer stdout digest does not bind artifact")

    verifier_code = (
        "import runpy; runpy.run_path('development/orion-qg-regime-geometry/"
        "qg6_generic_verify.py', run_name='__main__')"
    )
    generic_request, generic_result = _run_local(generic_ws, verifier_code, timeout=240)
    generic_token = _token(str(generic_result.output.get("stdout", "")), GENERIC_PREFIX)
    if not GENERIC_PATH.is_file():
        raise FileNotFoundError(GENERIC_PATH)
    generic = json.loads(GENERIC_PATH.read_text(encoding="utf-8"))
    if generic_token.get("decision") != generic.get("decision"):
        raise ValueError("QG-6 generic token does not bind verification artifact")

    validate_manifest(QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST)
    native_ws = ResearchWorkspace.initialize(
        NATIVE_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    native_outcome = run_campaign(
        native_ws,
        QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    final_state = CampaignState.from_dict(
        native_ws.load_latest_campaign_state(
            QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST["campaign_id"]
        )
    )
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT",
        "REJECT_RECORDED": "REJECT",
    }.get(final_state.phase_id, "INCOMPLETE")

    positive_analyzer = (
        analyzer.get("terminal")
        == "QG6_PRODUCTION_SYNDROME_RANK_INFERENCE_VERIFIED__R6M_D2_RECOVERS_SUPPORT2__R6I_D5_FOUND_THEOREM_PENDING_QG1"
    )
    both_accept = generic.get("decision") == "ACCEPT" and native_decision == "ACCEPT"
    if positive_analyzer and both_accept:
        terminal = (
            "QG6_PRODUCTION_SYNDROME_RANK_INFERENCE_VERIFIED__"
            "R6M_D2_RECOVERS_SUPPORT2__R6I_D5_FOUND_THEOREM_PENDING_QG1"
        )
    elif generic.get("decision") != native_decision:
        terminal = "QG6_NATIVE_GENERIC_DISAGREEMENT"
    else:
        terminal = "QG6_PRODUCTION_RANK_OR_BINDING_REFUTED"

    dual = {
        "schema": "ORION.QG.QG6.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#756",
        "terminal": terminal,
        "source_result_digest": analyzer.get("result_digest"),
        "generic_lane": {
            "decision": generic.get("decision"),
            "verification": generic,
            "analyzer_request": analyzer_request.as_dict(),
            "analyzer_result": analyzer_result.as_dict(),
            "verifier_request": generic_request.as_dict(),
            "verifier_result": generic_result.as_dict(),
        },
        "native_lane": {
            "decision": native_decision,
            "outcome": native_outcome,
            "final_state": final_state.as_dict(),
        },
        "both_accept": both_accept,
        "r6m_dimension": analyzer.get("r6m", {}).get("auto_dimension"),
        "r6i_dimension": analyzer.get("r6i", {}).get("auto_dimension"),
        "r6i_theorem_promotion": "PENDING_QG1",
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    DUAL_PATH.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "analyzer": str(ANALYZER_PATH),
                "generic": str(GENERIC_PATH),
                "dual": str(DUAL_PATH),
                "terminal": terminal,
                "generic_decision": generic.get("decision"),
                "native_decision": native_decision,
                "r6m_dimension": dual["r6m_dimension"],
                "r6i_dimension": dual["r6i_dimension"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
