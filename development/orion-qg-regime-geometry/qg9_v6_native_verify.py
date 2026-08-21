#!/usr/bin/env python3
"""Native ORION-Q bounded admission for QG-9 V6 support-1 theorem."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg9-v6-support1-normalization.json"
GENERIC = ROOT / "artifacts/orion-qg-qg9-v6-generic-verification.json"
PARENT = ROOT / "development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json"
OUT = ROOT / "artifacts/orion-qg-qg9-v6-native-verification.json"
TOKEN = "ORIONQG_QG9_V6_NATIVE="


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    a = json.loads(RESULT.read_text())
    g = json.loads(GENERIC.read_text())
    p = json.loads(PARENT.read_text())
    comp = a.get("composition_audit", {})
    checks = {
        "parent_support2_protected": p.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED" and p.get("both_accept") is True,
        "positive_terminal": a.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED",
        "all_production_gates": all(a.get("gates", {}).values()),
        "generic_accept": g.get("decision") == "ACCEPT_SUPPORT1_THEOREM" and g.get("all_checks") is True,
        "support_bound_one": a.get("support_bound") == 1,
        "kappa_one": a.get("intrinsic_support_number") == 1,
        "support0_infeasible": a.get("support0_infeasible") is True,
        "L1_credit": a.get("deletion_lemma", {}).get("max_delta") == {"commuting": -4, "anticommuting": -7},
        "L2_alignment": a.get("core_alignment_lemma", {}).get("max_restore_objective_increase") == 3,
        "L3_tag": a.get("tag_lemmas", {}).get("canonical_dual_all_nonzero") is True and a.get("tag_lemmas", {}).get("distinct_qubit_tag", {}).get("all_minima_8") is True,
        "L4_distinct_core": comp.get("distinct_non_support_case_closes") is True and comp.get("distinct_both_support1_case_closes") is True,
        "L5_same_core": comp.get("same_core_tag_nonincrease") is True and comp.get("same_core_alignment_paid") is True and comp.get("same_core_support1_rigidity") is True,
        "stress_is_only_corroboration": a.get("stress", {}).get("all_pass") is True,
        "no_self_novelty": a.get("new_theorem_authority") is False and a.get("novelty_authority") is False,
        "no_physical_advantage": a.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_SUPPORT1_THEOREM" if all(checks.values()) else "REJECT"
    out = {
        "schema": "ORION.QG.QG9.V6.NativeVerification.v1",
        "issue": "SzeChunYiu/ORION#807",
        "responsibility": "SUPPORT1_THEOREM" if decision.startswith("ACCEPT") else "CANNOT_CHECK",
        "decision": decision,
        "checks": checks,
        "all_checks": all(checks.values()),
        "terminal": a.get("terminal"),
        "support1_authority": decision == "ACCEPT_SUPPORT1_THEOREM",
        "tightness_by_support0_infeasibility": decision == "ACCEPT_SUPPORT1_THEOREM",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
