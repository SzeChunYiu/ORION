#!/usr/bin/env python3
"""Run QG-18 through independent generic and native ORION instruments."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
GW = ROOT / ".orion-qg-qg18-generic"
NW = ROOT / ".orion-qg-qg18-native"


def token(stdout: str, prefix: str):
    rows = [x for x in stdout.splitlines() if x.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError({"prefix": prefix, "count": len(rows)})
    return json.loads(rows[0][len(prefix):])


def run(ws: ResearchWorkspace, path: str, prefix: str, timeout: int = 180):
    req = ws.get_or_create_request(
        capability="PYTHON",
        payload={
            "code": f"import runpy;runpy.run_path({path!r},run_name='__main__')",
            "cwd": ".",
            "timeout": timeout,
        },
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
    names = (
        "orion-qg-qg18-intrinsic-support.json",
        "orion-qg-qg18-generic-verification.json",
        "orion-qg-qg18-native-verification.json",
        "orion-qg-qg18-dual-harness.json",
    )
    for name in names:
        p = ART / name
        if p.exists():
            p.unlink()

    gw = ResearchWorkspace.initialize(GW, project_root=ROOT, allow_process_tools=True)
    areq, ares, asum = run(
        gw,
        "research/extensions/orion-qg/qg18_tare_intrinsic_support.py",
        "ORIONQG_QG18=",
        180,
    )
    greq, gres, gsum = run(
        gw,
        "development/orion-qg-regime-geometry/qg18_generic_verify.py",
        "ORIONQG_QG18_GENERIC=",
        180,
    )
    a = json.loads((ART / "orion-qg-qg18-intrinsic-support.json").read_text())
    g = json.loads((ART / "orion-qg-qg18-generic-verification.json").read_text())
    if asum.get("result_digest") != a.get("result_digest"):
        raise AssertionError("QG18 analyzer digest mismatch")

    nw = ResearchWorkspace.initialize(NW, project_root=ROOT, allow_process_tools=True)
    nreq, nres, nsum = run(
        nw,
        "development/orion-qg-regime-geometry/qg18_native_verify.py",
        "ORIONQG_QG18_NATIVE=",
        60,
    )
    n = json.loads((ART / "orion-qg-qg18-native-verification.json").read_text())

    positive = a.get("terminal") == "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS"
    both_accept = (
        positive
        and g.get("decision") == "ACCEPT_KAPPA2"
        and g.get("all_checks") is True
        and n.get("decision") == "ACCEPT_KAPPA2"
        and n.get("all_checks") is True
        and g.get("source_result_digest") == a.get("result_digest")
        and n.get("source_result_digest") == a.get("result_digest")
    )
    terminal = a.get("terminal") if both_accept else "QG18_GENERIC_NATIVE_DISAGREEMENT"
    intrinsic = 2 if both_accept else None
    dual = {
        "schema": "ORIONQG.QG18.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#835",
        "terminal": terminal,
        "both_accept": both_accept,
        "intrinsic_support_conclusion": intrinsic,
        "source_result_digest": a.get("result_digest"),
        "support2_feasible_cost": a.get("support2_feasible_cost"),
        "cap1_cost": a.get("production_cap1_cost"),
        "strict_gap": a.get("strict_gap_cap1_minus_support2"),
        "derivation_kind": a.get("derivation_kind"),
        "generic_lane": {
            "decision": g.get("decision"),
            "analyzer_request": areq.as_dict(),
            "analyzer_result": ares.as_dict(),
            "verifier_request": greq.as_dict(),
            "verifier_result": gres.as_dict(),
            "verification": g,
        },
        "native_lane": {
            "decision": n.get("decision"),
            "request": nreq.as_dict(),
            "result": nres.as_dict(),
            "verification": n,
        },
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    (ART / "orion-qg-qg18-dual-harness.json").write_text(
        json.dumps(dual, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "terminal": terminal,
        "both_accept": both_accept,
        "intrinsic_support": intrinsic,
        "support2": dual["support2_feasible_cost"],
        "cap1": dual["cap1_cost"],
        "gap": dual["strict_gap"],
        "generic": g.get("decision"),
        "native": n.get("decision"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
