#!/usr/bin/env python3
"""Native ORION-Q authority gate for QG-7d J7 PA all-n closure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "artifacts/orion-qg-qg7d-j7-pa-confirm.json"
GENERIC = ROOT / "artifacts/orion-qg-qg7d-j7-pa-generic-verification.json"
PARENT = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG7D_J7_PA_CONFIRMATORY_PROTOCOL_V1.md"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg7d-j7-pa-native-verification.json"
TOKEN = "ORIONQG_QG7D_J7_NATIVE="
PARENT_DIGEST = "0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
POSITIVE = "QG7D_PA_PINNED_COMM_S2_CLOSED_ALL_N_MACHINE_CHECKED__PP_CHAIN_OPEN"


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = {k: v for k, v in raw.items() if k != "result_digest"}
    return raw.get("result_digest") == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyzer", type=Path, default=ANALYZER)
    ap.add_argument("--generic", type=Path, default=GENERIC)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    a = json.loads(args.analyzer.read_text())
    g = json.loads(args.generic.read_text())
    p = json.loads(PARENT.read_text())

    checks = {
        "analyzer_schema": a.get("schema") == "ORIONQG.QG7D.J7PAConfirmatory.v1",
        "analyzer_digest": verify_digest(a),
        "analyzer_positive": a.get("terminal") == POSITIVE and a.get("all_gates") is True,
        "generic_accept": g.get("decision") == "ACCEPT_PA_ALL_N_CLOSURE" and g.get("all_checks") is True,
        "generic_bound": g.get("source_result_digest") == a.get("result_digest"),
        "protocol_bound": a.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "parent_bound": p.get("result_digest") == PARENT_DIGEST == a.get("parent_qg7c_digest"),
        "parent_pa_complete": a.get("parent", {}).get("pa_failures") == 103048 == g.get("parent_failures"),
        "parent_histogram": a.get("parent", {}).get("delta_histogram") == {"1": 100672, "2": 2376} == g.get("parent_delta_histogram"),
        "j6_fingerprint": a.get("j6", {}).get("residual_count") == 42 == g.get("j6_residuals"),
        "j7_zero": a.get("j7_bprime", {}).get("final_residuals") == 0 == g.get("j7_final_residuals"),
        "bprime_all_verified": a.get("j7_bprime", {}).get("witness_verification_failures") == [],
        "bprime_histogram": a.get("j7_bprime", {}).get("delta_histogram") == {"-1": 6, "0": 36} == g.get("bprime_delta_histogram"),
        "pa_authority_true": a.get("PA_ALL_N") is True and g.get("PA_ALL_N") is True,
        "pp_authority_false": a.get("PP_ALL_N") is False and g.get("PP_ALL_N") is False,
        "chain_authority_false": a.get("CHAIN_ALL_N") is False and g.get("CHAIN_ALL_N") is False,
        "global_completeness_false": a.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False and g.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False,
        "authority_bounded": a.get("novelty_authority") is False and a.get("r6_authority") is False and a.get("physical_quantum_advantage_claim") is False and g.get("novelty_authority") is False,
        "protected_subject_not_read": a.get("protected_subject_read") is False,
    }
    if all(checks.values()):
        decision = "ACCEPT_PA_ALL_N_CLOSURE"
        responsibility = "PA_PINNED_COMM_S2_NORMALIZATION"
    elif not checks["generic_accept"] or not checks["generic_bound"]:
        decision = "REJECT_GENERIC_DISAGREEMENT"
        responsibility = "GENERIC_DISAGREEMENT"
    elif not checks["parent_bound"] or not checks["protocol_bound"]:
        decision = "REJECT_PARENT_BINDING"
        responsibility = "PARENT_BINDING_GAP"
    elif not checks["pp_authority_false"] or not checks["chain_authority_false"] or not checks["global_completeness_false"]:
        decision = "REJECT_AUTHORITY_LAUNDERING"
        responsibility = "GLOBAL_COMPLETENESS_BLOCKED"
    else:
        decision = "CANNOT_CHECK"
        responsibility = "CANNOT_CHECK"

    out = {
        "schema": "ORIONQG.QG7D.J7PANativeVerification.v1",
        "issue": "SzeChunYiu/ORION#836",
        "decision": decision,
        "responsibility": responsibility,
        "all_checks": all(checks.values()),
        "checks": checks,
        "source_result_digest": a.get("result_digest"),
        "PA_ALL_N": decision == "ACCEPT_PA_ALL_N_CLOSURE",
        "PP_ALL_N": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "decision": decision, "responsibility": responsibility,
        "all_checks": out["all_checks"], "PA_ALL_N": out["PA_ALL_N"],
        "PP_ALL_N": False, "CHAIN_ALL_N": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
