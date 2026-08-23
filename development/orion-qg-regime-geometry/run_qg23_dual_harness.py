#!/usr/bin/env python3
"""Run QG-23 production, generic ORION, and native ORION-Q through isolated harness workspaces."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
GW = ROOT / ".orion-qg-qg23-generic"
NW = ROOT / ".orion-qg-qg23-native"
POS = "QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED"


def parse(stdout: str, prefix: str):
    rows = [r for r in stdout.splitlines() if r.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError((prefix, len(rows)))
    return json.loads(rows[0][len(prefix):])


def run(ws, path: str, prefix: str, timeout: int = 120):
    req = ws.get_or_create_request(
        capability="PYTHON",
        payload={"code": f"import runpy;runpy.run_path({path!r},run_name='__main__')", "cwd": ".", "timeout": timeout},
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
        "orion-qg-qg23-aux-support-compactness.json",
        "orion-qg-qg23-generic-verification.json",
        "orion-qg-qg23-native-verification.json",
        "orion-qg-qg23-dual-harness.json",
    ):
        p = ART / name
        if p.exists():
            p.unlink()

    gw = ResearchWorkspace.initialize(GW, project_root=ROOT, allow_process_tools=True)
    ar, ao, at = run(gw, "research/extensions/orion-qg/qg23_aux_support_compactness.py", "ORIONQG_QG23=")
    gr, go, gt = run(gw, "development/orion-qg-regime-geometry/qg23_generic_verify.py", "ORIONQG_QG23_GENERIC=")

    a = json.loads((ART / "orion-qg-qg23-aux-support-compactness.json").read_text())
    g = json.loads((ART / "orion-qg-qg23-generic-verification.json").read_text())
    if at.get("result_digest") != a.get("result_digest"):
        raise AssertionError("analyzer token/result digest mismatch")

    nw = ResearchWorkspace.initialize(NW, project_root=ROOT, allow_process_tools=True)
    nr, no, nt = run(nw, "development/orion-qg-regime-geometry/qg23_native_verify.py", "ORIONQG_QG23_NATIVE=")
    n = json.loads((ART / "orion-qg-qg23-native-verification.json").read_text())

    both = (
        a.get("terminal") == POS
        and a.get("auxiliary_support_compactness_authority") is True
        and g.get("decision") == "ACCEPT_AUXILIARY_SUPPORT_COMPACTNESS"
        and g.get("all_checks") is True
        and n.get("decision") == "ACCEPT_AUXILIARY_SUPPORT_COMPACTNESS"
        and n.get("all_checks") is True
        and g.get("source_result_digest") == a.get("result_digest") == n.get("source_result_digest")
    )
    terminal = POS if both else "QG23_GENERIC_NATIVE_DISAGREEMENT"
    out = {
        "schema": "ORIONQG.QG23.DualHarness.v1",
        "issue": "SzeChunYiu/ORION#879",
        "terminal": terminal,
        "both_accept": bool(both),
        "source_result_digest": a.get("result_digest"),
        "maximum_auxiliary_support": a.get("maximum_auxiliary_support"),
        "shape_rows": len(a.get("shape_count_lattice", [])),
        "generic": {"summary": gt, "verification": g},
        "native": {"summary": nt, "verification": n},
        "AUXILIARY_SUPPORT_COMPACTNESS": bool(both),
        "FULL_STATE_DIMENSION_6": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "FIFTH_REGIME_FOUND": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    (ART / "orion-qg-qg23-dual-harness.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": terminal,
        "both_accept": both,
        "max_auxiliary_support": out["maximum_auxiliary_support"],
        "shape_rows": out["shape_rows"],
        "generic": g.get("decision"),
        "native": n.get("decision"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
