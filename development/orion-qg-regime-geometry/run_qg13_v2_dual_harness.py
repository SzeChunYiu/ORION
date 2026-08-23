#!/usr/bin/env python3
"""Run QG-13 V2 through generic ORION and native ORION-Q harnesses."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

REPO_ROOT = Path(__file__).resolve().parents[2]
ART = REPO_ROOT / "artifacts"
GEN = REPO_ROOT / ".orion-qg-qg13v2-generic"
NAT = REPO_ROOT / ".orion-qg-qg13v2-native"
A_PATH = ART / "orion-qg-qg13v2-combined-edit.json"
G_PATH = ART / "orion-qg-qg13v2-generic-verification.json"
D_PATH = ART / "orion-qg-qg13v2-dual-harness.json"


def run_local(ws, code, timeout=120):
    req = ws.get_or_create_request(capability="PYTHON", payload={"code": code, "cwd": ".", "timeout": timeout})
    res = service_local_request(ws, req.request_id)
    if not res.success:
        raise RuntimeError(res.error)
    if not isinstance(res.output, dict) or res.output.get("returncode") != 0:
        raise RuntimeError("local process failed")
    if res.output.get("sandboxed") is not False:
        raise RuntimeError("process receipt must preserve sandboxed=false")
    return req, res


def main():
    for p in (GEN, NAT):
        if p.exists(): shutil.rmtree(p)
    for p in (A_PATH, G_PATH, D_PATH): p.unlink(missing_ok=True)
    ART.mkdir(parents=True, exist_ok=True)

    ws = ResearchWorkspace.initialize(GEN, project_root=REPO_ROOT, allow_process_tools=True)
    a_req, a_res = run_local(ws, "import runpy;runpy.run_path('research/extensions/orion-qg/qg13_v2_combined_edit.py',run_name='__main__')", 120)
    if not A_PATH.is_file(): raise FileNotFoundError(A_PATH)
    g_req, g_res = run_local(ws, "import runpy;runpy.run_path('development/orion-qg-regime-geometry/qg13_v2_generic_verify.py',run_name='__main__')", 120)
    if not G_PATH.is_file(): raise FileNotFoundError(G_PATH)

    analyzer = json.loads(A_PATH.read_text())
    generic = json.loads(G_PATH.read_text())
    validate_manifest(QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST)
    nws = ResearchWorkspace.initialize(NAT, project_root=REPO_ROOT, allow_process_tools=True)
    outcome = run_campaign(nws, QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST, max_cycles=4, auto_service_local=True)
    state = CampaignState.from_dict(nws.load_latest_campaign_state(QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST["campaign_id"]))
    phase_map = {
        "CANDIDATE_RECORDED": "ACCEPT_SUPPORT4_CANDIDATE",
        "OBSTRUCTION_RECORDED": "ACCEPT_MINIMAL_OBSTRUCTION",
        "RESOURCE_RECORDED": "ACCEPT_RESOURCE_BOUNDARY",
        "REJECT_RECORDED": "REJECT",
    }
    native = phase_map.get(state.phase_id, "INCOMPLETE")
    accepted = generic.get("decision") == "ACCEPT" and native.startswith("ACCEPT_")
    terminal = analyzer.get("terminal") if accepted else "QG13V2_NATIVE_GENERIC_DISAGREEMENT"
    dual = {
        "schema": "ORION.QG.QG13V2.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#777",
        "terminal": terminal,
        "both_accept": accepted,
        "generic_lane": {
            "decision": generic.get("decision"),
            "analyzer_request": a_req.as_dict(), "analyzer_result": a_res.as_dict(),
            "verifier_request": g_req.as_dict(), "verifier_result": g_res.as_dict(),
        },
        "native_lane": {"decision": native, "outcome": outcome, "final_state": state.as_dict()},
        "new_theorem_authority": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    D_PATH.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": terminal, "generic": generic.get("decision"), "native": native,
        "support5": analyzer.get("obstruction_census", {}).get("support5_irreducible_patterns"),
        "covered": analyzer.get("obstruction_census", {}).get("covered_by_globally_safe_e2"),
        "uncovered": analyzer.get("obstruction_census", {}).get("uncovered_support5_patterns"),
    }, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
