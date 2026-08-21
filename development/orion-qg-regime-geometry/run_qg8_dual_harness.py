#!/usr/bin/env python3
"""Drive QG-8 analyzer, independent generic verification, and native admission."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts"
ANALYZER = ARTIFACTS / "orion-qg-qg8-support-phase.json"
GENERIC = ARTIFACTS / "orion-qg-qg8-generic-verification.json"
DUAL = ARTIFACTS / "orion-qg-qg8-dual-harness.json"
GENERIC_WS = REPO_ROOT / ".orion-qg-qg8-generic"
NATIVE_WS = REPO_ROOT / ".orion-qg-qg8-native"
ANALYZER_PREFIX = "ORIONQG_QG8_SUPPORT_PHASE="
GENERIC_PREFIX = "ORIONQG_QG8_GENERIC_VERIFY="


def _token(stdout: str, prefix: str) -> dict[str, Any]:
    rows = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected one {prefix} token, got {len(rows)}")
    raw = json.loads(rows[0][len(prefix):])
    if not isinstance(raw, dict):
        raise TypeError("token must be object")
    return raw


def _run(ws: ResearchWorkspace, code: str, timeout: int = 180):
    req = ws.get_or_create_request(
        capability="PYTHON", payload={"code": code, "cwd": ".", "timeout": timeout}
    )
    res = service_local_request(ws, req.request_id)
    if not res.success:
        raise RuntimeError(f"QG-8 capability failed: {res.error}")
    if not isinstance(res.output, dict) or res.output.get("returncode") != 0:
        raise RuntimeError("QG-8 process did not exit cleanly")
    if res.output.get("sandboxed") is not False:
        raise RuntimeError("QG-8 process receipt must retain sandboxed=false")
    return req, res


def main() -> int:
    for path in (GENERIC_WS, NATIVE_WS):
        if path.exists():
            shutil.rmtree(path)
    for path in (ANALYZER, GENERIC, DUAL):
        path.unlink(missing_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    generic_ws = ResearchWorkspace.initialize(
        GENERIC_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    analyzer_code = (
        "import runpy; runpy.run_path('research/extensions/orion-qg/"
        "qg8_support_phase.py', run_name='__main__')"
    )
    a_req, a_res = _run(generic_ws, analyzer_code, timeout=180)
    a_token = _token(str(a_res.output.get("stdout", "")), ANALYZER_PREFIX)
    analyzer = json.loads(ANALYZER.read_text(encoding="utf-8"))
    if a_token.get("result_digest") != analyzer.get("result_digest"):
        raise ValueError("analyzer stdout digest does not bind artifact")

    verifier_code = (
        "import runpy; runpy.run_path('development/orion-qg-regime-geometry/"
        "qg8_generic_verify.py', run_name='__main__')"
    )
    g_req, g_res = _run(generic_ws, verifier_code, timeout=180)
    g_token = _token(str(g_res.output.get("stdout", "")), GENERIC_PREFIX)
    generic = json.loads(GENERIC.read_text(encoding="utf-8"))
    if g_token.get("decision") != generic.get("decision"):
        raise ValueError("generic token does not bind verification artifact")

    validate_manifest(QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST)
    native_ws = ResearchWorkspace.initialize(
        NATIVE_WS, project_root=REPO_ROOT, allow_process_tools=True
    )
    outcome = run_campaign(
        native_ws, QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST,
        max_cycles=4, auto_service_local=True,
    )
    final = CampaignState.from_dict(
        native_ws.load_latest_campaign_state(QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST["campaign_id"])
    )
    native_decision = {
        "ACCEPT_RECORDED": "ACCEPT",
        "REJECT_RECORDED": "REJECT",
    }.get(final.phase_id, "INCOMPLETE")

    positive = analyzer.get("terminal") == "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED"
    both_accept = generic.get("decision") == "ACCEPT" and native_decision == "ACCEPT"
    if positive and both_accept:
        terminal = "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED"
    elif generic.get("decision") != native_decision:
        terminal = "QG8_NATIVE_GENERIC_DISAGREEMENT"
    else:
        terminal = "QG8_RESOURCE_VECTOR_OR_BINDING_REFUTED"

    dual = {
        "schema": "ORION.QG.QG8.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#760",
        "terminal": terminal,
        "source_result_digest": analyzer.get("result_digest"),
        "generic_lane": {
            "decision": generic.get("decision"),
            "verification": generic,
            "analyzer_request": a_req.as_dict(),
            "analyzer_result": a_res.as_dict(),
            "verifier_request": g_req.as_dict(),
            "verifier_result": g_res.as_dict(),
        },
        "native_lane": {
            "decision": native_decision,
            "outcome": outcome,
            "final_state": final.as_dict(),
        },
        "both_accept": both_accept,
        "outside_cone_semantics": "NOT_EQUAL_SUPPORT3_REQUIRED",
        "global_boundary_sharpness": "OPEN",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    DUAL.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "analyzer": str(ANALYZER),
        "generic": str(GENERIC),
        "dual": str(DUAL),
        "terminal": terminal,
        "generic_decision": generic.get("decision"),
        "native_decision": native_decision,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
