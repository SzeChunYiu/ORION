#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
GW = ROOT / ".orion-qg-qg16-generic"
NW = ROOT / ".orion-qg-qg16-native"


def token(stdout: str, prefix: str):
    rows = [r for r in stdout.splitlines() if r.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError({"prefix": prefix, "rows": len(rows)})
    return json.loads(rows[0][len(prefix):])


def run(ws, path: str, prefix: str, timeout: int = 120):
    req = ws.get_or_create_request(
        capability="PYTHON",
        payload={"code": f"import runpy;runpy.run_path({path!r},run_name='__main__')", "cwd": ".", "timeout": timeout},
    )
    res = service_local_request(ws, req.request_id)
    if not res.success or not isinstance(res.output, dict) or res.output.get("returncode") != 0:
        raise RuntimeError({"path": path, "error": res.error, "output": res.output})
    return req, res, token(str(res.output.get("stdout", "")), prefix)


def main() -> int:
    for p in (GW, NW):
        if p.exists():
            shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for name in (
        "orion-qg-qg16-r6i-support1-phase.json",
        "orion-qg-qg16-generic-verification.json",
        "orion-qg-qg16-native-verification.json",
        "orion-qg-qg16-dual-harness.json",
    ):
        p = ART / name
        if p.exists():
            p.unlink()

    gw = ResearchWorkspace.initialize(GW, project_root=ROOT, allow_process_tools=True)
    areq, ares, asum = run(gw, "research/extensions/orion-qg/qg16_r6i_support1_phase.py", "ORIONQG_QG16=")
    greq, gres, gsum = run(gw, "development/orion-qg-regime-geometry/qg16_generic_verify.py", "ORIONQG_QG16_GENERIC=")

    result = json.loads((ART / "orion-qg-qg16-r6i-support1-phase.json").read_text())
    generic = json.loads((ART / "orion-qg-qg16-generic-verification.json").read_text())
    if asum.get("result_digest") != result.get("result_digest"):
        raise AssertionError("analyzer stdout/file digest mismatch")

    nw = ResearchWorkspace.initialize(NW, project_root=ROOT, allow_process_tools=True)
    nreq, nres, nsum = run(nw, "development/orion-qg-regime-geometry/qg16_native_verify.py", "ORIONQG_QG16_NATIVE=")
    native = json.loads((ART / "orion-qg-qg16-native-verification.json").read_text())

    positive = result.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED"
    both = generic.get("decision") == "ACCEPT_SUPPORT1_PHASE" and native.get("decision") == "ACCEPT_SUPPORT1_PHASE"
    terminal = result.get("terminal") if positive and both else "QG16_R6I_SUPPORT1_PHASE_GENERIC_NATIVE_DISAGREEMENT"
    dual = {
        "schema": "ORION.QG.QG16.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#811",
        "terminal": terminal,
        "source_result_digest": result.get("result_digest"),
        "both_accept": both,
        "positive": positive,
        "support_bound_inside_cone": result.get("support_bound_inside_cone"),
        "generic_lane": {
            "decision": generic.get("decision"),
            "analyzer_request": areq.as_dict(),
            "analyzer_result": ares.as_dict(),
            "verifier_request": greq.as_dict(),
            "verifier_result": gres.as_dict(),
            "verification": generic,
        },
        "native_lane": {
            "decision": native.get("decision"),
            "request": nreq.as_dict(),
            "result": nres.as_dict(),
            "verification": native,
        },
        "outside_cone_semantics": "NOT_EQUAL_SUPPORT2_REQUIRED",
        "global_phase_boundary_sharpness": "OPEN",
        "support1_phase_authority": both and positive,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    (ART / "orion-qg-qg16-dual-harness.json").write_text(json.dumps(dual, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "both_accept": both, "worst_vectors": result.get("commuting_deletion_resources", {}).get("worst_vectors"), "O0_inside": result.get("controls", {}).get("O0", {}).get("inside"), "O0_boundary": result.get("controls", {}).get("O0", {}).get("on_boundary")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
