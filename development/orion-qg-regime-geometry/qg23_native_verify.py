#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for QG-23 auxiliary-support compactness."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "artifacts/orion-qg-qg23-aux-support-compactness.json"
G = ROOT / "artifacts/orion-qg-qg23-generic-verification.json"
PROTO = ROOT / "development/orion-qg-regime-geometry/QG23_TARE_AUX_SUPPORT_COMPACTNESS_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg23-native-verification.json"
TOKEN = "ORIONQG_QG23_NATIVE="
POS = "QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid_digest(r):
    u = {k: v for k, v in r.items() if k != "result_digest"}
    return r.get("result_digest") == hashlib.sha256(canon(u).encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyzer", type=Path, default=A)
    ap.add_argument("--generic", type=Path, default=G)
    ap.add_argument("--output", type=Path, default=OUT)
    x = ap.parse_args()
    a = json.loads(x.analyzer.read_text())
    g = json.loads(x.generic.read_text())

    scope_false = ("FULL_STATE_DIMENSION_6", "CHAIN_ALL_N", "GLOBAL_BDOUBLEPRIME_COMPLETENESS", "FIFTH_REGIME_FOUND")
    checks = {
        "analyzer_positive": a.get("terminal") == POS and a.get("auxiliary_support_compactness_authority") is True and valid_digest(a),
        "generic_positive": g.get("decision") == "ACCEPT_AUXILIARY_SUPPORT_COMPACTNESS" and g.get("all_checks") is True,
        "digest_bound": g.get("source_result_digest") == a.get("result_digest"),
        "protocol_bound": a.get("protocol_sha256") == hashlib.sha256(PROTO.read_bytes()).hexdigest(),
        "six_is_auxiliary_only": a.get("maximum_auxiliary_support") == 6 and a.get("target_spectator_state") == "OPEN_AND_NOT_BOUNDED_BY_6",
        "hostile_correction_preserved": a.get("overlapping_comm_s2_pairs_allowed") is True and a.get("hostile_correction_checks", {}).get("overlapping_distinct_pairs") is True,
        "stronger_authority_false_analyzer": all(a.get(k) is False for k in scope_false),
        "stronger_authority_false_generic": all(g.get(k) is False for k in scope_false),
        "no_novelty_or_physical_authority": all(a.get(k) is False for k in ("novelty_authority", "r6_authority", "physical_quantum_advantage_claim")) and all(g.get(k) is False for k in ("novelty_authority", "r6_authority", "physical_quantum_advantage_claim")),
    }
    ok = all(checks.values())
    out = {
        "schema": "ORIONQG.QG23.NativeVerification.v1",
        "decision": "ACCEPT_AUXILIARY_SUPPORT_COMPACTNESS" if ok else "REJECT",
        "responsibility": "AUXILIARY_SUPPORT_COMPACTNESS" if ok else "CANNOT_CHECK",
        "all_checks": bool(ok),
        "checks": checks,
        "source_result_digest": a.get("result_digest"),
        "AUXILIARY_SUPPORT_COMPACTNESS": bool(ok),
        "maximum_auxiliary_support": 6 if ok else None,
        "FULL_STATE_DIMENSION_6": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "FIFTH_REGIME_FOUND": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    x.output.parent.mkdir(parents=True, exist_ok=True)
    x.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"decision": out["decision"], "responsibility": out["responsibility"], "max_auxiliary_support": out["maximum_auxiliary_support"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
