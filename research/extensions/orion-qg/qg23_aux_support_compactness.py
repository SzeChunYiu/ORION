#!/usr/bin/env python3
"""QG-23 production analyzer: all-n auxiliary-support compactness for three-block TARE."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QG7C = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
QG7F = ROOT / "research/extensions/orion-qg/QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json"
PROTO = ROOT / "development/orion-qg-regime-geometry/QG23_TARE_AUX_SUPPORT_COMPACTNESS_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg23-aux-support-compactness.json"
TOKEN = "ORIONQG_QG23="
POS = "QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def shape_lattice():
    rows = []
    for a in range(4):
        for p in range(4 - a):
            c = 3 - a - p
            rows.append({
                "anchored": a,
                "phantom": p,
                "comm_s2": c,
                "tag_support_bound": 3 + c,
                "phantom_off_tag_home_bound": p,
                "aux_support_bound": 3 + c + p,
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    x = ap.parse_args()

    q7c = json.loads(QG7C.read_text())
    q7f = json.loads(QG7F.read_text())
    m1 = q7c.get("m1_inventory", {})
    t2 = q7c.get("t2_occupancy", {})
    shapes = m1.get("irreducible_shape_counts", {})
    cyc = q7c.get("obligations", {}).get("L4b_shape_classes", {}).get("cyclic_borrow", {})
    proto7c = ROOT / "development/orion-qg-regime-geometry/QG7C_CLASSIFICATION_PROTOCOL_V1.md"
    proto7c_text = proto7c.read_text()

    expected_shapes = {"anchored", "phantom", "comm_s2"}
    per_shape = t2.get("per_shape_anticommuting_tag_qubits", {})
    cor = str(t2.get("corollary", ""))
    mechanism = str(cyc.get("mechanism", ""))

    parent_checks = {
        "qg7c_protocol_bound": q7c.get("protocol") == "QG7C_CLASSIFICATION_PROTOCOL_V1" and q7c.get("protocol_sha256") == sha_file(proto7c),
        "m1_holds": m1.get("holds") is True,
        "m1_exact_three_shapes": set(shapes) == expected_shapes and all(int(shapes[k]) > 0 for k in expected_shapes) and m1.get("unclassified_irreducible") == 0,
        "t2_holds": t2.get("holds") is True and t2.get("occupancy_failures_from_m1") == 0,
        "per_shape_occupancy": per_shape == {"anchored": 1, "comm_s2": 2, "phantom": 1},
        "tag_bound_text_bound": "wt(s) <= 3 + #comm-s2" in cor,
        "phantom_home_tag_off_receipt": "every home carries none" in mechanism and "every irreducible borrow qubit carries a tag letter" in mechanism,
        "cyclic_borrow_closed_all_n": cyc.get("status") == "CLOSED_ALL_N",
        "shape_definitions_exact": all(s in proto7c_text for s in (
            "**anchored**: both frames weight-1 on one common qubit q",
            "**phantom**: anti frame support-2 on {b,h}",
            "σ_h = 0 (home OFF the tag)",
            "**comm-s2**: comm frame support-2 on {b,a}",
        )),
    }

    hostile_checks = {
        "terminal": q7f.get("terminal") == "QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION",
        "both_accept": q7f.get("both_accept") is True,
        "tag3": q7f.get("frozen_candidate", {}).get("tag_weight") == 3,
        "overlapping_distinct_pairs": q7f.get("frozen_candidate", {}).get("B_comm_s2_support") == [0, 1] and q7f.get("frozen_candidate", {}).get("C_comm_s2_support") == [1, 2],
        "representation_not_complete": q7f.get("CHAIN_REPRESENTATION_COMPLETE") is False,
    }

    rows = shape_lattice()
    max_aux = max(r["aux_support_bound"] for r in rows)
    max_rows = [r for r in rows if r["aux_support_bound"] == max_aux]
    lattice_checks = {
        "ten_shape_count_triples": len(rows) == 10 and len({(r["anchored"], r["phantom"], r["comm_s2"]) for r in rows}) == 10,
        "all_sum_to_three": all(r["anchored"] + r["phantom"] + r["comm_s2"] == 3 for r in rows),
        "formula_exact": all(r["aux_support_bound"] == 6 - r["anchored"] == r["tag_support_bound"] + r["phantom_off_tag_home_bound"] for r in rows),
        "maximum_exactly_six": max_aux == 6,
        "max_exactly_a0": all(r["anchored"] == 0 for r in max_rows) and {r["anchored"] for r in rows if r["aux_support_bound"] == 6} == {0},
        "c_ge_2_implies_p_le_1": all(r["phantom"] <= 1 for r in rows if r["comm_s2"] >= 2),
    }

    parent_ok = all(parent_checks.values())
    hostile_ok = all(hostile_checks.values())
    lattice_ok = all(lattice_checks.values())
    if not parent_ok:
        terminal = "QG23_PARENT_OCCUPANCY_AUTHORITY_GAP"
    elif not hostile_ok:
        terminal = "QG23_HOSTILE_CORRECTION_BINDING_GAP"
    elif not lattice_ok:
        terminal = "QG23_CANNOT_CHECK"
    else:
        terminal = POS

    out = {
        "schema": "ORIONQG.QG23.AuxSupportCompactness.v1",
        "issue": "SzeChunYiu/ORION#879",
        "terminal": terminal,
        "protocol_sha256": sha_file(PROTO),
        "qg7c_result_sha256": sha_file(QG7C),
        "qg7f_result_sha256": sha_file(QG7F),
        "parent_checks": parent_checks,
        "hostile_correction_checks": hostile_checks,
        "shape_count_lattice": rows,
        "lattice_checks": lattice_checks,
        "maximum_auxiliary_support": max_aux,
        "maximizing_shape_counts": max_rows,
        "theorem_statement": "For every irreducible three-block TARE auxiliary configuration after the earned QG-7c reductions, |supp(Tag) union phantom-homes| <= 6, independently of physical n.",
        "proof_identity": "|U_aux| <= wt(S)+p <= 3+c+p = 6-a <= 6, for a+p+c=3",
        "physical_n_in_bound": False,
        "overlapping_comm_s2_pairs_allowed": True,
        "phantom_home_count_is_union_upper_bound": True,
        "target_spectator_state": "OPEN_AND_NOT_BOUNDED_BY_6",
        "auxiliary_support_compactness_authority": terminal == POS,
        "FULL_STATE_DIMENSION_6": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "FIFTH_REGIME_FOUND": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    raw = canon(out)
    out["result_digest"] = hashlib.sha256(raw.encode()).hexdigest()
    x.output.parent.mkdir(parents=True, exist_ok=True)
    x.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({
        "terminal": terminal,
        "max_auxiliary_support": max_aux,
        "shape_rows": len(rows),
        "parent_ok": parent_ok,
        "hostile_ok": hostile_ok,
        "lattice_ok": lattice_ok,
        "result_digest": out["result_digest"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
