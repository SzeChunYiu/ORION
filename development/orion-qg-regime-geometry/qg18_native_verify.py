#!/usr/bin/env python3
"""Native ORION-Q responsibility verifier for QG-18.

This lane does not redo the primitive mathematics (generic ORION owns that).
It fail-closes the parent bindings, exact strict-gap responsibility, authority
ceiling, and agreement between the production-side receipt binder and the
independent generic verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANALYZER = ROOT / "artifacts/orion-qg-qg18-intrinsic-support.json"
DEFAULT_GENERIC = ROOT / "artifacts/orion-qg-qg18-generic-verification.json"
DEFAULT_OUTPUT = ROOT / "artifacts/orion-qg-qg18-native-verification.json"
TOKEN = "ORIONQG_QG18_NATIVE="
QG7_DIGEST = "159d174fbb17a66aeb39a3efb53cf4c505f0a86ce8ef1dff76337d00837d152f"
POSITIVE = "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def verify_result_digest(raw: dict[str, Any]) -> bool:
    unsigned = {k: v for k, v in raw.items() if k != "result_digest"}
    return raw.get("result_digest") == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def run(analyzer_path: Path, generic_path: Path) -> dict[str, Any]:
    a = json.loads(analyzer_path.read_text())
    g = json.loads(generic_path.read_text())
    checks = {
        "analyzer_schema": a.get("schema") == "ORIONQG.QG18.TAREIntrinsicSupport.v1",
        "analyzer_digest": verify_result_digest(a),
        "analyzer_positive_terminal": a.get("terminal") == POSITIVE,
        "analyzer_all_gates": bool(a.get("gates")) and all(a.get("gates", {}).values()),
        "qg7_parent_digest": a.get("qg7_parent", {}).get("result_digest") == QG7_DIGEST,
        "qg7_selected_first_witness": a.get("qg7_parent", {}).get("selected_index") == 0,
        "r6s_universal_support2_parent": a.get("r6s_parent", {}).get("universal_support_upper_bound") == 2,
        "production_support2_cost": a.get("support2_feasible_cost") == 7,
        "production_cap1_cost": a.get("production_cap1_cost") == 8,
        "production_strict_gap": a.get("strict_gap_cap1_minus_support2") == 1,
        "support2_is_actually_used": a.get("support2_max_frame_support") == 2,
        "generic_accepts": g.get("decision") == "ACCEPT_KAPPA2" and g.get("all_checks") is True,
        "generic_bound_to_analyzer": g.get("source_result_digest") == a.get("result_digest"),
        "generic_support2_cost": g.get("independent_support2", {}).get("cost") == 7,
        "generic_cap1_cost": g.get("independent_cap1", {}).get("cost") == 8,
        "generic_conclusion": g.get("intrinsic_support_conclusion") == 2,
        "claim_is_receipt_derived": a.get("derivation_kind") == "RECEIPT_DERIVED_COROLLARY_NOT_BLIND_DISCOVERY",
        "not_phase_complete": a.get("global_phase_boundary_complete") is False,
        "authority_bounded": (
            a.get("novelty_authority") is False
            and a.get("r6_authority") is False
            and a.get("physical_quantum_advantage_claim") is False
            and g.get("novelty_authority") is False
            and g.get("physical_quantum_advantage_claim") is False
        ),
        "protected_subject_not_read": a.get("protected_subject_read") is False,
    }
    if all(checks.values()):
        decision = "ACCEPT_KAPPA2"
        responsibility = "KAPPA2_COROLLARY"
    elif not checks["generic_accepts"] or not checks["generic_bound_to_analyzer"]:
        decision = "REJECT_GENERIC_DISAGREEMENT"
        responsibility = "GENERIC_DISAGREEMENT"
    elif not checks["r6s_universal_support2_parent"]:
        decision = "REJECT_R6S_PARENT_GAP"
        responsibility = "R6S_PARENT_GAP"
    elif not checks["production_cap1_cost"] or not checks["generic_cap1_cost"]:
        decision = "REJECT_CAP1_BINDING_GAP"
        responsibility = "CAP1_BINDING_GAP"
    elif not checks["production_strict_gap"]:
        decision = "REJECT_SUPPORT2_WITNESS_GAP"
        responsibility = "SUPPORT2_WITNESS_GAP"
    else:
        decision = "CANNOT_CHECK"
        responsibility = "CANNOT_CHECK"
    return {
        "schema": "ORIONQG.QG18.NativeVerification.v1",
        "decision": decision,
        "responsibility": responsibility,
        "all_checks": all(checks.values()),
        "checks": checks,
        "source_result_digest": a.get("result_digest"),
        "generic_source_result_digest": g.get("source_result_digest"),
        "intrinsic_support_conclusion": 2 if decision == "ACCEPT_KAPPA2" else None,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer", default=str(DEFAULT_ANALYZER))
    parser.add_argument("--generic", default=str(DEFAULT_GENERIC))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.analyzer), Path(args.generic))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "decision": result["decision"],
        "responsibility": result["responsibility"],
        "all_checks": result["all_checks"],
        "intrinsic_support": result["intrinsic_support_conclusion"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
