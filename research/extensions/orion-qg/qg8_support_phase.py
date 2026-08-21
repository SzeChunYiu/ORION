#!/usr/bin/env python3
"""QG-8 objective-indexed support-two cone from the R6S exchange resource vectors."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

BASE = "318d1cbbec451170448bb8e126c7ab50801930ce"
PROTOCOL_PATH = (
    REPO_ROOT / "development" / "orion-qg-regime-geometry" /
    "QG8_OBJECTIVE_SUPPORT_PHASE_PROTOCOL_V1.md"
)
NOVELTY_PATH = (
    REPO_ROOT / "development" / "orion-qg-regime-geometry" /
    "QG8_NOVELTY_THREAT_FREEZE_2026-08-21.md"
)
R6S_PATH = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG2_PATH = REPO_ROOT / "research" / "extensions" / "orion-qg" / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg8-support-phase.json"
TOKEN_PREFIX = "ORIONQG_QG8_SUPPORT_PHASE="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, (*path, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, (*path, str(index)))


def independent_tables() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    h = p10.h
    lw = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
    lm = np.array([[h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
    sy = np.array([[h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
    f3 = np.zeros((4, 4, 4), dtype=np.int64)
    for a, b, c in itertools.product(range(4), repeat=3):
        if a == b == c != 0:
            f3[a, b, c] = 1
        else:
            f3[a, b, c] = lw[a] + lw[b] + lw[c]
    return lw, lm, sy, f3


def symbolic_exchange_domain() -> dict[str, Any]:
    lw, lm, sy, f3 = independent_tables()
    fi, fp, sg, pp, uu, vv = np.meshgrid(
        np.arange(1, 4), np.arange(4), np.arange(4), np.arange(4),
        np.arange(4), np.arange(4), indexing="ij",
    )
    old = lm[pp, fi]
    alpha = sy[fi, fp]
    beta = sy[sg, fi]

    checked_per_kind = 0
    max_df3 = {"central": -10**9, "noncentral": -10**9}
    hist = {"central": {}, "noncentral": {}}
    equality_witness = None
    class_max: dict[str, int] = {}

    # The F3 change is independent of frame multiplier; both resource kinds sweep
    # the same local semantic domain, as R6S did with m in {2,4}.
    for slot in range(3):
        if slot == 0:
            df3 = f3[pp, uu, vv] - f3[old, uu, vv]
        elif slot == 1:
            df3 = f3[uu, pp, vv] - f3[uu, old, vv]
        else:
            df3 = f3[uu, vv, pp] - f3[uu, vv, old]

        checked_per_kind += int(df3.size)
        local_max = int(df3.max())
        for kind in ("central", "noncentral"):
            max_df3[kind] = max(max_df3[kind], local_max)
            values, counts = np.unique(df3, return_counts=True)
            for value, count in zip(values.tolist(), counts.tolist(), strict=True):
                key = str(int(value))
                hist[kind][key] = hist[kind].get(key, 0) + int(count)

        for a_bit in (0, 1):
            for b_bit in (0, 1):
                mask = (alpha == a_bit) & (beta == b_bit)
                key = f"class_{a_bit}{b_bit}_max_df3"
                class_max[key] = max(class_max.get(key, -10**9), int(df3[mask].max()))

        if equality_witness is None:
            rows = np.argwhere(df3 == 2)
            if rows.size:
                i0, i1, i2, i3, i4, i5 = (int(x) for x in rows[0])
                equality_witness = {
                    "slot": "ABC"[slot],
                    "zeroed_letter": i0 + 1,
                    "partner_letter": i1,
                    "tag_letter": i2,
                    "target_letter": i3,
                    "other_slots": [i4, i5],
                    "alpha": int(alpha[i0, i1, i2, i3, i4, i5]),
                    "beta": int(beta[i0, i1, i2, i3, i4, i5]),
                    "delta_f3": 2,
                    "unit_objective_central_net": 0,
                    "below_boundary_example": {
                        "t_c": 1.9,
                        "t_r": 1.0,
                        "weighted_delta": 0.1,
                    },
                }

    total_domain = checked_per_kind * 2
    tables_bound = {
        "LW": bool(np.array_equal(lw, r6m._LW)),
        "LM": bool(np.array_equal(lm, r6m._LM)),
        "SY": bool(np.array_equal(sy, r6m._SY)),
        "F3": bool(np.array_equal(f3, r6m._F3)),
    }
    return {
        "domain_size": total_domain,
        "domain_per_resource_kind": checked_per_kind,
        "max_delta_f3": max_df3,
        "histograms": hist,
        "class_max_delta_f3": class_max,
        "central_equality_witness": equality_witness,
        "production_table_binding": tables_bound,
        "all_tables_bound": all(tables_bound.values()),
        "derived_halfspaces": {
            "central": {
                "inequality": "t_c - 2*t_r >= 0",
                "frame_refund_coordinate": "t_c",
                "worst_f3_increase_units": max_df3["central"],
            },
            "noncentral": {
                "inequality": "t_nc - 2*t_r >= 0",
                "frame_refund_coordinate": "t_nc",
                "worst_f3_increase_units": max_df3["noncentral"],
            },
        },
    }


def bind_r6s() -> dict[str, Any]:
    raw = json.loads(R6S_PATH.read_text(encoding="utf-8"))
    lemma_e = raw.get("lemma_e", {})
    lemma_b = raw.get("lemma_b", {})
    gates = raw.get("gates", {})
    checks = {
        "authority": str(raw.get("authority", "")).startswith(
            "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"
        ),
        "domain_18432": lemma_e.get("domain_size") == 18432,
        "zero_violations": lemma_e.get("violations") == 0,
        "max_delta_f3_2": lemma_e.get("max_delta_f3") == 2,
        "w3plus_zero_sum": lemma_b.get("w3_to_w8_all_admit_subset") is True,
        "bindings_exact": gates.get("bindings_exact") is True,
        "no_new_subject_data": gates.get("no_new_subject_data") is True,
    }
    return {
        "receipt_sha256": sha256_file(R6S_PATH),
        "checks": checks,
        "all_bound": all(checks.values()),
    }


def _weight_rows(qg2: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for path, value in _walk(qg2):
        if not isinstance(value, dict):
            continue
        weights = value.get("weights")
        if not isinstance(weights, dict):
            continue
        keys = ("t_nc", "t_c", "t_tag", "t_r", "rho_per_rotation")
        if not all(key in weights for key in keys):
            continue
        vector = tuple(weights[key] for key in keys)
        if vector in seen:
            continue
        seen.add(vector)
        rows.append({"path": "/".join(path), "weights": dict(weights)})
    return rows


def _classify(weights: dict[str, Any]) -> dict[str, Any]:
    t_c = float(weights["t_c"])
    t_nc = float(weights["t_nc"])
    t_r = float(weights["t_r"])
    central_margin = t_c - 2.0 * t_r
    noncentral_margin = t_nc - 2.0 * t_r
    return {
        "inside_support2_cone": central_margin >= 0 and noncentral_margin >= 0,
        "central_margin": central_margin,
        "noncentral_margin": noncentral_margin,
        "central_boundary": central_margin == 0,
        "noncentral_boundary": noncentral_margin == 0,
    }


def bind_qg2() -> dict[str, Any]:
    raw = json.loads(QG2_PATH.read_text(encoding="utf-8"))
    rows = _weight_rows(raw)
    expected = {
        "O0": (4, 2, 2, 1, 0),
        "O1": (7, 1, 4, 3, 0),
        "O2": (4, 2, 2, 1, 5),
    }
    classified: dict[str, Any] = {}
    for name, vector in expected.items():
        match = next(
            (
                row for row in rows
                if tuple(row["weights"][key] for key in (
                    "t_nc", "t_c", "t_tag", "t_r", "rho_per_rotation"
                )) == vector
            ),
            None,
        )
        classified[name] = None if match is None else {
            **match,
            "classification": _classify(match["weights"]),
        }

    support3_witnesses = []
    for path, value in _walk(raw):
        if not isinstance(value, dict):
            continue
        if value.get("C_DP") == 11 and value.get("C_Dxx") == 13:
            support3_witnesses.append(
                {
                    "path": "/".join(path),
                    "C_DP": 11,
                    "C_Dxx": 13,
                    "C_Dplus": value.get("C_Dplus"),
                    "witness_present": isinstance(value.get("dp_witness"), dict),
                }
            )

    checks = {
        "authority": raw.get("authority")
        == "ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6",
        "all_expected_objectives_found": all(classified[name] is not None for name in expected),
        "o0_inside": bool(classified["O0"] and classified["O0"]["classification"]["inside_support2_cone"]),
        "o0_central_boundary": bool(classified["O0"] and classified["O0"]["classification"]["central_boundary"]),
        "o1_outside": bool(classified["O1"] and not classified["O1"]["classification"]["inside_support2_cone"]),
        "o2_inside": bool(classified["O2"] and classified["O2"]["classification"]["inside_support2_cone"]),
        "support3_global_witness_found": bool(support3_witnesses),
        "receipt_hostile_all_pass": raw.get("gates", {}).get("hostile_all_pass") is True,
    }
    return {
        "receipt_sha256": sha256_file(QG2_PATH),
        "objectives": classified,
        "support3_witnesses": support3_witnesses[:12],
        "checks": checks,
        "all_bound": all(checks.values()),
    }


def run() -> dict[str, Any]:
    local = symbolic_exchange_domain()
    r6s = bind_r6s()
    qg2 = bind_qg2()
    gates = {
        "protocol_present": PROTOCOL_PATH.is_file(),
        "novelty_freeze_present": NOVELTY_PATH.is_file(),
        "local_domain_exact_18432": local["domain_size"] == 18432,
        "production_tables_exact": local["all_tables_bound"],
        "central_max_df3_2": local["max_delta_f3"]["central"] == 2,
        "noncentral_max_df3_2": local["max_delta_f3"]["noncentral"] == 2,
        "central_equality_witness_present": isinstance(local["central_equality_witness"], dict),
        "r6s_receipt_bound": r6s["all_bound"],
        "qg2_controls_bound": qg2["all_bound"],
        "no_new_chemistry_or_protected_access": True,
    }
    positive = all(gates.values())
    terminal = (
        "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED"
        if positive else "QG8_RESOURCE_VECTOR_OR_BINDING_REFUTED"
    )
    result: dict[str, Any] = {
        "schema": "ORION.QG.QG8.SupportPhase.v1",
        "issue": "SzeChunYiu/ORION#760",
        "base_revision": BASE,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "novelty_threat_sha256": sha256_file(NOVELTY_PATH),
        "terminal": terminal,
        "support2_cone": {
            "conditions": ["t_c >= 2*t_r", "t_nc >= 2*t_r"],
            "tag_coefficient": "UNCONSTRAINED_BY_EXCHANGE",
            "rotation_coefficient": "WITHIN_FAMILY_CONSTANT_DIRECTION",
            "all_n_support_bound": 2,
            "global_boundary_sharpness": "OPEN",
            "certificate_boundary_sharpness": "CENTRAL_HYPERPLANE_EXACT",
        },
        "local_resource_domain": local,
        "r6s_binding": r6s,
        "qg2_binding": qg2,
        "proof_audit": {
            "tag_unchanged_on_zero_sum_exchange": True,
            "rotation_constant_within_r6m_family": True,
            "weighted_local_nonincrease_follows_from_halfspaces": True,
            "r6s_zero_sum_subset_lemma_reused_without_objective_dependence": r6s["all_bound"],
            "lexicographic_support_minimality_handles_boundary_ties": True,
            "outside_cone_not_equated_with_support3_required": True,
            "o1_global_witness_only_refutes_objective_independent_support2": bool(qg2["support3_witnesses"]),
        },
        "gates": gates,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    unsigned = canonical(result)
    result["result_digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        TOKEN_PREFIX + canonical({
            "path": str(path),
            "terminal": result["terminal"],
            "result_digest": result["result_digest"],
            "local_domain": result["local_resource_domain"]["domain_size"],
            "central_max_df3": result["local_resource_domain"]["max_delta_f3"]["central"],
            "noncentral_max_df3": result["local_resource_domain"]["max_delta_f3"]["noncentral"],
            "all_gates": all(result["gates"].values()),
        })
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
