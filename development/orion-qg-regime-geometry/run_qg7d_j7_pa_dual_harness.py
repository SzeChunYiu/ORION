#!/usr/bin/env python3
"""Execute the frozen QG-7d J7 PA packet through generic and native ORION."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
GW = ROOT / ".orion-qg-qg7d-j7-generic"
NW = ROOT / ".orion-qg-qg7d-j7-native"
POSITIVE = "QG7D_PA_PINNED_COMM_S2_CLOSED_ALL_N_MACHINE_CHECKED__PP_CHAIN_OPEN"


def parse(stdout: str, prefix: str):
    rows = [x for x in stdout.splitlines() if x.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError({"prefix": prefix, "count": len(rows)})
    return json.loads(rows[0][len(prefix):])


def run(ws: ResearchWorkspace, path: str, prefix: str, timeout: int = 240):
    req = ws.get_or_create_request(
        capability="PYTHON",
        payload={"code": f"import runpy;runpy.run_path({path!r},run_name='__main__')",
                 "cwd": ".", "timeout": timeout},
    )
    res = service_local_request(ws, req.request_id)
    if not res.success or not isinstance(res.output, dict) or res.output.get("returncode") != 0:
        raise RuntimeError({"path": path, "error": res.error, "output": res.output})
    return req, res, parse(str(res.output.get("stdout", "")), prefix)


def main() -> int:
    for p in (GW, NW):
        if p.exists():
            shutil.rmtree(p)
    ART.mkdir(exist_ok=True)
    for name in (
        "orion-qg-qg7d-j7-pa-confirm.json",
        "orion-qg-qg7d-j7-pa-generic-verification.json",
        "orion-qg-qg7d-j7-pa-native-verification.json",
        "orion-qg-qg7d-j7-pa-dual-harness.json",
    ):
        p = ART / name
        if p.exists():
            p.unlink()

    gw = ResearchWorkspace.initialize(GW, project_root=ROOT, allow_process_tools=True)
    areq, ares, asum = run(
        gw, "development/orion-qg-regime-geometry/qg7d_j7_analyzer_exec.py",
        "ORIONQG_QG7D_J7=", 240)
    greq, gres, gsum = run(
        gw, "development/orion-qg-regime-geometry/qg7d_j7_generic_exec.py",
        "ORIONQG_QG7D_J7_GENERIC=", 240)
    a = json.loads((ART / "orion-qg-qg7d-j7-pa-confirm.json").read_text())
    g = json.loads((ART / "orion-qg-qg7d-j7-pa-generic-verification.json").read_text())
    if asum.get("result_digest") != a.get("result_digest"):
        raise AssertionError("QG7d J7 analyzer digest token mismatch")

    nw = ResearchWorkspace.initialize(NW, project_root=ROOT, allow_process_tools=True)
    nreq, nres, nsum = run(
        nw, "development/orion-qg-regime-geometry/qg7d_j7_pa_native_verify.py",
        "ORIONQG_QG7D_J7_NATIVE=", 60)
    n = json.loads((ART / "orion-qg-qg7d-j7-pa-native-verification.json").read_text())

    both = (
        a.get("terminal") == POSITIVE and a.get("all_gates") is True
        and g.get("decision") == "ACCEPT_PA_ALL_N_CLOSURE" and g.get("all_checks") is True
        and n.get("decision") == "ACCEPT_PA_ALL_N_CLOSURE" and n.get("all_checks") is True
        and g.get("source_result_digest") == a.get("result_digest") == n.get("source_result_digest")
    )
    terminal = a.get("terminal") if both else "QG7D_GENERIC_NATIVE_DISAGREEMENT"
    dual = {
        "schema": "ORIONQG.QG7D.J7PADualHarness.v1",
        "issue": "SzeChunYiu/ORION#836",
        "terminal": terminal,
        "both_accept": both,
        "source_result_digest": a.get("result_digest"),
        "parent_pa_failures": a.get("parent", {}).get("pa_failures"),
        "j6_residuals": a.get("j6", {}).get("residual_count"),
        "j7_final_residuals": a.get("j7_bprime", {}).get("final_residuals"),
        "bprime_delta_histogram": a.get("j7_bprime", {}).get("delta_histogram"),
        "generic_lane": {"summary": gsum, "request": greq.as_dict(), "result": gres.as_dict(), "verification": g},
        "native_lane": {"summary": nsum, "request": nreq.as_dict(), "result": nres.as_dict(), "verification": n},
        "analyzer_request": areq.as_dict(),
        "analyzer_result": ares.as_dict(),
        "PA_ALL_N": both,
        "PP_ALL_N": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    (ART / "orion-qg-qg7d-j7-pa-dual-harness.json").write_text(
        json.dumps(dual, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": terminal, "both_accept": both,
        "parent_failures": dual["parent_pa_failures"],
        "j6_residuals": dual["j6_residuals"],
        "j7_residuals": dual["j7_final_residuals"],
        "bprime_delta_histogram": dual["bprime_delta_histogram"],
        "generic": g.get("decision"), "native": n.get("decision"),
        "PA_ALL_N": dual["PA_ALL_N"], "PP_ALL_N": False, "CHAIN_ALL_N": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
