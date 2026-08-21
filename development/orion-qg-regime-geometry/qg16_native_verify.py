#!/usr/bin/env python3
"""Native ORION-Q bounded admission for QG-16 objective-indexed support1 phase."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg16-r6i-support1-phase.json"
GENERIC = ROOT / "artifacts/orion-qg-qg16-generic-verification.json"
V6 = ROOT / "development/orion-qg-regime-geometry/QG9_V6_PROTECTED_RUN_RECEIPT_2026-08-21.json"
OUT = ROOT / "artifacts/orion-qg-qg16-native-verification.json"
TOKEN = "ORIONQG_QG16_NATIVE="


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    a = json.loads(RESULT.read_text())
    g = json.loads(GENERIC.read_text())
    p = json.loads(V6.read_text())
    checks = {
        "parent_support1_protected": p.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED" and p.get("both_accept") is True and p.get("support_bound") == 1,
        "positive_terminal": a.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED",
        "all_production_gates": all(a.get("gates", {}).values()),
        "generic_accept": g.get("decision") == "ACCEPT_SUPPORT1_PHASE" and g.get("all_checks") is True,
        "worst_vectors": a.get("commuting_deletion_resources", {}).get("worst_vectors") == [[0, 2, 2], [1, 1, 2]],
        "four_facets": len(a.get("facets", [])) == 4,
        "unit_inside_boundary": a.get("controls", {}).get("O0", {}).get("inside") is True and a.get("controls", {}).get("O0", {}).get("on_boundary") is True,
        "interior_control": a.get("controls", {}).get("O_in", {}).get("strict_interior") is True,
        "outside_controls": all(a.get("controls", {}).get(k, {}).get("inside") is False for k in ("O_tag_out", "O_restore_out", "O_nc_out")),
        "outside_not_support2": a.get("outside_cone_semantics") == "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED",
        "sharpness_open": a.get("global_phase_boundary_sharpness") == "OPEN",
        "inside_support_one": a.get("support_bound_inside_cone") == 1 and a.get("intrinsic_support_number_inside_cone") == 1,
        "no_novelty": a.get("novelty_authority") is False,
        "no_physical_advantage": a.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_SUPPORT1_PHASE" if all(checks.values()) else "REJECT"
    out = {
        "schema": "ORION.QG.QG16.NativeVerification.v1",
        "issue": "SzeChunYiu/ORION#811",
        "responsibility": "SUPPORT1_PHASE_CERTIFICATE" if decision.startswith("ACCEPT") else "CANNOT_CHECK",
        "decision": decision,
        "checks": checks,
        "all_checks": all(checks.values()),
        "terminal": a.get("terminal"),
        "support1_phase_authority": decision == "ACCEPT_SUPPORT1_PHASE",
        "outside_cone_semantics": "NOT_EQUAL_SUPPORT2_REQUIRED",
        "global_phase_boundary_sharpness": "OPEN",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
