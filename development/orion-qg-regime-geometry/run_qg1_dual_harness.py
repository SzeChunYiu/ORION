#!/usr/bin/env python3
"""Execute QG-1 theorem check through generic and native ORION-Q harnesses."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG1_SUPPORT5_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts"
THEOREM_PATH = ARTIFACTS / "orion-qg-qg1-support5-theorem.json"
GENERIC_VERIFY_PATH = ARTIFACTS / "orion-qg-qg1-generic-verification.json"
DUAL_PATH = ARTIFACTS / "orion-qg-qg1-dual-harness.json"
GENERIC_WS = REPO_ROOT / ".orion-qg-qg1-generic"
NATIVE_WS = REPO_ROOT / ".orion-qg-qg1-native"
THEOREM_PREFIX = "ORIONQG_QG1_THEOREM="
GENERIC_PREFIX = "ORIONQG_QG1_GENERIC_VERIFY="
POSITIVE = "QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED"


def token(stdout: str, prefix: str) -> dict[str, Any]:
    rows = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected one {prefix} token, got {len(rows)}")
    value = json.loads(rows[0][len(prefix) :])
    if not isinstance(value, dict):
        raise TypeError("token payload must be object")
    return value


def run_local(workspace: ResearchWorkspace, code: str, timeout: int = 120):
    request = workspace.get_or_create_request(
        capability="PYTHON", payload={"code": code, "cwd": ".", "timeout": timeout}
    )
    result = service_local_request(workspace, request.request_id)
    if not result.success:
        raise RuntimeError(f"QG-1 local capability failed: {result.error}")
    if not isinstance(result.output, dict) or result.output.get("returncode") != 0:
        raise RuntimeError("QG-1 local capability did not complete cleanly")
    if result.output.get("sandboxed") is not False:
        raise RuntimeError("QG-1 process receipt lost sandboxed=false fact")
    return request, result


def generic_decision(theorem: dict[str, Any], verification: dict[str, Any]) -> str:
    checks = verification.get("checks", {})
    custody_keys = (
        "result_digest_valid",
        "frozen_base_exact",
        "protocol_hash_exact",
        "novelty_hash_exact",
        "no_chemistry_access",
        "novelty_authority_false",
        "physical_advantage_false",
    )
    if not all(checks.get(key) is True for key in custody_keys):
        return "CANNOT_CHECK"
    if verification.get("verification_pass") is True and theorem.get("terminal") == POSITIVE:
        return "ACCEPT"
    return "REJECT"


def main() -> int:
    for path in (GENERIC_WS, NATIVE_WS):
        if path.exists():
            shutil.rmtree(path)
    for path in (THEOREM_PATH, GENERIC_VERIFY_PATH, DUAL_PATH):
        path.unlink(missing_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    generic_ws = ResearchWorkspace.initialize(
        GENERIC_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    checker_code = (
        "import runpy; runpy.run_path('research/extensions/orion-qg/"
        "qg1_rank2_support5.py', run_name='__main__')"
    )
    theorem_request, theorem_result = run_local(generic_ws, checker_code)
    theorem_summary = token(str(theorem_result.output.get("stdout", "")), THEOREM_PREFIX)
    theorem = json.loads(THEOREM_PATH.read_text(encoding="utf-8"))
    if theorem_summary.get("result_digest") != theorem.get("result_digest"):
        raise ValueError("theorem stdout digest does not bind theorem artifact")

    verify_code = (
        "import runpy; runpy.run_path('development/orion-qg-regime-geometry/"
        "qg1_generic_verify.py', run_name='__main__')"
    )
    verify_request, verify_result = run_local(generic_ws, verify_code)
    verification_token = token(str(verify_result.output.get("stdout", "")), GENERIC_PREFIX)
    verification = json.loads(GENERIC_VERIFY_PATH.read_text(encoding="utf-8"))
    if verification_token != verification:
        raise ValueError("generic verification token differs from serialized artifact")
    lane_a_decision = generic_decision(theorem, verification)

    validate_manifest(QG1_SUPPORT5_CAMPAIGN_MANIFEST)
    native_ws = ResearchWorkspace.initialize(
        NATIVE_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    native_outcome = run_campaign(
        native_ws,
        QG1_SUPPORT5_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    final_state = CampaignState.from_dict(
        native_ws.load_latest_campaign_state(QG1_SUPPORT5_CAMPAIGN_MANIFEST["campaign_id"])
    )
    native_map = {
        "ACCEPT_RECORDED": "ACCEPT",
        "REJECT_RECORDED": "REJECT",
        "CANNOT_RECORDED": "CANNOT_CHECK",
    }
    lane_b_decision = native_map.get(final_state.phase_id, "INCOMPLETE")
    native_digest = final_state.observation_map.get("QG1_RESULT_DIGEST", "")
    if native_digest != theorem.get("result_digest"):
        raise ValueError("native ORION-Q lane not bound to current theorem digest")

    if lane_a_decision == "ACCEPT" and lane_b_decision == "ACCEPT":
        terminal = POSITIVE
    elif "CANNOT_CHECK" in {lane_a_decision, lane_b_decision} or "INCOMPLETE" in {
        lane_a_decision,
        lane_b_decision,
    }:
        terminal = "QG1_CANNOT_CHECK"
    elif lane_a_decision != lane_b_decision:
        terminal = "QG1_DUAL_HARNESS_DISAGREEMENT"
    else:
        terminal = "QG1_MACHINE_THEOREM_REJECTED"

    dual = {
        "schema": "ORION.QG.QG1.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#747",
        "terminal": terminal,
        "theorem_result_digest": theorem.get("result_digest"),
        "generic_lane": {
            "decision": lane_a_decision,
            "theorem_request": theorem_request.as_dict(),
            "theorem_result": theorem_result.as_dict(),
            "verification_request": verify_request.as_dict(),
            "verification_result": verify_result.as_dict(),
            "verification": verification,
        },
        "native_lane": {
            "decision": lane_b_decision,
            "outcome": native_outcome,
            "final_state": final_state.as_dict(),
        },
        "both_accept": lane_a_decision == "ACCEPT" and lane_b_decision == "ACCEPT",
        "chemistry_sources_read": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    DUAL_PATH.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "theorem_result_digest": theorem.get("result_digest"),
                "local_case_count": theorem.get("local", {}).get("case_count"),
                "max_delta": theorem.get("local", {}).get("max_delta"),
                "abstract_multiset_count": theorem.get("f2_5", {}).get("multiset_count"),
                "boundary_rank": theorem.get("f2_5", {}).get("boundary_rank"),
                "generic_decision": lane_a_decision,
                "native_decision": lane_b_decision,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
