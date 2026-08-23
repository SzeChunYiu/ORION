#!/usr/bin/env python3
"""Independent generic-harness verifier for QG-8 objective support phase theorem."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402

PROTOCOL_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG8_OBJECTIVE_SUPPORT_PHASE_PROTOCOL_V1.md"
NOVELTY_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG8_NOVELTY_THREAT_FREEZE_2026-08-21.md"
R6S_PATH = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG2_PATH = REPO_ROOT / "research" / "extensions" / "orion-qg" / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json"
DEFAULT_INPUT = REPO_ROOT / "artifacts" / "orion-qg-qg8-support-phase.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg8-generic-verification.json"
TOKEN_PREFIX = "ORIONQG_QG8_GENERIC_VERIFY="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    observed = raw.get("result_digest")
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def rebuild_domain() -> dict[str, Any]:
    h = p10.h
    lw = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
    lm = np.array([[h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
    f3 = np.zeros((4, 4, 4), dtype=np.int64)
    for a, b, c in itertools.product(range(4), repeat=3):
        f3[a, b, c] = 1 if a == b == c != 0 else lw[a] + lw[b] + lw[c]

    fi, pp, uu, vv = np.meshgrid(
        np.arange(1, 4), np.arange(4), np.arange(4), np.arange(4), indexing="ij"
    )
    old = lm[pp, fi]
    max_df3 = -10**9
    equality = None
    semantic_rows = 0
    for slot in range(3):
        if slot == 0:
            df3 = f3[pp, uu, vv] - f3[old, uu, vv]
        elif slot == 1:
            df3 = f3[uu, pp, vv] - f3[uu, old, vv]
        else:
            df3 = f3[uu, vv, pp] - f3[uu, vv, old]
        semantic_rows += int(df3.size)
        max_df3 = max(max_df3, int(df3.max()))
        if equality is None:
            rows = np.argwhere(df3 == 2)
            if rows.size:
                i0, i1, i2, i3 = (int(x) for x in rows[0])
                equality = {
                    "slot": "ABC"[slot],
                    "frame": i0 + 1,
                    "target": i1,
                    "other_slots": [i2, i3],
                    "df3": 2,
                }
    # R6S separately sweeps partner/tag letters (4*4) but they do not enter F3;
    # and two multiplier kinds. Reconstruct the declared full receipt domain.
    full_domain = semantic_rows * 16 * 2
    return {
        "semantic_rows": semantic_rows,
        "full_domain": full_domain,
        "max_df3_central": max_df3,
        "max_df3_noncentral": max_df3,
        "equality": equality,
        "central_halfspace": "t_c - 2*t_r >= 0",
        "noncentral_halfspace": "t_nc - 2*t_r >= 0",
    }


def find_support3_control(raw: Any) -> bool:
    if isinstance(raw, dict):
        if raw.get("C_DP") == 11 and raw.get("C_Dxx") == 13:
            return True
        return any(find_support3_control(value) for value in raw.values())
    if isinstance(raw, list):
        return any(find_support3_control(value) for value in raw)
    return False


def run(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    local = rebuild_domain()
    r6s = json.loads(R6S_PATH.read_text(encoding="utf-8"))
    qg2 = json.loads(QG2_PATH.read_text(encoding="utf-8"))
    analyzer_local = raw.get("local_resource_domain", {})
    analyzer_qg2 = raw.get("qg2_binding", {})

    checks = {
        "schema": raw.get("schema") == "ORION.QG.QG8.SupportPhase.v1",
        "base": raw.get("base_revision") == "318d1cbbec451170448bb8e126c7ab50801930ce",
        "protocol_hash": raw.get("protocol_sha256") == sha256_file(PROTOCOL_PATH),
        "novelty_hash": raw.get("novelty_threat_sha256") == sha256_file(NOVELTY_PATH),
        "result_digest": verify_digest(raw),
        "independent_full_domain_18432": local["full_domain"] == 18432,
        "analyzer_domain_matches": analyzer_local.get("domain_size") == local["full_domain"],
        "central_max2": local["max_df3_central"] == analyzer_local.get("max_delta_f3", {}).get("central") == 2,
        "noncentral_max2": local["max_df3_noncentral"] == analyzer_local.get("max_delta_f3", {}).get("noncentral") == 2,
        "local_equality_exists": isinstance(local["equality"], dict) and isinstance(analyzer_local.get("central_equality_witness"), dict),
        "halfspaces_exact": raw.get("support2_cone", {}).get("conditions") == ["t_c >= 2*t_r", "t_nc >= 2*t_r"],
        "r6s_hash": raw.get("r6s_binding", {}).get("receipt_sha256") == sha256_file(R6S_PATH),
        "r6s_machine_theorem": str(r6s.get("authority", "")).startswith("MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"),
        "r6s_local_bound": r6s.get("lemma_e", {}).get("domain_size") == 18432 and r6s.get("lemma_e", {}).get("max_delta_f3") == 2 and r6s.get("lemma_e", {}).get("violations") == 0,
        "r6s_zero_sum": r6s.get("lemma_b", {}).get("w3_to_w8_all_admit_subset") is True,
        "qg2_hash": analyzer_qg2.get("receipt_sha256") == sha256_file(QG2_PATH),
        "qg2_authority": qg2.get("authority") == "ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6",
        "qg2_support3_global_control": find_support3_control(qg2),
        "o0_inside": analyzer_qg2.get("objectives", {}).get("O0", {}).get("classification", {}).get("inside_support2_cone") is True,
        "o1_outside": analyzer_qg2.get("objectives", {}).get("O1", {}).get("classification", {}).get("inside_support2_cone") is False,
        "o2_inside": analyzer_qg2.get("objectives", {}).get("O2", {}).get("classification", {}).get("inside_support2_cone") is True,
        "global_sharpness_open": raw.get("support2_cone", {}).get("global_boundary_sharpness") == "OPEN",
        "no_novelty_authority": raw.get("novelty_authority") is False,
        "no_physical_advantage": raw.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    return {
        "schema": "ORION.QG.QG8.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent_resource_domain": local,
        "source_result_digest": raw.get("result_digest"),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.input))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TOKEN_PREFIX + canonical({"decision": result["decision"], "path": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
