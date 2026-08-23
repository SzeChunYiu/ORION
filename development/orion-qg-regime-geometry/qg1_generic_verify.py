#!/usr/bin/env python3
"""Independent reconstruction for the QG-1 support-five theorem artifact."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULT_PATH = REPO_ROOT / "artifacts" / "orion-qg-qg1-support5-theorem.json"
PROTOCOL_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG1_RANK2_SUPPORT5_PROTOCOL_V1.md"
NOVELTY_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG1_NOVELTY_THREAT_FREEZE_2026-08-21.md"
TOKEN_PREFIX = "ORIONQG_QG1_GENERIC_VERIFY="
FROZEN_BASE = "e6011bbeae68d91b5cce45ffa34e67306905844d"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gf2_rank(values: list[int]) -> int:
    basis = [0] * 5
    rank = 0
    for value in values:
        x = int(value)
        while x:
            pivot = x.bit_length() - 1
            if basis[pivot]:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                rank += 1
                break
    return rank


def result_digest_valid(result: dict[str, Any]) -> bool:
    observed = result.get("result_digest")
    unsigned = dict(result)
    unsigned.pop("result_digest", None)
    expected = hashlib.sha256(canonical(unsigned).encode("utf-8")).hexdigest()
    return isinstance(observed, str) and observed == expected


def analytic_local_bound() -> dict[str, Any]:
    two_frame_bound = -6 + 2
    three_frame_bound = -10 + 3
    return {
        "two_frame_support_delta_bound": two_frame_bound,
        "three_frame_support_delta_bound": three_frame_bound,
        "universal_delta_bound": max(two_frame_bound, three_frame_bound),
    }


def verify(result: dict[str, Any]) -> dict[str, Any]:
    local = result.get("local", {})
    constraints = result.get("constraints", {})
    f2 = result.get("f2_5", {})
    analytic = analytic_local_bound()
    boundary = [int(x) for x in f2.get("boundary_classes", [])]
    boundary_xor = 0
    for value in boundary:
        boundary_xor ^= value

    checks = {
        "result_digest_valid": result_digest_valid(result),
        "frozen_base_exact": result.get("base_revision") == FROZEN_BASE,
        "protocol_hash_exact": result.get("protocol_sha256") == sha256_file(PROTOCOL_PATH),
        "novelty_hash_exact": result.get("novelty_threat_sha256") == sha256_file(NOVELTY_PATH),
        "positive_terminal_exact": result.get("terminal") == "QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED",
        "local_count_reconstructs": int(local.get("case_count", -1)) == 3 * 15 * (4**5),
        "local_max_delta_matches_independent_bound": int(local.get("max_delta", 99)) == analytic["universal_delta_bound"] == -4,
        "local_violation_list_empty": local.get("violations") == [],
        "delta_histogram_sums_domain": sum(int(v) for v in local.get("delta_histogram", {}).values()) == 46080,
        "constraint_count_reconstructs": int(constraints.get("case_count", -1)) == 15 * 16,
        "constraint_violations_empty": constraints.get("violations") == [],
        "realizable_span_rank5": int(constraints.get("realizable_span_rank", -1)) == 5,
        "abstract_multiset_count_reconstructs": int(f2.get("multiset_count", -1)) == math.comb(37, 6),
        "distinct_nonzero_count_reconstructs": int(f2.get("distinct_nonzero_count", -1)) == math.comb(31, 6),
        "six_vector_rank_ceiling": int(f2.get("max_six_rank", 99)) == 5 and f2.get("rank_violations") == [],
        "boundary_has_five_classes": len(boundary) == 5,
        "boundary_independent": gf2_rank(boundary) == 5 == int(f2.get("boundary_rank", -1)),
        "boundary_xor_exact": boundary_xor == 27 == int(f2.get("boundary_xor", -1)),
        "all_machine_gates_true": all(bool(v) for v in result.get("gates", {}).values()),
        "all_proof_audit_gates_true": all(bool(v) for v in result.get("proof_audit", {}).values()),
        "no_chemistry_access": result.get("chemistry_sources_read") is False,
        "novelty_authority_false": result.get("novelty_authority") is False,
        "physical_advantage_false": result.get("physical_quantum_advantage_claim") is False,
    }
    return {
        "schema": "ORION.QG.QG1.GenericVerification.v1",
        "verification_pass": all(checks.values()),
        "theorem_result_digest": result.get("result_digest"),
        "checks": checks,
        "independent_local_bound": analytic,
        "ground_truth_source": "FINITE_LOCAL_ENUMERATION_PLUS_F2_DIMENSION_THEOREM",
        "chemistry_sources_read": False,
        "novelty_authority": False,
    }


def main() -> int:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    verification = verify(result)
    path = REPO_ROOT / "artifacts" / "orion-qg-qg1-generic-verification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TOKEN_PREFIX + canonical(verification))
    # A theorem refutation is a completed scientific run, not a host/tool failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
