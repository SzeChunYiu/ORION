#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import run_campaign
from orion_research_harness.domains.orion_qg import QG12_SIXLCU_P0_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
A = ART / "orion-qg-qg12-sixlcu-p0-theorem.json"
G = ART / "orion-qg-qg12-generic-verification.json"
D = ART / "orion-qg-qg12-dual-harness.json"
GWS = ROOT / ".orion-qg-qg12-generic"
NWS = ROOT / ".orion-qg-qg12-native"


def run_py(ws: ResearchWorkspace, code: str, timeout: int):
    req = ws.get_or_create_request(
        capability="PYTHON",
        payload={"code": code, "cwd": ".", "timeout": timeout},
    )
    res = service_local_request(ws, req.request_id)
    if not res.success:
        raise RuntimeError(res.error)
    if not isinstance(res.output, dict) or res.output.get("returncode") != 0:
        raise RuntimeError("QG12 process failed")
    if res.output.get("sandboxed") is not False:
        raise RuntimeError("sandboxed fact missing")
    return req, res


def main() -> int:
    for p in (GWS, NWS):
        if p.exists(): shutil.rmtree(p)
    for p in (A, G, D): p.unlink(missing_ok=True)
    ART.mkdir(parents=True, exist_ok=True)

    gws = ResearchWorkspace.initialize(GWS, project_root=ROOT, allow_process_tools=True)
    a_req, a_res = run_py(
        gws,
        "import runpy; runpy.run_path('research/extensions/orion-qg/qg12_sixlcu_p0_theorem.py', run_name='__main__')",
        1200,
    )
    analyzer = json.loads(A.read_text())
    if analyzer.get("terminal") is None:
        raise ValueError("analyzer terminal missing")

    g_req, g_res = run_py(
        gws,
        "import runpy; runpy.run_path('development/orion-qg-regime-geometry/qg12_generic_verify.py', run_name='__main__')",
        1200,
    )
    generic = json.loads(G.read_text())

    validate_manifest(QG12_SIXLCU_P0_CAMPAIGN_MANIFEST)
    nws = ResearchWorkspace.initialize(NWS, project_root=ROOT, allow_process_tools=True)
    outcome = run_campaign(
        nws,
        QG12_SIXLCU_P0_CAMPAIGN_MANIFEST,
        max_cycles=4,
        auto_service_local=True,
    )
    final = CampaignState.from_dict(
        nws.load_latest_campaign_state(QG12_SIXLCU_P0_CAMPAIGN_MANIFEST["campaign_id"])
    )
    native = {
        "ACCEPT_RECORDED": "ACCEPT",
        "REJECT_RECORDED": "REJECT",
    }.get(final.phase_id, "INCOMPLETE")

    positive = analyzer.get("terminal") == "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED"
    both = generic.get("decision") == "ACCEPT" and native == "ACCEPT"
    if positive and both:
        terminal = "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED"
    elif generic.get("decision") != native:
        terminal = "QG12_NATIVE_GENERIC_DISAGREEMENT"
    else:
        terminal = "QG12_P0_THEOREM_OR_BINDING_REFUTED"

    dual = {
        "schema": "ORION.QG.QG12.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#765",
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
            "decision": native,
            "outcome": outcome,
            "final_state": final.as_dict(),
        },
        "both_accept": both,
        "scope": "SIXLCU_ONLY",
        "cross_family_transfer": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    D.write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "generic": generic.get("decision"), "native": native}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
